#!/usr/bin/env python3
import sys
import csv
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QTextEdit, QTabWidget,
    QFileDialog, QFrame, QHeaderView, QStatusBar, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette
import pymysql

from app.logger import log_info, log_error
from app.config import load_config, save_config
from app.validators import validate_host, validate_port, validate_user, validate_sql, validate_json
from app.styles import DARK_THEME
from app.dialogs import show_info, show_success, show_warning, show_error


class LoginWidget(QWidget):
    def __init__(self, on_connect):
        super().__init__()
        self.on_connect = on_connect
        self.config = load_config()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 登录卡片
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(400, 560)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(0)

        # Logo 图标
        icon_label = QLabel("⬡")
        icon_label.setStyleSheet("font-size: 42px; color: #8b5cf6;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        card_layout.addSpacing(12)

        # 标题
        title = QLabel("SQL Manager")
        title.setObjectName("logoLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("连接您的数据库")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(28)

        # 输入字段
        fields = [
            ("主机", self.config.get("host", "localhost"), False),
            ("端口", str(self.config.get("port", 3306)), False),
            ("用户名", self.config.get("user", "root"), False),
            ("密码", self.config.get("password", ""), True),
        ]

        self.inputs = {}
        for label_text, default, is_password in fields:
            label = QLabel(label_text)
            label.setObjectName("inputLabel")
            card_layout.addWidget(label)
            card_layout.addSpacing(4)

            input_field = QLineEdit(default)
            input_field.setFixedHeight(42)
            if is_password:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
            card_layout.addWidget(input_field)
            card_layout.addSpacing(12)
            self.inputs[label_text] = input_field

        card_layout.addSpacing(12)

        # 连接按钮
        btn = QPushButton("连接")
        btn.setFixedHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.connect)
        card_layout.addWidget(btn)

        layout.addWidget(card)
        self.setLayout(layout)

    def connect(self):
        host = self.inputs["主机"].text()
        port = self.inputs["端口"].text()
        user = self.inputs["用户名"].text()
        password = self.inputs["密码"].text()

        for validator, value in [(validate_host, host), (validate_port, port), (validate_user, user)]:
            ok, msg = validator(value)
            if not ok:
                show_warning(self, "验证失败", msg)
                return

        try:
            log_info(f"连接: {host}:{port}")
            conn = pymysql.connect(
                host=host.strip(), port=int(port), user=user.strip(),
                password=password, cursorclass=pymysql.cursors.DictCursor
            )
            log_info("连接成功")
            save_config({"host": host.strip(), "port": int(port), "user": user.strip(), "password": password})
            self.on_connect(conn)
        except Exception as e:
            log_error(f"连接失败: {e}")
            show_error(self, "连接失败", str(e))


class ManagerWidget(QWidget):
    def __init__(self, conn, on_disconnect):
        super().__init__()
        self.conn = conn
        self.on_disconnect = on_disconnect
        self.current_db = None
        self.current_table = None
        self.conn_params = None  # 保存连接参数用于重连
        self.init_ui()
        self.load_databases()

    def ensure_connection(self):
        """确保数据库连接有效，必要时重连"""
        try:
            self.conn.ping(reconnect=True)
            return True
        except Exception as e:
            log_error(f"连接检查失败: {e}")
            return False

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 侧边栏
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 24, 20, 20)
        sidebar_layout.setSpacing(20)

        # Logo
        logo_row = QHBoxLayout()
        logo_icon = QLabel("⬡")
        logo_icon.setStyleSheet("font-size: 24px; color: #8b5cf6;")
        logo_text = QLabel("SQL Manager")
        logo_text.setObjectName("logoLabel")
        logo_text.setStyleSheet("font-size: 16px;")
        logo_row.addWidget(logo_icon)
        logo_row.addWidget(logo_text)
        logo_row.addStretch()
        sidebar_layout.addLayout(logo_row)

        # 数据库指示器
        self.db_indicator = QLabel("选择数据库开始")
        self.db_indicator.setObjectName("dbIndicator")
        self.db_indicator.setWordWrap(True)
        sidebar_layout.addWidget(self.db_indicator)

        # 分隔
        section = QLabel("数据库列表")
        section.setObjectName("sectionLabel")
        sidebar_layout.addWidget(section)

        # 树形列表
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(0)  # 无缩进
        self.tree.setAnimated(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QTreeWidget::branch {
                background: transparent;
                border: none;
                image: none;
                width: 0px;
            }
            QTreeWidget::item {
                background-color: transparent;
                padding: 8px 12px;
                margin: 2px 4px;
                border-radius: 6px;
                color: #a1a1aa;
            }
            QTreeWidget::item:hover {
                background-color: #27272a;
                color: #e4e4e7;
            }
            QTreeWidget::item:selected {
                background-color: #8b5cf6;
                color: white;
            }
        """)
        self.tree.itemClicked.connect(self.on_tree_click)
        self.tree.itemExpanded.connect(self.on_tree_expand)
        sidebar_layout.addWidget(self.tree, 1)

        # 断开按钮
        disconnect_btn = QPushButton("断开连接")
        disconnect_btn.setObjectName("dangerBtn")
        disconnect_btn.setFixedHeight(44)
        disconnect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        disconnect_btn.clicked.connect(self.disconnect)
        sidebar_layout.addWidget(disconnect_btn)

        layout.addWidget(sidebar)

        # 主内容区
        main = QFrame()
        main.setObjectName("mainContent")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(24)

        # 标签页
        self.tabs = QTabWidget()

        # 表结构
        struct_widget = QWidget()
        struct_layout = QVBoxLayout(struct_widget)
        struct_layout.setContentsMargins(0, 0, 0, 0)
        self.structure_table = QTableWidget()
        self.structure_table.setColumnCount(5)
        self.structure_table.setHorizontalHeaderLabels(["字段", "类型", "可空", "键", "默认值"])
        self.structure_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.structure_table.setAlternatingRowColors(True)
        self.structure_table.verticalHeader().setVisible(False)
        self.structure_table.setShowGrid(False)
        self.structure_table.setStyleSheet("""
            QTableWidget {
                background-color: #18181b;
                alternate-background-color: #1f1f23;
                border: 1px solid #27272a;
                border-radius: 8px;
                gridline-color: #27272a;
            }
            QTableWidget::item {
                padding: 10px 14px;
                color: #e4e4e7;
                background-color: #18181b;
            }
            QTableWidget::item:alternate {
                background-color: #1f1f23;
            }
            QTableWidget::item:selected {
                background-color: #7c3aed;
                color: white;
            }
            QHeaderView::section {
                background-color: #27272a;
                color: #a1a1aa;
                padding: 12px 14px;
                border: none;
                font-weight: 600;
            }
        """)
        struct_layout.addWidget(self.structure_table)
        self.tabs.addTab(struct_widget, "  结构  ")

        # SQL 查询
        query_widget = QWidget()
        query_layout = QVBoxLayout(query_widget)
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_layout.setSpacing(16)

        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText("输入 SQL 查询语句...\n\n例如:\nSELECT * FROM users;\nSELECT name, price FROM products WHERE stock > 50;")
        self.sql_input.setFixedHeight(160)
        query_layout.addWidget(self.sql_input)

        btn_row = QHBoxLayout()
        exec_btn = QPushButton("执行查询")
        exec_btn.setFixedSize(140, 44)
        exec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exec_btn.clicked.connect(self.execute_query)
        btn_row.addWidget(exec_btn)
        btn_row.addStretch()
        query_layout.addLayout(btn_row)

        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setShowGrid(False)
        self.result_table.setStyleSheet("""
            QTableWidget {
                background-color: #18181b;
                alternate-background-color: #1f1f23;
                border: 1px solid #27272a;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 10px 14px;
                color: #e4e4e7;
                background-color: #18181b;
            }
            QTableWidget::item:alternate {
                background-color: #1f1f23;
            }
            QTableWidget::item:selected {
                background-color: #7c3aed;
                color: white;
            }
            QHeaderView::section {
                background-color: #27272a;
                color: #a1a1aa;
                padding: 12px 14px;
                border: none;
                font-weight: 600;
            }
        """)
        query_layout.addWidget(self.result_table, 1)

        self.tabs.addTab(query_widget, "  查询  ")

        # 导入
        import_widget = QWidget()
        import_layout = QVBoxLayout(import_widget)
        import_layout.setContentsMargins(0, 0, 0, 0)
        import_layout.setSpacing(16)

        self.import_target = QLabel("请先选择目标表")
        self.import_target.setObjectName("targetLabel")
        import_layout.addWidget(self.import_target)

        hint = QLabel("JSON 格式数据:")
        hint.setStyleSheet("color: #71717a; font-size: 13px;")
        import_layout.addWidget(hint)

        self.import_text = QTextEdit()
        self.import_text.setPlaceholderText('[{"username": "test", "email": "test@example.com"}]')
        import_layout.addWidget(self.import_text, 1)

        import_btn = QPushButton("导入数据")
        import_btn.setFixedSize(140, 44)
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.clicked.connect(self.import_data)
        import_layout.addWidget(import_btn)

        self.tabs.addTab(import_widget, "  导入  ")

        # 导出
        export_widget = QWidget()
        export_layout = QVBoxLayout(export_widget)
        export_layout.setContentsMargins(0, 0, 0, 0)
        export_layout.setSpacing(16)

        self.export_target = QLabel("请先选择要导出的表")
        self.export_target.setObjectName("targetLabel")
        export_layout.addWidget(self.export_target)

        export_btn = QPushButton("导出 CSV")
        export_btn.setFixedSize(140, 44)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self.export_data)
        export_layout.addWidget(export_btn)
        export_layout.addStretch()

        self.tabs.addTab(export_widget, "  导出  ")

        main_layout.addWidget(self.tabs)
        layout.addWidget(main, 1)
        self.setLayout(layout)

    def load_databases(self):
        self.tree.clear()
        if not self.ensure_connection():
            show_error(self, "连接错误", "数据库连接已断开")
            return
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                for row in cursor.fetchall():
                    name = row["Database"]
                    item = QTreeWidgetItem([f"📁 {name}"])
                    item.setData(0, Qt.ItemDataRole.UserRole, {"type": "db", "name": name})
                    item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                    self.tree.addTopLevelItem(item)
        except Exception as e:
            log_error(f"加载数据库列表失败: {e}")
            show_error(self, "加载失败", str(e))

    def on_tree_expand(self, item):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data["type"] == "db" and item.childCount() == 0:
            if not self.ensure_connection():
                show_error(self, "连接错误", "数据库连接已断开")
                return
            try:
                self.conn.select_db(data["name"])
                with self.conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    for row in cursor.fetchall():
                        tbl = list(row.values())[0]
                        child = QTreeWidgetItem([f"  📄 {tbl}"])
                        child.setData(0, Qt.ItemDataRole.UserRole, {"type": "tbl", "db": data["name"], "name": tbl})
                        item.addChild(child)
            except Exception as e:
                log_error(f"加载表列表失败: {e}")
                show_error(self, "加载失败", str(e))

    def on_tree_click(self, item):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        if data["type"] == "db":
            self.current_db = data["name"]
            self.current_table = None
            self.db_indicator.setText(f"📁  {data['name']}")
            self.import_target.setText(f"数据库: {data['name']}")
            self.export_target.setText("请选择表")
            # 单击展开/收起
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        else:
            self.current_db = data["db"]
            self.current_table = data["name"]
            self.db_indicator.setText(f"📁 {data['db']}  →  📄 {data['name']}")
            self.import_target.setText(f"目标: {data['db']}.{data['name']}")
            self.export_target.setText(f"导出: {data['db']}.{data['name']}")
            self.load_structure()

    def load_structure(self):
        if not self.ensure_connection():
            show_error(self, "连接错误", "数据库连接已断开")
            return
        try:
            self.conn.select_db(self.current_db)
            with self.conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{self.current_table}`")
                rows = cursor.fetchall()
            self.structure_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, k in enumerate(["Field", "Type", "Null", "Key", "Default"]):
                    val = str(r.get(k) or "-")
                    self.structure_table.setItem(i, j, QTableWidgetItem(val))
        except Exception as e:
            log_error(f"加载表结构失败: {e}")
            show_error(self, "加载失败", str(e))

    def execute_query(self):
        if not self.current_db:
            show_warning(self, "提示", "请先选择数据库")
            return
        sql = self.sql_input.toPlainText().strip()
        ok, msg = validate_sql(sql)
        if not ok:
            show_warning(self, "验证", msg)
            return
        if not self.ensure_connection():
            show_error(self, "连接错误", "数据库连接已断开，请重新连接")
            return
        try:
            log_info(f"SQL: {sql[:80]}")
            self.conn.select_db(self.current_db)
            with self.conn.cursor() as cur:
                cur.execute(sql)
                if sql.upper().startswith(("SELECT", "SHOW", "DESC")):
                    rows = cur.fetchall()
                    if rows:
                        cols = list(rows[0].keys())
                        self.result_table.setColumnCount(len(cols))
                        self.result_table.setHorizontalHeaderLabels(cols)
                        self.result_table.setRowCount(len(rows))
                        for i, row in enumerate(rows):
                            for j, c in enumerate(cols):
                                self.result_table.setItem(i, j, QTableWidgetItem(str(row[c] or "")))
                        show_success(self, "查询成功", f"共 {len(rows)} 条记录")
                    else:
                        self.result_table.setRowCount(0)
                        self.result_table.setColumnCount(0)
                        show_info(self, "查询结果", "没有找到数据")
                else:
                    self.conn.commit()
                    show_success(self, "执行成功", f"影响了 {cur.rowcount} 行数据")
        except Exception as e:
            log_error(str(e))
            show_error(self, "执行错误", str(e))

    def import_data(self):
        if not self.current_table:
            show_warning(self, "提示", "请先选择目标表")
            return
        txt = self.import_text.toPlainText()
        ok, msg = validate_json(txt)
        if not ok:
            show_warning(self, "验证", msg)
            return
        if not self.ensure_connection():
            show_error(self, "连接错误", "数据库连接已断开")
            return
        try:
            data = json.loads(txt)
            self.conn.select_db(self.current_db)
            cols = list(data[0].keys())
            sql = f"INSERT INTO `{self.current_table}` ({','.join(f'`{c}`' for c in cols)}) VALUES ({','.join(['%s']*len(cols))})"
            with self.conn.cursor() as cur:
                for row in data:
                    cur.execute(sql, [row.get(c) for c in cols])
            self.conn.commit()
            show_success(self, "导入成功", f"成功导入 {len(data)} 条数据")
        except Exception as e:
            show_error(self, "导入失败", str(e))

    def export_data(self):
        if not self.current_table:
            show_warning(self, "提示", "请先选择要导出的表")
            return
        if not self.ensure_connection():
            show_error(self, "连接错误", "数据库连接已断开")
            return
        try:
            self.conn.select_db(self.current_db)
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{self.current_table}`")
                rows = cur.fetchall()
            if not rows:
                show_info(self, "提示", "表中没有数据")
                return
            path, _ = QFileDialog.getSaveFileName(self, "保存", f"{self.current_table}.csv", "CSV (*.csv)")
            if path:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=rows[0].keys())
                    w.writeheader()
                    w.writerows(rows)
                show_success(self, "导出成功", f"已保存到\n{path}")
        except Exception as e:
            show_error(self, "导出失败", str(e))

    def disconnect(self):
        log_info("断开")
        self.conn.close()
        self.on_disconnect()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL Manager")
        self.setMinimumSize(1200, 800)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.show_login()

    def show_login(self):
        self.statusBar.showMessage("等待连接...")
        self.setCentralWidget(LoginWidget(self.on_connect))

    def on_connect(self, conn):
        self.statusBar.showMessage("● 已连接")
        self.setCentralWidget(ManagerWidget(conn, self.show_login))


def main():
    try:
        log_info("启动")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setStyleSheet(DARK_THEME)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

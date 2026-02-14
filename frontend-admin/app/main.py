#!/usr/bin/env python3
"""SQL Manager - 主程序入口"""
import sys
import csv
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QTextEdit, QTabWidget,
    QFileDialog, QFrame, QHeaderView, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt

from app.logger import log_info, log_error
from app.config import load_config, save_config
from app.database import DatabaseService
from app.validators import validate_host, validate_port, validate_user, validate_sql, validate_json, is_dangerous_sql
from app.styles import DARK_THEME
from app.dialogs import show_info, show_success, show_warning, show_error


class LoginWidget(QWidget):
    """登录界面"""
    def __init__(self, on_connect):
        super().__init__()
        self.on_connect = on_connect
        self.config = load_config()
        self.db_service = DatabaseService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(400, 560)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(0)

        icon_label = QLabel("⬡")
        icon_label.setStyleSheet("font-size: 42px; color: #8b5cf6;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        card_layout.addSpacing(12)

        title = QLabel("SQL Manager")
        title.setObjectName("logoLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("连接您的数据库")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(28)

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
            self.db_service.connect(host.strip(), int(port), user.strip(), password)
            save_config({"host": host.strip(), "port": int(port), "user": user.strip(), "password": password})
            self.on_connect(self.db_service)
        except Exception as e:
            log_error(f"连接失败: {e}")
            show_error(self, "连接失败", str(e))


class ManagerWidget(QWidget):
    """主管理界面"""
    def __init__(self, db_service: DatabaseService, on_disconnect):
        super().__init__()
        self.db = db_service
        self.on_disconnect = on_disconnect
        self.current_db = None
        self.current_table = None
        self.init_ui()
        self.load_databases()

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

        self.db_indicator = QLabel("选择数据库开始")
        self.db_indicator.setObjectName("dbIndicator")
        self.db_indicator.setWordWrap(True)
        sidebar_layout.addWidget(self.db_indicator)

        section = QLabel("数据库列表")
        section.setObjectName("sectionLabel")
        sidebar_layout.addWidget(section)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(0)
        self.tree.setAnimated(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setStyleSheet("""
            QTreeWidget { background-color: transparent; border: none; outline: none; }
            QTreeWidget::branch { background: transparent; border: none; image: none; width: 0px; }
            QTreeWidget::item { background-color: transparent; padding: 8px 12px; margin: 2px 4px; border-radius: 6px; color: #a1a1aa; }
            QTreeWidget::item:hover { background-color: #27272a; color: #e4e4e7; }
            QTreeWidget::item:selected { background-color: #8b5cf6; color: white; }
        """)
        self.tree.itemClicked.connect(self.on_tree_click)
        self.tree.itemExpanded.connect(self.on_tree_expand)
        sidebar_layout.addWidget(self.tree, 1)

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

        self.tabs = QTabWidget()
        self._setup_structure_tab()
        self._setup_query_tab()
        self._setup_import_tab()
        self._setup_export_tab()

        main_layout.addWidget(self.tabs)
        layout.addWidget(main, 1)
        self.setLayout(layout)

    def _setup_structure_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.structure_table = QTableWidget()
        self.structure_table.setColumnCount(5)
        self.structure_table.setHorizontalHeaderLabels(["字段", "类型", "可空", "键", "默认值"])
        self.structure_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.structure_table.setAlternatingRowColors(True)
        self.structure_table.verticalHeader().setVisible(False)
        self.structure_table.setShowGrid(False)
        layout.addWidget(self.structure_table)
        self.tabs.addTab(widget, "  结构  ")

    def _setup_query_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText("输入 SQL 查询语句...\n\n例如:\nSELECT * FROM users;\nSELECT name, price FROM products WHERE stock > 50;")
        self.sql_input.setFixedHeight(160)
        layout.addWidget(self.sql_input)

        btn_row = QHBoxLayout()
        exec_btn = QPushButton("执行查询")
        exec_btn.setFixedSize(140, 44)
        exec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exec_btn.clicked.connect(self.execute_query)
        btn_row.addWidget(exec_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setShowGrid(False)
        layout.addWidget(self.result_table, 1)

        self.tabs.addTab(widget, "  查询  ")

    def _setup_import_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.import_target = QLabel("请先选择目标表")
        self.import_target.setObjectName("targetLabel")
        layout.addWidget(self.import_target)

        hint = QLabel("JSON 格式数据:")
        hint.setStyleSheet("color: #71717a; font-size: 13px;")
        layout.addWidget(hint)

        self.import_text = QTextEdit()
        self.import_text.setPlaceholderText('[{"username": "test", "email": "test@example.com"}]')
        layout.addWidget(self.import_text, 1)

        import_btn = QPushButton("导入数据")
        import_btn.setFixedSize(140, 44)
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.clicked.connect(self.import_data)
        layout.addWidget(import_btn)

        self.tabs.addTab(widget, "  导入  ")

    def _setup_export_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.export_target = QLabel("请先选择要导出的表")
        self.export_target.setObjectName("targetLabel")
        layout.addWidget(self.export_target)

        export_btn = QPushButton("导出 CSV")
        export_btn.setFixedSize(140, 44)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self.export_data)
        layout.addWidget(export_btn)
        layout.addStretch()

        self.tabs.addTab(widget, "  导出  ")

    def load_databases(self):
        self.tree.clear()
        try:
            for name in self.db.get_databases():
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
            try:
                for tbl in self.db.get_tables(data["name"]):
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
            item.setExpanded(not item.isExpanded())
        else:
            self.current_db = data["db"]
            self.current_table = data["name"]
            self.db_indicator.setText(f"📁 {data['db']}  →  📄 {data['name']}")
            self.import_target.setText(f"目标: {data['db']}.{data['name']}")
            self.export_target.setText(f"导出: {data['db']}.{data['name']}")
            self.load_structure()

    def load_structure(self):
        try:
            rows = self.db.get_table_structure(self.current_db, self.current_table)
            self.structure_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, k in enumerate(["Field", "Type", "Null", "Key", "Default"]):
                    self.structure_table.setItem(i, j, QTableWidgetItem(str(r.get(k) or "-")))
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
        
        # 检查是否需要二次确认
        is_dangerous, op, desc = is_dangerous_sql(msg)
        if is_dangerous:
            reply = QMessageBox.warning(
                self, "危险操作确认",
                f"您即将执行危险操作：{op}\n\n{desc}\n\n确定要继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            rows, count = self.db.execute_query(sql, self.current_db)
            if rows:
                cols = list(rows[0].keys())
                self.result_table.setColumnCount(len(cols))
                self.result_table.setHorizontalHeaderLabels(cols)
                self.result_table.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    for j, c in enumerate(cols):
                        self.result_table.setItem(i, j, QTableWidgetItem(str(row[c] or "")))
                show_success(self, "查询成功", f"共 {len(rows)} 条记录")
            elif sql.strip().upper().startswith(("SELECT", "SHOW", "DESC")):
                self.result_table.setRowCount(0)
                self.result_table.setColumnCount(0)
                show_info(self, "查询结果", "没有找到数据")
            else:
                show_success(self, "执行成功", f"影响了 {count} 行数据")
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
        try:
            data = json.loads(txt)
            count = self.db.import_data(self.current_db, self.current_table, data)
            show_success(self, "导入成功", f"成功导入 {count} 条数据")
        except Exception as e:
            show_error(self, "导入失败", str(e))

    def export_data(self):
        if not self.current_table:
            show_warning(self, "提示", "请先选择要导出的表")
            return
        try:
            rows = self.db.export_data(self.current_db, self.current_table)
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
        self.db.disconnect()
        self.on_disconnect()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL Manager")
        self.setMinimumSize(1200, 800)
        # 强制深色背景
        self.setStyleSheet("QMainWindow { background-color: #0a0a0b; }")
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.show_login()

    def show_login(self):
        self.statusBar.showMessage("等待连接...")
        widget = LoginWidget(self.on_connect)
        self.setCentralWidget(widget)

    def on_connect(self, db_service: DatabaseService):
        self.statusBar.showMessage("● 已连接")
        widget = ManagerWidget(db_service, self.show_login)
        self.setCentralWidget(widget)


def main():
    try:
        log_info("启动应用")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # 设置深色调色板
        from PyQt6.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0a0a0b"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#e4e4e7"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#18181b"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1f1f23"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#e4e4e7"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#27272a"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e4e4e7"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#8b5cf6"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        app.setPalette(palette)
        
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

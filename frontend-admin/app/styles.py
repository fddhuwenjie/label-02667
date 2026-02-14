"""现代深色主题"""

DARK_THEME = """
QMainWindow {
    background-color: #0a0a0b;
}

QWidget {
    background-color: transparent;
    color: #e4e4e7;
    font-size: 13px;
}

QFrame#loginCard {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 16px;
}

QFrame#sidebar {
    background-color: #111113;
    border-right: 1px solid #27272a;
}

QLabel {
    color: #e4e4e7;
    background-color: transparent;
}

QLabel#logoLabel {
    font-size: 18px;
    font-weight: 600;
    color: #fafafa;
}

QLabel#subtitleLabel {
    font-size: 14px;
    color: #71717a;
}

QLabel#sectionLabel {
    font-size: 11px;
    font-weight: 600;
    color: #52525b;
    text-transform: uppercase;
    padding: 4px 0;
}

QLabel#inputLabel {
    font-size: 13px;
    color: #a1a1aa;
    font-weight: 500;
    padding: 2px 0;
}

QLabel#dbIndicator {
    background-color: #1e1b4b;
    border: 1px solid #312e81;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 13px;
    color: #c4b5fd;
}

QLabel#targetLabel {
    color: #a1a1aa;
    font-size: 14px;
    padding: 8px 0;
}

QLineEdit {
    background-color: #1f1f23;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 14px;
    color: #fafafa;
    selection-background-color: #8b5cf6;
}

QLineEdit:hover {
    border-color: #52525b;
}

QLineEdit:focus {
    border-color: #8b5cf6;
    background-color: #27272a;
}

QTextEdit {
    background-color: #1f1f23;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 14px;
    font-size: 13px;
    color: #fafafa;
}

QTextEdit:focus {
    border-color: #8b5cf6;
}

QPushButton {
    background-color: #8b5cf6;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #a78bfa;
}

QPushButton:pressed {
    background-color: #7c3aed;
}

QPushButton#dangerBtn {
    background-color: #7f1d1d;
    border: 1px solid #991b1b;
}

QPushButton#dangerBtn:hover {
    background-color: #991b1b;
}

/* 树形列表 - 完全移除蓝色 */
QTreeView, QTreeWidget {
    background-color: transparent;
    border: none;
    outline: none;
    font-size: 13px;
    show-decoration-selected: 0;
    selection-background-color: transparent;
}

QTreeView::item, QTreeWidget::item {
    padding: 8px 12px;
    border-radius: 6px;
    margin: 1px 4px;
    color: #a1a1aa;
    background-color: transparent;
    border: none;
}

QTreeView::item:hover, QTreeWidget::item:hover {
    background-color: #27272a;
    color: #e4e4e7;
}

QTreeView::item:selected, QTreeWidget::item:selected {
    background-color: #8b5cf6;
    color: #ffffff;
}

QTreeView::branch, QTreeWidget::branch {
    background-color: transparent;
    border: none;
    border-image: none;
    image: none;
    width: 0px;
}

/* 标签页 */
QTabWidget::pane {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 16px;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: transparent;
    color: #71717a;
    padding: 10px 20px;
    margin-right: 4px;
    font-size: 14px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:hover {
    color: #a1a1aa;
}

QTabBar::tab:selected {
    color: #8b5cf6;
    border-bottom-color: #8b5cf6;
}

/* 表格 - 深色背景 */
QTableView, QTableWidget {
    background-color: #18181b;
    alternate-background-color: #1f1f23;
    border: 1px solid #27272a;
    border-radius: 8px;
    gridline-color: #27272a;
    font-size: 13px;
    selection-background-color: #7c3aed;
}

QTableView::item, QTableWidget::item {
    padding: 10px 14px;
    color: #e4e4e7;
    background-color: #18181b;
    border: none;
}

QTableView::item:alternate, QTableWidget::item:alternate {
    background-color: #1f1f23;
}

QTableView::item:selected, QTableWidget::item:selected {
    background-color: #7c3aed;
    color: #ffffff;
}

QHeaderView {
    background-color: #27272a;
}

QHeaderView::section {
    background-color: #27272a;
    color: #a1a1aa;
    padding: 12px 14px;
    border: none;
    font-weight: 600;
    font-size: 12px;
}

/* 状态栏 */
QStatusBar {
    background-color: #111113;
    border-top: 1px solid #27272a;
    color: #71717a;
    padding: 8px 16px;
    font-size: 12px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #18181b;
    width: 8px;
    border-radius: 4px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #3f3f46;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #52525b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0px;
    border: none;
}

QScrollBar:horizontal {
    background-color: #18181b;
    height: 8px;
    border-radius: 4px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background-color: #3f3f46;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
    width: 0px;
    border: none;
}

/* 消息框 */
QMessageBox {
    background-color: #18181b;
}

QMessageBox QLabel {
    color: #e4e4e7;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""

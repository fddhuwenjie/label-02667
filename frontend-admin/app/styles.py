"""现代深色主题样式"""

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0f0f10;
    color: #e4e4e7;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

QGroupBox {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 12px;
    margin-top: 12px;
    padding: 20px;
    font-weight: 600;
    font-size: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 0 8px;
    color: #a1a1aa;
}

QLabel {
    color: #a1a1aa;
    font-size: 13px;
}

QLineEdit, QTextEdit {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 10px 14px;
    color: #e4e4e7;
    font-size: 13px;
    selection-background-color: #8b5cf6;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #8b5cf6;
}

QLineEdit:hover, QTextEdit:hover {
    border-color: #3f3f46;
}

QPushButton {
    background-color: #8b5cf6;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #7c3aed;
}

QPushButton:pressed {
    background-color: #6d28d9;
}

QPushButton:disabled {
    background-color: #3f3f46;
    color: #71717a;
}

QPushButton#secondaryBtn {
    background-color: #27272a;
    color: #e4e4e7;
}

QPushButton#secondaryBtn:hover {
    background-color: #3f3f46;
}

QPushButton#dangerBtn {
    background-color: #dc2626;
}

QPushButton#dangerBtn:hover {
    background-color: #b91c1c;
}

QTreeWidget {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 8px;
    outline: none;
}

QTreeWidget::item {
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px 0;
}

QTreeWidget::item:hover {
    background-color: #27272a;
}

QTreeWidget::item:selected {
    background-color: #8b5cf6;
    color: white;
}

QTreeWidget::branch {
    background-color: transparent;
}

QHeaderView::section {
    background-color: #1f1f23;
    color: #a1a1aa;
    padding: 12px 16px;
    border: none;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}

QTableWidget {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    gridline-color: #27272a;
}

QTableWidget::item {
    padding: 12px 16px;
    border-bottom: 1px solid #27272a;
}

QTableWidget::item:selected {
    background-color: #8b5cf6;
    color: white;
}

QTabWidget::pane {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: transparent;
    color: #71717a;
    padding: 14px 20px;
    font-size: 13px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
}

QTabBar::tab:hover {
    color: #e4e4e7;
}

QTabBar::tab:selected {
    color: #8b5cf6;
    border-bottom-color: #8b5cf6;
}

QSplitter::handle {
    background-color: #27272a;
    width: 1px;
}

QStatusBar {
    background-color: #18181b;
    border-top: 1px solid #27272a;
    color: #71717a;
    padding: 8px 16px;
    font-size: 12px;
}

QScrollBar:vertical {
    background-color: #18181b;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #3f3f46;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #52525b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #18181b;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #3f3f46;
    border-radius: 4px;
    min-width: 30px;
}

QMessageBox {
    background-color: #18181b;
}

QMessageBox QLabel {
    color: #e4e4e7;
    font-size: 14px;
}
"""

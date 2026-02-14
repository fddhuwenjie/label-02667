"""自定义弹窗"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class CustomDialog(QDialog):
    def __init__(self, parent, title, message, dialog_type="info"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(380)
        
        # 类型配置
        config = {
            "info": ("ℹ", "#3b82f6"),
            "success": ("✓", "#22c55e"),
            "warning": ("!", "#f59e0b"),
            "error": ("✕", "#ef4444")
        }
        icon, color = config.get(dialog_type, config["info"])
        
        # 主容器
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1a1a1d;
                border-radius: 20px;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(36, 40, 36, 36)
        layout.setSpacing(0)
        
        # 图标圆圈
        icon_label = QLabel(icon)
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
                background-color: {color}18;
                border-radius: 32px;
            }}
        """)
        
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)
        layout.addSpacing(24)
        
        # 标题
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #fafafa;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        layout.addSpacing(10)
        
        # 消息
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #71717a;
                background: transparent;
                line-height: 1.6;
            }
        """)
        layout.addWidget(msg_label)
        layout.addSpacing(32)
        
        # 按钮
        btn = QPushButton("好的")
        btn.setFixedHeight(46)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {color}cc;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        
        # 外层
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(container)


def show_info(parent, title, message):
    CustomDialog(parent, title, message, "info").exec()


def show_success(parent, title, message):
    CustomDialog(parent, title, message, "success").exec()


def show_warning(parent, title, message):
    CustomDialog(parent, title, message, "warning").exec()


def show_error(parent, title, message):
    CustomDialog(parent, title, message, "error").exec()

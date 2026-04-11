from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QLineEdit, QCheckBox,
    QMessageBox, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QColor, QFont, QPainter, QLinearGradient, QBrush, QPen
from database.db import Database, UserDB


class AnimatedLineEdit(QLineEdit):
    def __init__(self, placeholder, echo_mode=QLineEdit.Normal, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setEchoMode(echo_mode)
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QLineEdit {
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 0 16px;
                font-size: 14px;
                color: #0f172a;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                background: white;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
        """)


class LoginWidget(QWidget):
    login_success = pyqtSignal(dict)  # emit user info

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        # Full screen layout with gradient background
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel - branding
        left = QFrame()
        left.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4f46e5,
                    stop:0.5 #6366f1,
                    stop:1 #818cf8
                );
            }
        """)
        left.setMinimumWidth(420)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(50, 60, 50, 60)
        left_layout.setSpacing(20)

        left_layout.addStretch(2)

        logo = QLabel("🛍️")
        logo.setStyleSheet("font-size: 64px; background: transparent;")
        logo.setAlignment(Qt.AlignCenter)

        brand = QLabel("TAP HOA HOAIDUC")
        brand.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: 800;
            background: transparent;
            letter-spacing: 1px;
        """)
        brand.setAlignment(Qt.AlignCenter)

        tagline = QLabel("Quản lý bán hàng thông minh\ncho doanh nghiệp của bạn")
        tagline.setStyleSheet("""
            color: rgba(255,255,255,0.8);
            font-size: 15px;
            background: transparent;
            line-height: 1.6;
        """)
        tagline.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(logo)
        left_layout.addWidget(brand)
        left_layout.addSpacing(8)
        left_layout.addWidget(tagline)

        left_layout.addStretch(1)

        # Feature list
        features = [
            ("📊", "Thống kê doanh thu theo thời gian thực"),
            ("📦", "Quản lý kho hàng thông minh"),
            ("👥", "Chăm sóc khách hàng chuyên nghiệp"),
            ("🧾", "Xử lý đơn hàng nhanh chóng"),
        ]
        for icon, text in features:
            row = QHBoxLayout()
            row.setSpacing(12)
            ico = QLabel(icon)
            ico.setStyleSheet("font-size: 18px; background: transparent;")
            ico.setFixedWidth(28)
            lbl = QLabel(text)
            lbl.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 13px; background: transparent;")
            row.addWidget(ico)
            row.addWidget(lbl)
            row.addStretch()
            left_layout.addLayout(row)

        left_layout.addStretch(2)

        version = QLabel("Phiên bản 1.0.0 • MongoDB Edition")
        version.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px; background: transparent;")
        version.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(version)

        main_layout.addWidget(left)

        # Right panel - login form
        right = QFrame()
        right.setStyleSheet("QFrame { background: #f8fafc; }")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignCenter)

        # Card
        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(0)

        # Card title
        welcome = QLabel("Chào mừng trở lại 👋")
        welcome.setStyleSheet("color: #0f172a; font-size: 22px; font-weight: 800;")
        sub = QLabel("Đăng nhập để tiếp tục quản lý")
        sub.setStyleSheet("color: #94a3b8; font-size: 13px; margin-top: 4px;")

        card_layout.addWidget(welcome)
        card_layout.addWidget(sub)
        card_layout.addSpacing(32)

        # Username
        user_lbl = QLabel("Tên đăng nhập")
        user_lbl.setStyleSheet("color: #374151; font-size: 13px; font-weight: 600;")
        self.username_input = AnimatedLineEdit("Nhập tên đăng nhập...")
        self.username_input.setText("admin")
        card_layout.addWidget(user_lbl)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(16)

        # Password
        pass_lbl = QLabel("Mật khẩu")
        pass_lbl.setStyleSheet("color: #374151; font-size: 13px; font-weight: 600;")

        pass_row = QHBoxLayout()
        self.password_input = AnimatedLineEdit("Nhập mật khẩu...", QLineEdit.Password)
        self.password_input.setText("admin123")
        self.password_input.returnPressed.connect(self._do_login)

        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setFixedSize(44, 44)  # slightly smaller than input
        self.show_pass_btn.setCursor(Qt.PointingHandCursor)
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 16px;
                color: #64748b;
            }
            QPushButton:checked { background: #eef2ff; border-color: #6366f1; }
            QPushButton:hover { background: #e2e8f0; }
        """)
        self.show_pass_btn.toggled.connect(self._toggle_password)

        pass_row.addWidget(self.password_input)
        pass_row.addSpacing(8)
        pass_row.addWidget(self.show_pass_btn)

        card_layout.addWidget(pass_lbl)
        card_layout.addSpacing(6)
        card_layout.addLayout(pass_row)
        card_layout.addSpacing(12)

        # Remember me
        self.remember_cb = QCheckBox("Ghi nhớ đăng nhập")
        self.remember_cb.setChecked(True)
        self.remember_cb.setStyleSheet("""
            QCheckBox {
                color: #64748b;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 2px solid #e2e8f0;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #6366f1;
                border-color: #6366f1;
                image: none;
            }
        """)
        card_layout.addWidget(self.remember_cb)
        card_layout.addSpacing(24)

        # Error message
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("""
            color: #dc2626;
            background: #fee2e2;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
        """)
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.hide()
        card_layout.addWidget(self.error_lbl)

        # Login button
        self.login_btn = QPushButton("Đăng nhập →")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #818cf8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #6366f1);
            }
            QPushButton:pressed { background: #4338ca; }
            QPushButton:disabled { background: #c7d2fe; }
        """)
        self.login_btn.clicked.connect(self._do_login)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.login_btn)
        card_layout.addSpacing(24)

        # Default accounts hint
        hint_frame = QFrame()
        hint_frame.setStyleSheet("QFrame { background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; }")
        hint_layout = QVBoxLayout(hint_frame)
        hint_layout.setContentsMargins(14, 12, 14, 12)
        hint_layout.setSpacing(4)

        # # hint_title = QLabel("💡 Tài khoản mặc định:")
        # # hint_title.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600; background: transparent;")

        # # hint_admin = QLabel("👑  admin / admin123  (Quản trị viên)")
        # # hint_admin.setStyleSheet("color: #6366f1; font-size: 12px; background: transparent;")

        # # hint_staff = QLabel("👤  nhanvien / 123456  (Nhân viên)")
        # # hint_staff.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")

        # hint_layout.addWidget(hint_title)
        # hint_layout.addWidget(hint_admin)
        # hint_layout.addWidget(hint_staff)
        # card_layout.addWidget(hint_frame)

        right_layout.addWidget(card)
        main_layout.addWidget(right, 1)

    def _toggle_password(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self._show_error("Vui lòng nhập tên đăng nhập và mật khẩu!")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Đang đăng nhập...")

        try:
            user_db = UserDB()
            user = user_db.authenticate(username, password)
            if user:
                self.error_lbl.hide()
                self.login_success.emit(user)
            else:
                self._show_error("Tên đăng nhập hoặc mật khẩu không đúng!")
        except Exception as e:
            self._show_error(f"Lỗi kết nối: {str(e)}")
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Đăng nhập →")

    def _show_error(self, msg):
        self.error_lbl.setText(f"⚠️  {msg}")
        self.error_lbl.show()

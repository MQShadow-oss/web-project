from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QGraphicsDropShadowEffect, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from ui.dashboard import DashboardWidget
from ui.products import ProductsWidget
from ui.customers import CustomersWidget
from ui.orders import OrdersWidget
from database.db import Database


class SidebarButton(QPushButton):
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.icon_text = icon_text
        self.label_text = label
        self._build_ui()
        self.setFixedHeight(52)
        self.setCursor(Qt.PointingHandCursor)

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        icon_label = QLabel(self.icon_text)
        icon_label.setFixedWidth(24)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 18px; background: transparent; color: inherit;")

        text_label = QLabel(self.label_text)
        text_label.setStyleSheet("font-size: 14px; font-weight: 500; background: transparent; color: inherit;")

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()

        self.setStyleSheet("""
            SidebarButton {
                background: transparent;
                border: none;
                border-radius: 10px;
                color: #94a3b8;
                text-align: left;
            }
            SidebarButton:hover {
                background: rgba(255,255,255,0.07);
                color: #e2e8f0;
            }
            SidebarButton:checked {
                background: rgba(99, 102, 241, 0.2);
                color: #a5b4fc;
                border-left: 3px solid #6366f1;
            }
        """)


class Sidebar(QWidget):
    page_changed = pyqtSignal(int)
    logout_clicked = pyqtSignal()

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user or {}
        self.setFixedWidth(220)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            Sidebar {
                background: #0f172a;
                border-right: 1px solid #1e293b;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 16)
        layout.setSpacing(4)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(70)
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 0, 20, 0)
        logo_icon = QLabel("🛍️")
        logo_icon.setStyleSheet("font-size: 24px;")
        logo_name = QLabel("BánHàng Pro")
        logo_name.setStyleSheet("color: white; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_name)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)

        # User info card
        user_card = QFrame()
        user_card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.08);
            }
        """)
        user_layout = QHBoxLayout(user_card)
        user_layout.setContentsMargins(12, 10, 12, 10)
        user_layout.setSpacing(10)

        role = self.user.get("vai_tro", "staff")
        avatar_icon = "👑" if role == "admin" else "👤"
        avatar = QLabel(avatar_icon)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            background: rgba(99,102,241,0.3);
            border-radius: 18px;
            font-size: 18px;
        """)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        name_lbl = QLabel(self.user.get("ho_ten", "Người dùng"))
        name_lbl.setStyleSheet("color: #e2e8f0; font-size: 12px; font-weight: 600; background: transparent;")
        name_lbl.setMaximumWidth(120)

        role_text = "Quản trị viên" if role == "admin" else "Nhân viên"
        role_lbl = QLabel(role_text)
        role_lbl.setStyleSheet("color: #6366f1; font-size: 11px; background: transparent;")

        info_col.addWidget(name_lbl)
        info_col.addWidget(role_lbl)

        user_layout.addWidget(avatar)
        user_layout.addLayout(info_col)
        user_layout.addStretch()
        layout.addWidget(user_card)
        layout.addSpacing(8)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #1e293b; margin: 0 8px;")
        layout.addWidget(div)
        layout.addSpacing(4)

        # Menu label
        menu_label = QLabel("MENU CHÍNH")
        menu_label.setStyleSheet("color: #475569; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; padding: 0 20px; margin-top: 4px;")
        layout.addWidget(menu_label)
        layout.addSpacing(4)

        # Nav buttons
        self.buttons = []
        nav_items = [
            ("📊", "Tổng quan"),
            ("📦", "Sản phẩm"),
            ("👥", "Khách hàng"),
            ("🧾", "Đơn hàng"),
        ]
        for i, (icon, label) in enumerate(nav_items):
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda checked, idx=i: self._on_button_click(idx))
            self.buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Bottom
        div2 = QFrame()
        div2.setFixedHeight(1)
        div2.setStyleSheet("background: #1e293b; margin: 0 8px;")
        layout.addWidget(div2)
        layout.addSpacing(8)

        # DB status
        self.db_status = QLabel("● MongoDB Connected")
        self.db_status.setStyleSheet("color: #22c55e; font-size: 11px; padding: 0 20px;")
        layout.addWidget(self.db_status)
        layout.addSpacing(8)

        # Logout button
        logout_btn = QPushButton("🚪  Đăng xuất")
        logout_btn.setFixedHeight(40)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239,68,68,0.1);
                color: #f87171;
                border: 1px solid rgba(239,68,68,0.2);
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(239,68,68,0.2);
                color: #fca5a5;
            }
        """)
        logout_btn.clicked.connect(self._confirm_logout)
        layout.addWidget(logout_btn)

        self.buttons[0].setChecked(True)

    def _on_button_click(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.page_changed.emit(index)

    def set_db_status(self, connected):
        if connected:
            self.db_status.setText("● MongoDB Connected")
            self.db_status.setStyleSheet("color: #22c55e; font-size: 11px; padding: 0 20px;")
        else:
            self.db_status.setText("● Không có kết nối DB")
            self.db_status.setStyleSheet("color: #ef4444; font-size: 11px; padding: 0 20px;")

    def _confirm_logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất",
            "Bạn có chắc muốn đăng xuất không?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_clicked.emit()


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user=None):
        super().__init__()
        self.user = user or {}
        self.setWindowTitle("QuanLyBanHang Pro")
        self.setMinimumSize(1200, 750)
        self._init_db()
        self._build_ui()

    def _init_db(self):
        try:
            db = Database.get_instance()
            self.db_connected = db.is_connected()
        except:
            self.db_connected = False

    def update_user(self, user):
        self.user = user

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background: #f8fafc;")

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar(user=self.user)
        self.sidebar.page_changed.connect(self._change_page)
        self.sidebar.logout_clicked.connect(self.logout_requested.emit)
        self.sidebar.set_db_status(self.db_connected)
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #f1f5f9;")

        if self.db_connected:
            self.stack.addWidget(DashboardWidget())
            self.stack.addWidget(ProductsWidget())
            self.stack.addWidget(CustomersWidget())
            self.stack.addWidget(OrdersWidget())
        else:
            self._show_no_db_page()

        main_layout.addWidget(self.stack)

    def _show_no_db_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("🔌")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 64px;")

        title = QLabel("Không thể kết nối MongoDB")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b; margin-top: 16px;")

        desc = QLabel("Vui lòng đảm bảo MongoDB đang chạy tại\nmongodb://localhost:27017/")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 14px; color: #64748b; margin-top: 8px;")

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        self.stack.addWidget(page)

    def _change_page(self, index):
        self.stack.setCurrentIndex(index)
        widget = self.stack.currentWidget()
        if hasattr(widget, 'refresh'):
            widget.refresh()

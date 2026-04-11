import sys
import os
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt
from ui.login import LoginWidget
from ui.main_window import MainWindow
from database.db import Database


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("QuanLyBanHang Pro")

    app.setStyleSheet("""
        * { font-family: 'Segoe UI', Arial, sans-serif; }
        QToolTip {
            background-color: #1e293b; color: white;
            border: 1px solid #334155; border-radius: 4px; padding: 4px 8px;
        }
        QScrollBar:vertical { background: #f1f5f9; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background: #94a3b8; border-radius: 4px; min-height: 20px; }
        QScrollBar::handle:vertical:hover { background: #64748b; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        QScrollBar:horizontal { background: #f1f5f9; height: 8px; border-radius: 4px; }
        QScrollBar::handle:horizontal { background: #94a3b8; border-radius: 4px; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
    """)

    stack = QStackedWidget()
    stack.setWindowTitle("QuanLyBanHang Pro")
    stack.resize(1400, 860)

    login_widget = LoginWidget()
    main_window_holder = [None]

    def on_login_success(user):
        if main_window_holder[0] is None:
            main_window_holder[0] = MainWindow(user=user)
            main_window_holder[0].logout_requested.connect(on_logout)
            stack.addWidget(main_window_holder[0])
        else:
            main_window_holder[0].update_user(user)
        stack.setCurrentIndex(1)
        stack.setWindowTitle(f"QuanLyBanHang Pro — {user.get('ho_ten', user.get('username', ''))}")

    def on_logout():
        stack.setCurrentIndex(0)
        stack.setWindowTitle("QuanLyBanHang Pro")
        login_widget.password_input.clear()
        login_widget.error_lbl.hide()

    login_widget.login_success.connect(on_login_success)
    stack.addWidget(login_widget)
    stack.setCurrentIndex(0)
    stack.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QMessageBox, QAbstractItemView, QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from database.db import CustomerDB
import pandas as pd
from PyQt5.QtWidgets import QFileDialog


STYLE_INPUT = """
    QLineEdit, QComboBox, QTextEdit {
        background: #f8fafc;
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #0f172a;
    }
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
        border-color: #6366f1;
        background: white;
    }
"""

STYLE_BTN_PRIMARY = """
    QPushButton {
        background: #6366f1;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        padding: 0 20px;
    }
    QPushButton:hover { background: #4f46e5; }
"""

STYLE_BTN_SECONDARY = """
    QPushButton {
        background: #f1f5f9;
        color: #475569;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        padding: 0 20px;
    }
    QPushButton:hover { background: #e2e8f0; }
"""

STYLE_BTN_SUCCESS = """
    QPushButton {
        background: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        padding: 0 20px;
    }
    QPushButton:hover { background: #059669; }
    QPushButton:pressed { background: #047857; }
"""

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer_data=None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.is_edit = customer_data is not None
        self.setWindowTitle("Chỉnh sửa khách hàng" if self.is_edit else "Thêm khách hàng")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._build_ui()
        if self.is_edit:
            self._fill_data()

    def _build_ui(self):
        self.setStyleSheet("QDialog { background: white; } QLabel { color: #374151; font-size: 13px; font-weight: 500; }" + STYLE_INPUT)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        title = QLabel("✏️ Chỉnh sửa khách hàng" if self.is_edit else "➕ Thêm khách hàng mới")
        title.setStyleSheet("color: #0f172a; font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.ten = QLineEdit()
        self.ten.setPlaceholderText("Họ và tên")
        form.addRow("Tên khách hàng *", self.ten)

        self.sdt = QLineEdit()
        self.sdt.setPlaceholderText("0901234567")
        form.addRow("Số điện thoại *", self.sdt)

        self.email = QLineEdit()
        self.email.setPlaceholderText("email@example.com")
        form.addRow("Email", self.email)

        self.dia_chi = QTextEdit()
        self.dia_chi.setPlaceholderText("Địa chỉ...")
        self.dia_chi.setFixedHeight(70)
        form.addRow("Địa chỉ", self.dia_chi)

        self.loai = QComboBox()
        self.loai.addItems(["Thường", "VIP", "Đại lý"])
        form.addRow("Loại khách hàng", self.loai)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("💾  Lưu")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _fill_data(self):
        self.ten.setText(self.customer_data.get("ten_khach_hang", ""))
        self.sdt.setText(self.customer_data.get("so_dien_thoai", ""))
        self.email.setText(self.customer_data.get("email", ""))
        self.dia_chi.setPlainText(self.customer_data.get("dia_chi", ""))
        idx = self.loai.findText(self.customer_data.get("loai_khach_hang", "Thường"))
        if idx >= 0:
            self.loai.setCurrentIndex(idx)

    def _save(self):
        if not self.ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên khách hàng!")
            return
        if not self.sdt.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số điện thoại!")
            return
        self.result_data = {
            "ten_khach_hang": self.ten.text().strip(),
            "so_dien_thoai": self.sdt.text().strip(),
            "email": self.email.text().strip(),
            "dia_chi": self.dia_chi.toPlainText().strip(),
            "loai_khach_hang": self.loai.currentText(),
        }
        self.accept()


class CustomersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = CustomerDB()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("👥 Quản lý khách hàng")
        title.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 800;")
        add_btn = QPushButton("+ Thêm khách hàng")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_customer)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)
        
        # Trong hàm _build_ui của CustomersWidget
        self.export_btn = QPushButton("📊 Xuất Excel")
        self.export_btn.setFixedHeight(40)
        self.export_btn.setStyleSheet(STYLE_BTN_SUCCESS) # Dùng style xanh lá mình đã đưa
        self.export_btn.clicked.connect(self._export_excel)
        header.addWidget(self.export_btn)

        # Filter
        filter_frame = QFrame()
        filter_frame.setStyleSheet("QFrame { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }" + STYLE_INPUT)
        fl = QHBoxLayout(filter_frame)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(12)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Tìm theo tên, SĐT, email...")
        self.search_box.setFixedHeight(38)
        self.search_box.textChanged.connect(self.refresh)

        self.count_label = QLabel("0 khách hàng")
        self.count_label.setStyleSheet("color: #64748b; font-size: 13px;")

        fl.addWidget(self.search_box, 1)
        fl.addWidget(self.count_label)
        layout.addWidget(filter_frame)

        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Tên khách hàng", "Số điện thoại", "Email",
            "Loại KH", "Địa chỉ", "Đơn hàng", "Tổng mua", "Thao tác"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                gridline-color: #f1f5f9;
                font-size: 13px;
            }
            QHeaderView::section {
                background: #f8fafc;
                color: #64748b;
                font-weight: 700;
                font-size: 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 10px 12px;
            }
            QTableWidget::item { padding: 8px 12px; border-bottom: 1px solid #f1f5f9; color: #334155; }
            QTableWidget::item:selected { background: #eef2ff; color: #4338ca; }
        """)
        hv = self.table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.Fixed)
        hv.setSectionResizeMode(1, QHeaderView.Fixed)
        hv.setSectionResizeMode(2, QHeaderView.Stretch)
        hv.setSectionResizeMode(3, QHeaderView.Fixed)
        hv.setSectionResizeMode(4, QHeaderView.Stretch)
        hv.setSectionResizeMode(5, QHeaderView.Fixed)
        hv.setSectionResizeMode(6, QHeaderView.Fixed)
        hv.setSectionResizeMode(7, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 130)
        self.table.setColumnWidth(7, 130)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        search = self.search_box.text() if hasattr(self, 'search_box') else ""
        try:
            customers = self.db.get_all(search=search)
            self.current_customers = customers
            self._populate_table(customers)
            self.count_label.setText(f"{len(customers)} khách hàng")
        except Exception as e:
            print(f"Customers refresh error: {e}")

    def _populate_table(self, customers):
        self.table.setRowCount(0)
        loai_colors = {"VIP": "#f59e0b", "Đại lý": "#6366f1", "Thường": "#64748b"}

        for c in customers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 52)

            name_item = QTableWidgetItem(c.get("ten_khach_hang", ""))
            name_item.setForeground(QColor("#0f172a"))
            self.table.setItem(row, 0, name_item)

            self.table.setItem(row, 1, QTableWidgetItem(c.get("so_dien_thoai", "")))
            self.table.setItem(row, 2, QTableWidgetItem(c.get("email", "")))

            loai = c.get("loai_khach_hang", "Thường")
            loai_item = QTableWidgetItem(loai)
            loai_item.setForeground(QColor(loai_colors.get(loai, "#64748b")))
            self.table.setItem(row, 3, loai_item)

            self.table.setItem(row, 4, QTableWidgetItem(c.get("dia_chi", "")))

            don_hang = QTableWidgetItem(str(c.get("so_don_hang", 0)))
            don_hang.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, don_hang)

            tong = c.get("tong_mua_hang", 0)
            tong_item = QTableWidgetItem(f"{tong:,.0f} ₫")
            tong_item.setForeground(QColor("#22c55e"))
            self.table.setItem(row, 6, tong_item)

            # Buttons
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(8, 6, 8, 6)
            btn_l.setSpacing(6)

            edit_btn = QPushButton("✏️ Sửa")
            edit_btn.setFixedHeight(30)
            edit_btn.setStyleSheet("QPushButton { background: #eef2ff; color: #4338ca; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; padding: 0 10px; } QPushButton:hover { background: #e0e7ff; }")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda _, cid=str(c["_id"]): self._edit_customer(cid))

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("QPushButton { background: #fee2e2; color: #dc2626; border: none; border-radius: 6px; } QPushButton:hover { background: #fecaca; }")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect(lambda _, cid=str(c["_id"]), name=c.get("ten_khach_hang", ""): self._delete_customer(cid, name))

            btn_l.addWidget(edit_btn)
            btn_l.addWidget(del_btn)
            self.table.setCellWidget(row, 7, btn_w)

    def _add_customer(self):
        dlg = CustomerDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            try:
                self.db.create(dlg.result_data)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit_customer(self, customer_id):
        try:
            customer = self.db.get_by_id(customer_id)
            dlg = CustomerDialog(self, customer)
            if dlg.exec_() == QDialog.Accepted:
                self.db.update(customer_id, dlg.result_data)
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _delete_customer(self, customer_id, name):
        reply = QMessageBox.question(
            self, "Xác nhận", f"Xóa khách hàng '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete(customer_id)
            self.refresh()

    def _export_excel(self):
        import pandas as pd
        from PyQt5.QtWidgets import QFileDialog, QMessageBox

        if not hasattr(self, 'current_customers') or not self.current_customers:
            QMessageBox.warning(self, "Thông báo", "Không có dữ liệu để xuất!")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo", "Bao_cao_khach_hang_dep.xlsx", "Excel Files (*.xlsx)")
        if not path: return

        try:
            # 1. Chuẩn bị dữ liệu
            df = pd.DataFrame(self.current_customers)
            if '_id' in df.columns: df['_id'] = df['_id'].apply(str)

            mapping = {
                "ten_khach_hang": "Tên Khách Hàng",
                "so_dien_thoai": "Số Điện Thoại",
                "email": "Email",
                "loai_khach_hang": "Loại KH",
                "tong_mua_hang": "Tổng Chi Tiêu",
                "so_don_hang": "Số Đơn",
                "ngay_tao": "Ngày Tham Gia"
            }
            valid_cols = [c for c in mapping.keys() if c in df.columns]
            final_df = df[valid_cols].rename(columns=mapping)

            # 2. Bắt đầu "trang điểm" với XlsxWriter
            writer = pd.ExcelWriter(path, engine='xlsxwriter')
            final_df.to_excel(writer, sheet_name='DanhSach', index=False)

            workbook  = writer.book
            worksheet = writer.sheets['DanhSach']

            # --- Định dạng Tiêu đề (Header) ---
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'vcenter',
                'align': 'center',
                'fg_color': '#6366f1', # Màu tím Indigo giống UI của bạn
                'font_color': 'white',
                'border': 1
            })

            # --- Định dạng Nội dung (Body) ---
            cell_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
            money_format = workbook.add_format({'num_format': '#,##0 "₫"', 'border': 1, 'font_color': '#22c55e'})

            # 3. Áp dụng định dạng và Tự động chỉnh độ rộng cột
            for col_num, value in enumerate(final_df.columns.values):
                # Viết lại tiêu đề với định dạng mới
                worksheet.write(0, col_num, value, header_format)
                
                # Tính độ rộng cột (dựa trên độ dài chữ)
                column_len = max(final_df[value].astype(str).map(len).max(), len(value)) + 2
                
                # Áp dụng định dạng tiền tệ cho cột "Tổng Chi Tiêu"
                if value == "Tổng Chi Tiêu":
                    worksheet.set_column(col_num, col_num, column_len, money_format)
                else:
                    worksheet.set_column(col_num, col_num, column_len, cell_format)

            writer.close() # Quan trọng: Phải đóng writer để lưu file
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo !")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Biến cố: {str(e)}")
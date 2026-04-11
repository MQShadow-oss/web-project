from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QDialog,
    QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit,
    QMessageBox, QAbstractItemView, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QColor, QDrag, QFont
from database.db import ProductDB, CategoryDB
from bson import ObjectId
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QMessageBox

STYLE_INPUT = """
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
        background: #f8fafc;
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #0f172a;
    }
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
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
    QPushButton:pressed { background: #4338ca; }
"""

STYLE_BTN_DANGER = """
    QPushButton {
        background: #fee2e2;
        color: #dc2626;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        padding: 0 16px;
    }
    QPushButton:hover { background: #fecaca; }
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

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.is_edit = product_data is not None
        self.setWindowTitle("Chỉnh sửa sản phẩm" if self.is_edit else "Thêm sản phẩm mới")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if self.is_edit:
            self._fill_data()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog { background: white; }
            QLabel { color: #374151; font-size: 13px; font-weight: 500; }
        """ + STYLE_INPUT)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Title
        title = QLabel("✏️ Chỉnh sửa sản phẩm" if self.is_edit else "➕ Thêm sản phẩm mới")
        title.setStyleSheet("color: #0f172a; font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.ma_sp = QLineEdit()
        self.ma_sp.setPlaceholderText("Ví dụ: SP001")
        form.addRow("Mã sản phẩm *", self.ma_sp)

        self.ten_sp = QLineEdit()
        self.ten_sp.setPlaceholderText("Tên sản phẩm")
        form.addRow("Tên sản phẩm *", self.ten_sp)

        self.danh_muc = QComboBox()
        try:
            cat_db = CategoryDB()
            cats = cat_db.get_names()
            self.danh_muc.addItems(cats)
        except:
            self.danh_muc.addItems(["Điện tử", "Thời trang", "Thực phẩm", "Gia dụng", "Khác"])
        form.addRow("Danh mục", self.danh_muc)

        self.gia_nhap = QDoubleSpinBox()
        self.gia_nhap.setRange(0, 999_999_999)
        self.gia_nhap.setSuffix(" ₫")
        self.gia_nhap.setSingleStep(1000)
        form.addRow("Giá nhập (₫) *", self.gia_nhap)

        self.gia_ban = QDoubleSpinBox()
        self.gia_ban.setRange(0, 999_999_999)
        self.gia_ban.setSuffix(" ₫")
        self.gia_ban.setSingleStep(1000)
        form.addRow("Giá bán (₫) *", self.gia_ban)

        self.so_luong = QSpinBox()
        self.so_luong.setRange(0, 999999)
        form.addRow("Số lượng tồn", self.so_luong)

        self.mo_ta = QTextEdit()
        self.mo_ta.setPlaceholderText("Mô tả sản phẩm...")
        self.mo_ta.setFixedHeight(80)
        form.addRow("Mô tả", self.mo_ta)

        layout.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("💾  Lưu sản phẩm")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _fill_data(self):
        self.ma_sp.setText(self.product_data.get("ma_san_pham", ""))
        self.ten_sp.setText(self.product_data.get("ten_san_pham", ""))
        idx = self.danh_muc.findText(self.product_data.get("danh_muc", ""))
        if idx >= 0:
            self.danh_muc.setCurrentIndex(idx)
        self.gia_nhap.setValue(float(self.product_data.get("gia_nhap", 0)))
        self.gia_ban.setValue(float(self.product_data.get("gia_ban", 0)))
        self.so_luong.setValue(int(self.product_data.get("so_luong_ton", 0)))
        self.mo_ta.setPlainText(self.product_data.get("mo_ta", ""))

    def _save(self):
        if not self.ma_sp.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã sản phẩm!")
            return
        if not self.ten_sp.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên sản phẩm!")
            return

        self.result_data = {
            "ma_san_pham": self.ma_sp.text().strip(),
            "ten_san_pham": self.ten_sp.text().strip(),
            "danh_muc": self.danh_muc.currentText(),
            "gia_nhap": self.gia_nhap.value(),
            "gia_ban": self.gia_ban.value(),
            "so_luong_ton": self.so_luong.value(),
            "mo_ta": self.mo_ta.toPlainText().strip(),
        }
        self.accept()


class DraggableTable(QTableWidget):
    """Table with drag-and-drop row reordering"""
    row_dropped = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._drag_row = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_row = self.rowAt(event.pos().y())
        super().mousePressEvent(event)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.row_dropped.emit()


class ProductsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = ProductDB()
        self.current_products = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("📦 Quản lý sản phẩm")
        title.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 800;")
        add_btn = QPushButton("+ Thêm sản phẩm")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_product)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.export_btn = QPushButton("📊 Xuất Excel")
        self.export_btn.setFixedHeight(40)
        self.export_btn.setStyleSheet(STYLE_BTN_SUCCESS) # Dùng style xanh lá mình đã đưa
        self.export_btn.clicked.connect(self._export_excel)
        header.addWidget(self.export_btn)

        # Filters
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """ + STYLE_INPUT)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(12)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Tìm theo tên hoặc mã sản phẩm...")
        self.search_box.setFixedHeight(38)
        self.search_box.textChanged.connect(self.refresh)

        self.cat_filter = QComboBox()
        self.cat_filter.setFixedHeight(38)
        self.cat_filter.setFixedWidth(160)
        self.cat_filter.addItem("Tất cả")
        try:
            cat_db = CategoryDB()
            self.cat_filter.addItems(cat_db.get_names())
        except:
            pass
        self.cat_filter.currentTextChanged.connect(self.refresh)

        self.count_label = QLabel("0 sản phẩm")
        self.count_label.setStyleSheet("color: #64748b; font-size: 13px;")

        filter_layout.addWidget(self.search_box, 1)
        filter_layout.addWidget(self.cat_filter)
        filter_layout.addWidget(self.count_label)
        layout.addWidget(filter_frame)

        # Drag hint
        hint = QLabel("💡 Kéo thả hàng để sắp xếp thứ tự sản phẩm")
        hint.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic;")
        layout.addWidget(hint)

        # Table
        self.table = DraggableTable(0, 8)
        self.table.setHorizontalHeaderLabels([
            "☰", "Mã SP", "Tên sản phẩm", "Danh mục",
            "Giá nhập", "Giá bán", "Tồn kho", "Thao tác"
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
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f1f5f9;
                color: #334155;
            }
            QTableWidget::item:selected {
                background: #eef2ff;
                color: #4338ca;
            }
            QTableWidget::item:hover {
                background: #f8fafc;
            }
        """)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Fixed)
        header_view.setSectionResizeMode(1, QHeaderView.Fixed)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.Fixed)
        header_view.setSectionResizeMode(4, QHeaderView.Fixed)
        header_view.setSectionResizeMode(5, QHeaderView.Fixed)
        header_view.setSectionResizeMode(6, QHeaderView.Fixed)
        header_view.setSectionResizeMode(7, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 36)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 90)
        self.table.setColumnWidth(7, 160)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setRowHeight(0, 52)

        layout.addWidget(self.table)

    def refresh(self):
        search = self.search_box.text() if hasattr(self, 'search_box') else ""
        category = self.cat_filter.currentText() if hasattr(self, 'cat_filter') else ""
        try:
            products = self.db.get_all(search=search, category=category)
            self.current_products = products
            self._populate_table(products)
            self.count_label.setText(f"{len(products)} sản phẩm")
        except Exception as e:
            print(f"Products refresh error: {e}")

    def _populate_table(self, products):
        self.table.setRowCount(0)
        for i, p in enumerate(products):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 52)

            # Drag handle
            drag_item = QTableWidgetItem("⠿")
            drag_item.setTextAlignment(Qt.AlignCenter)
            drag_item.setForeground(QColor("#cbd5e1"))
            drag_item.setData(Qt.UserRole, str(p["_id"]))
            self.table.setItem(row, 0, drag_item)

            # Data columns
            self.table.setItem(row, 1, QTableWidgetItem(p.get("ma_san_pham", "")))
            self.table.setItem(row, 2, QTableWidgetItem(p.get("ten_san_pham", "")))

            cat_item = QTableWidgetItem(p.get("danh_muc", ""))
            cat_item.setForeground(QColor("#6366f1"))
            self.table.setItem(row, 3, cat_item)

            gia_nhap = f"{p.get('gia_nhap', 0):,.0f} ₫"
            self.table.setItem(row, 4, QTableWidgetItem(gia_nhap))

            gia_ban = f"{p.get('gia_ban', 0):,.0f} ₫"
            gia_item = QTableWidgetItem(gia_ban)
            gia_item.setForeground(QColor("#22c55e"))
            self.table.setItem(row, 5, gia_item)

            # Stock with color
            qty = p.get("so_luong_ton", 0)
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignCenter)
            if qty <= 5:
                qty_item.setForeground(QColor("#ef4444"))
                qty_item.setBackground(QColor("#fee2e2"))
            elif qty <= 10:
                qty_item.setForeground(QColor("#f59e0b"))
                qty_item.setBackground(QColor("#fef3c7"))
            else:
                qty_item.setForeground(QColor("#22c55e"))
            self.table.setItem(row, 6, qty_item)

            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(8, 6, 8, 6)
            btn_layout.setSpacing(6)

            edit_btn = QPushButton("✏️ Sửa")
            edit_btn.setFixedHeight(30)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #eef2ff;
                    color: #4338ca;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 0 10px;
                }
                QPushButton:hover { background: #e0e7ff; }
            """)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda _, pid=str(p["_id"]): self._edit_product(pid))

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("""
                QPushButton {
                    background: #fee2e2;
                    color: #dc2626;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover { background: #fecaca; }
            """)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect(lambda _, pid=str(p["_id"]), name=p.get("ten_san_pham", ""): self._delete_product(pid, name))

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 7, btn_widget)

    def _add_product(self):
        dlg = ProductDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            try:
                self.db.create(dlg.result_data)
                self.refresh()
                QMessageBox.information(self, "Thành công", "Đã thêm sản phẩm mới!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm sản phẩm:\n{str(e)}")

    def _edit_product(self, product_id):
        try:
            product = self.db.get_by_id(product_id)
            dlg = ProductDialog(self, product)
            if dlg.exec_() == QDialog.Accepted:
                self.db.update(product_id, dlg.result_data)
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _delete_product(self, product_id, name):
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa sản phẩm:\n'{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete(product_id)
            self.refresh()
    def _export_excel(self):
        if not hasattr(self, 'current_products') or not self.current_products:
            QMessageBox.warning(self, "Thông báo", "Không có sản phẩm nào để xuất!")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo", "Bao_cao_san_pham.xlsx", "Excel Files (*.xlsx)")
        if not path: return

        try:
            df = pd.DataFrame(self.current_products)
            if '_id' in df.columns: df['_id'] = df['_id'].apply(str)

            # Mapping chuẩn cho Sản phẩm
            mapping = {
                "ma_san_pham": "Mã Sản Phẩm",
                "ten_san_pham": "Tên Máy Tính",
                "danh_muc": "Danh Mục",
                "gia_nhap": "Giá Nhập",
                "gia_ban": "Giá Bán",
                "so_luong_ton": "Tồn Kho"
            }
            valid_cols = [c for c in mapping.keys() if c in df.columns]
            final_df = df[valid_cols].rename(columns=mapping)

            writer = pd.ExcelWriter(path, engine='xlsxwriter')
            final_df.to_excel(writer, sheet_name='KhoHang', index=False)
            workbook = writer.book
            worksheet = writer.sheets['KhoHang']

            # Định dạng
            header_fmt = workbook.add_format({'bold': True, 'align': 'center', 'fg_color': '#6366f1', 'font_color': 'white', 'border': 1})
            cell_fmt = workbook.add_format({'border': 1, 'valign': 'vcenter'})
            money_fmt = workbook.add_format({'num_format': '#,##0 "₫"', 'border': 1})
            stock_fmt = workbook.add_format({'align': 'center', 'border': 1})

            for col_num, value in enumerate(final_df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
                col_len = max(final_df[value].astype(str).map(len).max(), len(value)) + 2
                
                # Áp dụng định dạng tiền cho cột Giá và căn giữa cho Tồn kho
                if value in ["Giá Nhập", "Giá Bán"]:
                    worksheet.set_column(col_num, col_num, col_len, money_fmt)
                elif value == "Tồn Kho":
                    worksheet.set_column(col_num, col_num, col_len, stock_fmt)
                else:
                    worksheet.set_column(col_num, col_num, col_len, cell_fmt)

            writer.close()
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo kho hàng !")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
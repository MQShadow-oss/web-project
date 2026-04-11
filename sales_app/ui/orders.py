from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QMessageBox, QAbstractItemView, QComboBox, QSpinBox,
    QSplitter, QListWidget, QListWidgetItem, QScrollArea,
    QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from database.db import OrderDB, ProductDB, CustomerDB
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import urllib.parse
import requests
from PyQt5.QtGui import QPixmap, QImage

STYLE_INPUT = """
    QLineEdit, QComboBox, QSpinBox {
        background: #f8fafc;
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #0f172a;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
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

STYLE_BTN_SUCCESS = """
    QPushButton {
        background: #22c55e;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        padding: 0 20px;
    }
    QPushButton:hover { background: #16a34a; }
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

class OrderItemRow(QWidget):
    removed = pyqtSignal(str)
    changed = pyqtSignal()

    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        name_lbl = QLabel(self.product.get("ten_san_pham", ""))
        name_lbl.setStyleSheet("font-size: 13px; color: #334155; font-weight: 500;")
        name_lbl.setMinimumWidth(160)

        price_lbl = QLabel(f"{self.product.get('gia_ban', 0):,.0f} ₫")
        price_lbl.setStyleSheet("font-size: 13px; color: #6366f1;")
        price_lbl.setFixedWidth(110)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, self.product.get("so_luong_ton", 999))
        self.qty_spin.setValue(1)
        self.qty_spin.setFixedWidth(70)
        self.qty_spin.setFixedHeight(32)
        self.qty_spin.setStyleSheet(STYLE_INPUT)
        self.qty_spin.valueChanged.connect(self._on_change)

        self.subtotal_lbl = QLabel(f"{self.product.get('gia_ban', 0):,.0f} ₫")
        self.subtotal_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #0f172a;")
        self.subtotal_lbl.setFixedWidth(120)
        self.subtotal_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        rm_btn = QPushButton("✕")
        rm_btn.setFixedSize(28, 28)
        rm_btn.setStyleSheet("""
            QPushButton { background: #fee2e2; color: #dc2626; border: none; border-radius: 6px; font-size: 12px; font-weight: 700; }
            QPushButton:hover { background: #fecaca; }
        """)
        rm_btn.setCursor(Qt.PointingHandCursor)
        rm_btn.clicked.connect(lambda: self.removed.emit(str(self.product["_id"])))

        layout.addWidget(name_lbl, 1)
        layout.addWidget(price_lbl)
        layout.addWidget(self.qty_spin)
        layout.addWidget(self.subtotal_lbl)
        layout.addWidget(rm_btn)

    def _on_change(self):
        total = self.product.get("gia_ban", 0) * self.qty_spin.value()
        self.subtotal_lbl.setText(f"{total:,.0f} ₫")
        self.changed.emit()

    def get_item_data(self):
        return {
            "product_id": str(self.product["_id"]),
            "ma_san_pham": self.product.get("ma_san_pham", ""),
            "ten_san_pham": self.product.get("ten_san_pham", ""),
            "gia_ban": self.product.get("gia_ban", 0),
            "so_luong": self.qty_spin.value(),
            "thanh_tien": self.product.get("gia_ban", 0) * self.qty_spin.value(),
        }


class CreateOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tạo đơn hàng mới")
        self.setMinimumSize(900, 650)
        self.setModal(True)
        self.order_items = {}  # product_id -> OrderItemRow
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        self.setStyleSheet("QDialog { background: #f8fafc; } QLabel { color: #374151; }" + STYLE_INPUT)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left: Product selection
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background: white; border-right: 1px solid #e2e8f0; }")
        left_panel.setFixedWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(12)

        left_title = QLabel("📦 Chọn sản phẩm")
        left_title.setStyleSheet("color: #0f172a; font-size: 16px; font-weight: 700;")
        left_layout.addWidget(left_title)

        self.prod_search = QLineEdit()
        self.prod_search.setPlaceholderText("🔍 Tìm sản phẩm...")
        self.prod_search.setFixedHeight(38)
        self.prod_search.textChanged.connect(self._filter_products)
        left_layout.addWidget(self.prod_search)

        self.prod_list = QListWidget()
        self.prod_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                background: white;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #f1f5f9;
                font-size: 13px;
                color: #334155;
            }
            QListWidget::item:hover { background: #eef2ff; }
            QListWidget::item:selected { background: #eef2ff; color: #4338ca; }
        """)
        self.prod_list.itemDoubleClicked.connect(self._add_product_to_order)
        left_layout.addWidget(self.prod_list)

        add_prod_btn = QPushButton("➕ Thêm vào đơn")
        add_prod_btn.setFixedHeight(40)
        add_prod_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        add_prod_btn.clicked.connect(lambda: self._add_product_to_order(self.prod_list.currentItem()))
        left_layout.addWidget(add_prod_btn)

        layout.addWidget(left_panel)

        # Right: Order details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 20, 24, 20)
        right_layout.setSpacing(14)

        right_title = QLabel("🧾 Chi tiết đơn hàng")
        right_title.setStyleSheet("color: #0f172a; font-size: 16px; font-weight: 700;")
        right_layout.addWidget(right_title)

        # Customer selection
        cust_frame = QFrame()
        cust_frame.setStyleSheet("QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }")
        cust_layout = QFormLayout(cust_frame)
        cust_layout.setContentsMargins(16, 14, 16, 14)
        cust_layout.setSpacing(10)
        cust_layout.setLabelAlignment(Qt.AlignLeft)
        cust_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.cust_combo = QComboBox()
        self.cust_combo.setFixedHeight(36)
        cust_layout.addRow("Khách hàng *", self.cust_combo)

        self.ghi_chu = QLineEdit()
        self.ghi_chu.setPlaceholderText("Ghi chú đơn hàng...")
        self.ghi_chu.setFixedHeight(36)
        cust_layout.addRow("Ghi chú", self.ghi_chu)

        right_layout.addWidget(cust_frame)

        # Items section
        items_label_row = QHBoxLayout()
        items_lbl = QLabel("Sản phẩm trong đơn")
        items_lbl.setStyleSheet("color: #0f172a; font-size: 14px; font-weight: 600;")
        self.items_count = QLabel("(0 sản phẩm)")
        self.items_count.setStyleSheet("color: #94a3b8; font-size: 13px;")
        items_label_row.addWidget(items_lbl)
        items_label_row.addWidget(self.items_count)
        items_label_row.addStretch()
        right_layout.addLayout(items_label_row)

        # Items header
        items_header = QFrame()
        items_header.setStyleSheet("background: #f8fafc; border-radius: 6px;")
        ih_layout = QHBoxLayout(items_header)
        ih_layout.setContentsMargins(12, 8, 12, 8)
        for col in ["Sản phẩm", "Đơn giá", "Số lượng", "Thành tiền", ""]:
            lbl = QLabel(col)
            lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
            ih_layout.addWidget(lbl, 1 if col in ["Sản phẩm", "Thành tiền"] else 0)
        right_layout.addWidget(items_header)

        # Items scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e2e8f0;")
        scroll.setMinimumHeight(200)

        self.items_container = QWidget()
        self.items_container.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 4, 0, 4)
        self.items_layout.setSpacing(0)
        self.items_layout.addStretch()

        scroll.setWidget(self.items_container)
        right_layout.addWidget(scroll)

        # Total section
        total_frame = QFrame()
        total_frame.setStyleSheet("QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }")
        total_layout = QVBoxLayout(total_frame)
        total_layout.setContentsMargins(16, 14, 16, 14)
        total_layout.setSpacing(6)

        subtotal_row = QHBoxLayout()
        subtotal_row.addWidget(QLabel("Tạm tính:"))
        self.subtotal_lbl = QLabel("0 ₫")
        self.subtotal_lbl.setAlignment(Qt.AlignRight)
        subtotal_row.addWidget(self.subtotal_lbl)
        total_layout.addLayout(subtotal_row)

        disc_row = QHBoxLayout()
        disc_row.addWidget(QLabel("Giảm giá:"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setSuffix("%")
        self.discount_spin.setFixedWidth(90)
        self.discount_spin.setFixedHeight(32)
        self.discount_spin.valueChanged.connect(self._update_total)
        disc_row.addStretch()
        disc_row.addWidget(self.discount_spin)
        total_layout.addLayout(disc_row)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #e2e8f0;")
        total_layout.addWidget(div)

        final_row = QHBoxLayout()
        final_lbl = QLabel("TỔNG TIỀN:")
        final_lbl.setStyleSheet("color: #0f172a; font-size: 15px; font-weight: 700;")
        self.total_lbl = QLabel("0 ₫")
        self.total_lbl.setStyleSheet("color: #6366f1; font-size: 18px; font-weight: 800;")
        self.total_lbl.setAlignment(Qt.AlignRight)
        final_row.addWidget(final_lbl)
        final_row.addStretch()
        final_row.addWidget(self.total_lbl)
        total_layout.addLayout(final_row)

        right_layout.addWidget(total_frame)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setFixedHeight(44)
        cancel_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("✅  Tạo đơn hàng")
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet(STYLE_BTN_SUCCESS)
        save_btn.clicked.connect(self._create_order)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        right_layout.addLayout(btn_row)

        layout.addWidget(right_panel)

    def _load_data(self):
        try:
            # Load products
            prod_db = ProductDB()
            self.all_products = prod_db.get_all()
            self._populate_products(self.all_products)

            # Load customers
            cust_db = CustomerDB()
            customers = cust_db.get_all()
            self.cust_combo.clear()
            self.cust_combo.addItem("-- Chọn khách hàng --", None)
            for c in customers:
                self.cust_combo.addItem(
                    f"{c.get('ten_khach_hang', '')} - {c.get('so_dien_thoai', '')}",
                    str(c["_id"])
                )
        except Exception as e:
            print(f"Load data error: {e}")

    def _populate_products(self, products):
        self.prod_list.clear()
        for p in products:
            qty = p.get("so_luong_ton", 0)
            if qty <= 0:
                continue
            item = QListWidgetItem(f"{p.get('ten_san_pham', '')}  |  {p.get('gia_ban', 0):,.0f} ₫  |  Còn: {qty}")
            item.setData(Qt.UserRole, p)
            self.prod_list.addItem(item)

    def _filter_products(self, text):
        filtered = [p for p in self.all_products if text.lower() in p.get("ten_san_pham", "").lower()]
        self._populate_products(filtered)

    def _add_product_to_order(self, list_item):
        if list_item is None:
            return
        product = list_item.data(Qt.UserRole)
        pid = str(product["_id"])

        if pid in self.order_items:
            # Increment qty
            self.order_items[pid].qty_spin.setValue(self.order_items[pid].qty_spin.value() + 1)
            return

        row_widget = OrderItemRow(product)
        row_widget.removed.connect(self._remove_item)
        row_widget.changed.connect(self._update_total)

        # Insert before stretch
        self.items_layout.insertWidget(self.items_layout.count() - 1, row_widget)
        self.order_items[pid] = row_widget
        self._update_total()

    def _remove_item(self, product_id):
        if product_id in self.order_items:
            widget = self.order_items.pop(product_id)
            widget.setParent(None)
            widget.deleteLater()
            self._update_total()

    def _update_total(self):
        subtotal = sum(
            row.product.get("gia_ban", 0) * row.qty_spin.value()
            for row in self.order_items.values()
        )
        discount = self.discount_spin.value() / 100 if hasattr(self, 'discount_spin') else 0
        total = subtotal * (1 - discount)

        if hasattr(self, 'subtotal_lbl'):
            self.subtotal_lbl.setText(f"{subtotal:,.0f} ₫")
            self.total_lbl.setText(f"{total:,.0f} ₫")
            self.items_count.setText(f"({len(self.order_items)} sản phẩm)")

    def _create_order(self):
        if not self.order_items:
            QMessageBox.warning(self, "Lỗi", "Vui lòng thêm ít nhất một sản phẩm!")
            return

        cust_id = self.cust_combo.currentData()
        cust_name = self.cust_combo.currentText().split(" - ")[0] if self.cust_combo.currentIndex() > 0 else "Khách lẻ"

        items = [row.get_item_data() for row in self.order_items.values()]
        subtotal = sum(i["thanh_tien"] for i in items)
        discount = self.discount_spin.value() / 100
        total = subtotal * (1 - discount)

        self.result_data = {
            "khach_hang_id": cust_id,
            "ten_khach_hang": cust_name,
            "ghi_chu": self.ghi_chu.text(),
            "san_pham": items,
            "tam_tinh": subtotal,
            "giam_gia": self.discount_spin.value(),
            "tong_tien": total,
        }
        self.accept()


class OrdersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = OrderDB()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("🧾 Quản lý đơn hàng")
        title.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 800;")
        add_btn = QPushButton("+ Tạo đơn hàng")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._create_order)
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
        filter_frame.setStyleSheet("QFrame { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }" + STYLE_INPUT)
        fl = QHBoxLayout(filter_frame)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(12)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Tìm mã đơn, tên khách hàng...")
        self.search_box.setFixedHeight(38)
        self.search_box.textChanged.connect(self.refresh)

        self.status_filter = QComboBox()
        self.status_filter.setFixedHeight(38)
        self.status_filter.setFixedWidth(150)
        self.status_filter.addItems(["Tất cả", "Chờ xử lý", "Đang xử lý", "Hoàn thành", "Đã hủy"])
        self.status_filter.currentTextChanged.connect(self.refresh)

        self.count_label = QLabel("0 đơn hàng")
        self.count_label.setStyleSheet("color: #64748b; font-size: 13px;")

        fl.addWidget(self.search_box, 1)
        fl.addWidget(self.status_filter)
        fl.addWidget(self.count_label)
        layout.addWidget(filter_frame)

        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Mã đơn hàng", "Khách hàng", "Sản phẩm", "Tạm tính",
            "Giảm giá", "Tổng tiền", "Trạng thái", "Thao tác"
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
        hv.setSectionResizeMode(4, QHeaderView.Fixed)
        hv.setSectionResizeMode(5, QHeaderView.Fixed)
        hv.setSectionResizeMode(6, QHeaderView.Fixed)
        hv.setSectionResizeMode(7, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 90)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 180)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        search = self.search_box.text() if hasattr(self, 'search_box') else ""
        status = self.status_filter.currentText() if hasattr(self, 'status_filter') else ""
        try:
            orders = self.db.get_all(search=search, status=status)
            self.current_orders = orders
            self._populate_table(orders)
            self.count_label.setText(f"{len(orders)} đơn hàng")
        except Exception as e:
            print(f"Orders refresh error: {e}")

    def _populate_table(self, orders):
        self.table.setRowCount(0)
        STATUS_COLORS = {
            "Chờ xử lý": ("#f59e0b", "#fef3c7"),
            "Đang xử lý": ("#3b82f6", "#dbeafe"),
            "Hoàn thành": ("#22c55e", "#dcfce7"),
            "Đã hủy": ("#ef4444", "#fee2e2"),
        }

        for o in orders:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 56)

            ma_item = QTableWidgetItem(o.get("ma_don_hang", ""))
            ma_item.setForeground(QColor("#6366f1"))
            self.table.setItem(row, 0, ma_item)

            self.table.setItem(row, 1, QTableWidgetItem(o.get("ten_khach_hang", "")))

            items = o.get("san_pham", [])
            items_str = ", ".join(i.get("ten_san_pham", "") for i in items[:2])
            if len(items) > 2:
                items_str += f" +{len(items)-2} khác"
            self.table.setItem(row, 2, QTableWidgetItem(items_str))

            tam_tinh = o.get("tam_tinh", o.get("tong_tien", 0))
            self.table.setItem(row, 3, QTableWidgetItem(f"{tam_tinh:,.0f} ₫"))

            giam = o.get("giam_gia", 0)
            giam_item = QTableWidgetItem(f"{giam}%" if giam else "-")
            giam_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, giam_item)

            tong = QTableWidgetItem(f"{o.get('tong_tien', 0):,.0f} ₫")
            tong.setForeground(QColor("#0f172a"))
            self.table.setItem(row, 5, tong)

            # Status badge widget
            status = o.get("trang_thai", "")
            colors = STATUS_COLORS.get(status, ("#64748b", "#f1f5f9"))
            status_w = QWidget()
            sl = QHBoxLayout(status_w)
            sl.setContentsMargins(8, 6, 8, 6)
            st_lbl = QLabel(status)
            st_lbl.setStyleSheet(f"""
                color: {colors[0]};
                background: {colors[1]};
                border-radius: 12px;
                padding: 3px 12px;
                font-size: 12px;
                font-weight: 600;
            """)
            sl.addWidget(st_lbl)
            self.table.setCellWidget(row, 6, status_w)

            # Action: status change + delete
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 4, 4, 4)
            btn_l.setSpacing(4)

            if status != "Hoàn thành" and status != "Đã hủy":
                pay_btn = QPushButton("💰")
                pay_btn.setFixedSize(30, 30) # Để kích thước vuông cho đều với nút xóa
                pay_btn.setToolTip("Xác nhận thanh toán")
                pay_btn.setStyleSheet(STYLE_BTN_SUCCESS) 
                pay_btn.setCursor(Qt.PointingHandCursor)
                pay_btn.clicked.connect(lambda _, oid=str(o["_id"]): self._handle_payment(oid))
                btn_l.addWidget(pay_btn)

            status_combo = QComboBox()
            status_combo.addItems(["Chờ xử lý", "Đang xử lý", "Hoàn thành", "Đã hủy"])
            status_combo.setCurrentText(status)
            status_combo.setFixedHeight(30)
            status_combo.setFixedWidth(130)
            status_combo.setStyleSheet("QComboBox { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px; padding: 0 6px; }")
            status_combo.currentTextChanged.connect(
                lambda new_status, oid=str(o["_id"]): self._update_status(oid, new_status)
            )

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("QPushButton { background: #fee2e2; color: #dc2626; border: none; border-radius: 6px; } QPushButton:hover { background: #fecaca; }")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect(lambda _, oid=str(o["_id"]), ma=o.get("ma_don_hang", ""): self._delete_order(oid, ma))

            btn_l.addWidget(status_combo)
            btn_l.addWidget(del_btn)
            self.table.setCellWidget(row, 7, btn_w)

    def _handle_payment(self, order_id):
        # 1. Lấy thông tin đơn hàng từ danh sách hiện tại
        order = next((o for o in self.current_orders if str(o["_id"]) == order_id), None)
        if not order: return

        # 2. Tạo Link QR (Chỉ lấy đường dẫn, không mở lên)
        amount = order.get("tong_tien", 0)
        content = f"THANH TOAN {order.get('ma_don_hang', 'DH')}"
        qr_url = self.get_qr_link(amount, content)

        # 3. HIỂN THỊ TRỰC TIẾP TRONG APP
        # Thay vì dùng webbrowser, ta gọi hàm show_qr_dialog đã viết ở trên
        # Hàm này trả về QDialog.Accepted khi Sơn bấm "Đã nhận tiền"
        if self.show_qr_dialog(qr_url) == QDialog.Accepted:
            
            # 4. Xác nhận thanh toán vào Database
            if self.db.confirm_payment(order_id):
                QMessageBox.information(self, "Thành công", "Hệ thống đã cập nhật trạng thái đơn và trừ kho!")
                self.refresh() # Load lại bảng để thấy trạng thái mới
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xử lý thanh toán trên hệ thống.")

# Trong class OrdersWidget:
    def get_qr_link(self, amount, content):
        bank_id = "tcb"  # Vietcombank (hoặc mã ngân hàng của Sơn)
        account_no = "7718112006" # Số tài khoản thực của Sơn
        template = "compact2"
        
        # Mã hóa nội dung để tránh lỗi dấu cách/ký tự đặc biệt
        safe_content = urllib.parse.quote(content)
        
        return f"https://img.vietqr.io/image/{bank_id}-{account_no}-{template}.png?amount={int(amount)}&addInfo={safe_content}"
    def show_qr_dialog(self, url):
        dialog = QDialog(self)
        dialog.setWindowTitle("Thanh toán qua Techcombank")
        layout = QVBoxLayout(dialog)
        
        # Tạo nhãn hiển thị trạng thái/ảnh
        label_img = QLabel("🔄 Đang tạo mã QR...")
        label_img.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_img)

        try:
            # Tải ảnh "ngầm" dưới nền, không mở trình duyệt
            response = requests.get(url, timeout=10)
            
            # Biến dữ liệu tải về thành ảnh trong PyQt5
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            # Hiển thị lên giao diện
            label_img.setPixmap(pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            label_img.setText(f"❌ Lỗi kết nối mạng: {e}")

        # Nút bấm để đóng sau khi xác nhận tiền về
        btn = QPushButton("Xác nhận đã nhận tiền")
        btn.setStyleSheet(STYLE_BTN_PRIMARY) # Style tím của Sơn
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn)

        return dialog.exec_()
    def _create_order(self):
        dlg = CreateOrderDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            try:
                order_db = OrderDB()
                result = order_db.create(dlg.result_data)

                # Update product stock & customer stats
                prod_db = ProductDB()
                for item in dlg.result_data.get("san_pham", []):
                    prod_db.update_stock(item["product_id"], -item["so_luong"])

                if dlg.result_data.get("khach_hang_id"):
                    cust_db = CustomerDB()
                    cust_db.update_stats(dlg.result_data["khach_hang_id"], dlg.result_data["tong_tien"])

                self.refresh()
                QMessageBox.information(self, "Thành công", "Đã tạo đơn hàng mới!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tạo đơn hàng:\n{str(e)}")

    def _update_status(self, order_id, new_status):
        try:
            self.db.update_status(order_id, new_status)
        except Exception as e:
            print(f"Update status error: {e}")

    def _delete_order(self, order_id, ma):
        reply = QMessageBox.question(
            self, "Xác nhận", f"Xóa đơn hàng '{ma}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete(order_id)
            self.refresh()
    def _export_excel(self):
        if not hasattr(self, 'current_orders') or not self.current_orders:
            QMessageBox.warning(self, "Thông báo", "Không có đơn hàng nào!")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo", "Bao_cao_doanh_thu.xlsx", "Excel Files (*.xlsx)")
        if not path: return

        try:
            df = pd.DataFrame(self.current_orders)
            if '_id' in df.columns: df['_id'] = df['_id'].apply(str)

            mapping = {
                "ma_don_hang": "Mã Đơn",
                "ten_khach_hang": "Khách Hàng",
                "tong_tien": "Tổng Thanh Toán",
                "trang_thai": "Trạng Thái",
                "ngay_tao": "Ngày Lập Đơn"
            }
            valid_cols = [c for c in mapping.keys() if c in df.columns]
            final_df = df[valid_cols].rename(columns=mapping)

            # Định dạng lại ngày tháng để Pandas không làm hỏng
            if "Ngày Lập Đơn" in final_df.columns:
                final_df["Ngày Lập Đơn"] = pd.to_datetime(final_df["Ngày Lập Đơn"]).dt.strftime('%d/%m/%Y %H:%M')

            writer = pd.ExcelWriter(path, engine='xlsxwriter')
            final_df.to_excel(writer, sheet_name='DoanhThu', index=False)
            workbook = writer.book
            worksheet = writer.sheets['DoanhThu']

            header_fmt = workbook.add_format({'bold': True, 'align': 'center', 'fg_color': '#10b981', 'font_color': 'white', 'border': 1})
            cell_fmt = workbook.add_format({'border': 1})
            money_fmt = workbook.add_format({'num_format': '#,##0 "₫"', 'border': 1, 'bold': True})
            status_fmt = workbook.add_format({'align': 'center', 'border': 1})

            for col_num, value in enumerate(final_df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
                col_len = max(final_df[value].astype(str).map(len).max(), len(value)) + 3
                
                if value == "Tổng Thanh Toán":
                    worksheet.set_column(col_num, col_num, col_len, money_fmt)
                elif value == "Trạng Thái":
                    worksheet.set_column(col_num, col_num, col_len, status_fmt)
                else:
                    worksheet.set_column(col_num, col_num, col_len, cell_fmt)

            writer.close()
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo doanh thu thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
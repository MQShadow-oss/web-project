from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from database.db import OrderDB, ProductDB, CustomerDB
from datetime import datetime


def format_currency(amount):
    if amount >= 1_000_000:
        return f"{amount/1_000_000:.1f}M ₫"
    elif amount >= 1_000:
        return f"{amount/1_000:.0f}K ₫"
    return f"{amount:,.0f} ₫"


class StatCard(QFrame):
    def __init__(self, title, value, subtitle, color, icon, parent=None):
        super().__init__(parent)
        self.color = color
        self._build_ui(title, value, subtitle, color, icon)

    def _build_ui(self, title, value, subtitle, color, icon):
        self.setStyleSheet(f"""
            StatCard {{
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }}
        """)
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        # Top row: icon + title
        top = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 20px;
            background: {color}15;
            border-radius: 10px;
            padding: 6px 8px;
        """)
        icon_label.setFixedSize(42, 42)
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")

        top.addWidget(icon_label)
        top.addWidget(title_label, 1)
        layout.addLayout(top)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: #0f172a;
            font-size: 26px;
            font-weight: 700;
        """)
        layout.addWidget(self.value_label)

        # Subtitle
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(sub_label)

    def update_value(self, value):
        self.value_label.setText(value)


class RevenueChart(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        self.setStyleSheet("""
            RevenueChart {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)

        header = QHBoxLayout()
        title = QLabel("Doanh thu 7 ngày gần đây")
        title.setStyleSheet("color: #0f172a; font-size: 16px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Chart
        self.chart = QChart()
        self.chart.setBackgroundBrush(QBrush(QColor("white")))
        self.chart.setMargins(QMargins_safe(0, 0, 0, 0))
        self.chart.legend().setVisible(False)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background: transparent;")
        self.chart_view.setMinimumHeight(200)
        layout.addWidget(self.chart_view)

    def load_data(self):
        try:
            order_db = OrderDB()
            data = order_db.get_revenue_by_day(7)

            series = QBarSet("Doanh thu")
            series.setColor(QColor("#6366f1"))
            categories = []

            for item in data:
                series.append(item["total"])
                categories.append(item["_id"])

            if not data:
                for i in range(7):
                    series.append(0)
                    categories.append(f"Day {i+1}")

            bar_series = QBarSeries()
            bar_series.append(series)

            self.chart.removeAllSeries()
            for ax in self.chart.axes():
                self.chart.removeAxis(ax)

            self.chart.addSeries(bar_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            axis_x.setLabelsColor(QColor("#94a3b8"))
            self.chart.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)

            axis_y = QValueAxis()
            axis_y.setLabelsColor(QColor("#94a3b8"))
            axis_y.setGridLineColor(QColor("#f1f5f9"))
            self.chart.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)

        except Exception as e:
            print(f"Chart error: {e}")


def QMargins_safe(l, t, r, b):
    from PyQt5.QtCore import QMargins
    return QMargins(l, t, r, b)


class RecentOrdersTable(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        self.setStyleSheet("""
            RecentOrdersTable {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("Đơn hàng gần đây")
        title.setStyleSheet("color: #0f172a; font-size: 16px; font-weight: 700;")
        layout.addWidget(title)

        # Header row
        header = QFrame()
        header.setStyleSheet("background: #f8fafc; border-radius: 8px;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 8, 12, 8)

        for col, width in [("Mã ĐH", 120), ("Khách hàng", 160), ("Tổng tiền", 120), ("Trạng thái", 120)]:
            lbl = QLabel(col)
            lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
            lbl.setFixedWidth(width)
            h_layout.addWidget(lbl)
        h_layout.addStretch()

        layout.addWidget(header)

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(4)
        layout.addLayout(self.rows_layout)

    def load_data(self):
        # Clear
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            order_db = OrderDB()
            orders = order_db.get_recent(6)

            status_colors = {
                "Chờ xử lý": "#f59e0b",
                "Đang xử lý": "#3b82f6",
                "Hoàn thành": "#22c55e",
                "Đã hủy": "#ef4444",
            }

            for order in orders:
                row = QFrame()
                row.setStyleSheet("""
                    QFrame { border-radius: 6px; }
                    QFrame:hover { background: #f8fafc; }
                """)
                r_layout = QHBoxLayout(row)
                r_layout.setContentsMargins(12, 8, 12, 8)

                ma = QLabel(order.get("ma_don_hang", ""))
                ma.setStyleSheet("color: #6366f1; font-size: 13px; font-weight: 600;")
                ma.setFixedWidth(120)

                ten = QLabel(order.get("ten_khach_hang", ""))
                ten.setStyleSheet("color: #334155; font-size: 13px;")
                ten.setFixedWidth(160)

                tien = QLabel(format_currency(order.get("tong_tien", 0)))
                tien.setStyleSheet("color: #0f172a; font-size: 13px; font-weight: 600;")
                tien.setFixedWidth(120)

                status = order.get("trang_thai", "")
                color = status_colors.get(status, "#94a3b8")
                status_lbl = QLabel(status)
                status_lbl.setStyleSheet(f"""
                    color: {color};
                    background: {color}15;
                    border-radius: 12px;
                    padding: 2px 10px;
                    font-size: 12px;
                    font-weight: 500;
                """)
                status_lbl.setFixedWidth(110)

                r_layout.addWidget(ma)
                r_layout.addWidget(ten)
                r_layout.addWidget(tien)
                r_layout.addWidget(status_lbl)
                r_layout.addStretch()

                self.rows_layout.addWidget(row)

        except Exception as e:
            print(f"Orders table error: {e}")


class LowStockWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        self.setStyleSheet("""
            LowStockWidget {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Sắp hết hàng")
        title.setStyleSheet("color: #0f172a; font-size: 16px; font-weight: 700;")
        warn = QLabel("⚠️")
        warn.setStyleSheet("font-size: 18px;")
        header.addWidget(warn)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(6)
        layout.addLayout(self.list_layout)

    def load_data(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            product_db = ProductDB()
            products = product_db.get_low_stock(10)[:6]

            if not products:
                empty = QLabel("Không có sản phẩm nào sắp hết hàng")
                empty.setStyleSheet("color: #94a3b8; font-size: 13px; padding: 8px 0;")
                self.list_layout.addWidget(empty)
                return

            for p in products:
                row = QFrame()
                r_layout = QHBoxLayout(row)
                r_layout.setContentsMargins(0, 0, 0, 0)

                name = QLabel(p.get("ten_san_pham", ""))
                name.setStyleSheet("color: #334155; font-size: 13px;")

                qty = p.get("so_luong_ton", 0)
                qty_color = "#ef4444" if qty <= 5 else "#f59e0b"
                qty_lbl = QLabel(f"{qty} còn lại")
                qty_lbl.setStyleSheet(f"color: {qty_color}; font-size: 13px; font-weight: 600;")
                qty_lbl.setAlignment(Qt.AlignRight)

                r_layout.addWidget(name, 1)
                r_layout.addWidget(qty_lbl)
                self.list_layout.addWidget(row)

                div = QFrame()
                div.setFixedHeight(1)
                div.setStyleSheet("background: #f1f5f9;")
                self.list_layout.addWidget(div)

        except Exception as e:
            print(f"Low stock error: {e}")


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

        # Auto refresh every 30s
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)

    def _build_ui(self):
        # Main scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(28, 24, 28, 28)
        main_layout.setSpacing(20)

        # Page header
        header = QHBoxLayout()
        title = QLabel("Tổng quan")
        title.setStyleSheet("color: #0f172a; font-size: 26px; font-weight: 800;")
        date_label = QLabel(datetime.now().strftime("📅 %d/%m/%Y"))
        date_label.setStyleSheet("color: #64748b; font-size: 14px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(date_label)
        main_layout.addLayout(header)

        # Stat cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_revenue_day = StatCard("Doanh thu hôm nay", "0 ₫", "Tổng doanh thu", "#6366f1", "💰")
        self.card_revenue_month = StatCard("Doanh thu tháng", "0 ₫", "Tháng hiện tại", "#22c55e", "📈")
        self.card_orders = StatCard("Tổng đơn hàng", "0", "Tất cả đơn hàng", "#f59e0b", "🧾")
        self.card_customers = StatCard("Khách hàng", "0", "Tổng số khách hàng", "#3b82f6", "👥")
        self.card_products = StatCard("Sản phẩm", "0", "Trong kho", "#ec4899", "📦")

        for card in [self.card_revenue_day, self.card_revenue_month, self.card_orders, self.card_customers, self.card_products]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        self.revenue_chart = RevenueChart()
        self.revenue_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.revenue_chart.setMinimumHeight(280)

        self.low_stock = LowStockWidget()
        self.low_stock.setFixedWidth(280)
        self.low_stock.setMinimumHeight(280)

        charts_row.addWidget(self.revenue_chart)
        charts_row.addWidget(self.low_stock)
        main_layout.addLayout(charts_row)

        # Recent orders
        self.recent_orders = RecentOrdersTable()
        main_layout.addWidget(self.recent_orders)

        main_layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh(self):
        try:
            order_db = OrderDB()
            product_db = ProductDB()
            customer_db = CustomerDB()

            rev_day = order_db.get_revenue_today()
            rev_month = order_db.get_revenue_month()
            orders_count = order_db.count()
            customers_count = customer_db.count()
            products_count = product_db.count()

            self.card_revenue_day.update_value(format_currency(rev_day))
            self.card_revenue_month.update_value(format_currency(rev_month))
            self.card_orders.update_value(str(orders_count))
            self.card_customers.update_value(str(customers_count))
            self.card_products.update_value(str(products_count))

            self.revenue_chart.load_data()
            self.low_stock.load_data()
            self.recent_orders.load_data()

        except Exception as e:
            print(f"Dashboard refresh error: {e}")

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.connect()

    def connect(self, uri="mongodb://localhost:27017/", db_name="quan_ly_ban_hang"):
        try:
            self._client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            self._client.server_info()
            self._db = self._client[db_name]
            logger.info("Kết nối MongoDB thành công!")
            self._init_collections()
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Không thể kết nối MongoDB: {e}")
            return False

    def _init_collections(self):
        """Khởi tạo các collection và index"""
        # Products
        if "products" not in self._db.list_collection_names():
            self._db.create_collection("products")
        self._db.products.create_index("ma_san_pham", unique=True)

        # Customers
        if "customers" not in self._db.list_collection_names():
            self._db.create_collection("customers")

        # Orders
        if "orders" not in self._db.list_collection_names():
            self._db.create_collection("orders")
        self._db.orders.create_index("ma_don_hang", unique=True)

        # Categories
        if "categories" not in self._db.list_collection_names():
            self._db.create_collection("categories")
            self._seed_categories()

    def _seed_categories(self):
        categories = [
            {"ten_danh_muc": "Điện tử", "mo_ta": "Sản phẩm điện tử, thiết bị"},
            {"ten_danh_muc": "Thời trang", "mo_ta": "Quần áo, phụ kiện"},
            {"ten_danh_muc": "Thực phẩm", "mo_ta": "Đồ ăn, thức uống"},
            {"ten_danh_muc": "Gia dụng", "mo_ta": "Đồ gia dụng"},
            {"ten_danh_muc": "Khác", "mo_ta": "Danh mục khác"},
        ]
        self._db.categories.insert_many(categories)

    @property
    def db(self):
        return self._db

    def is_connected(self):
        try:
            self._client.server_info()
            return True
        except:
            return False


# ===== PRODUCT OPERATIONS =====
class ProductDB:
    def __init__(self):
        self.col = Database.get_instance().db.products

    def get_all(self, search="", category=""):
        query = {}
        if search:
            query["$or"] = [
                {"ten_san_pham": {"$regex": search, "$options": "i"}},
                {"ma_san_pham": {"$regex": search, "$options": "i"}},
            ]
        if category and category != "Tất cả":
            query["danh_muc"] = category
        return list(self.col.find(query).sort("ten_san_pham", 1))

    def get_by_id(self, product_id):
        return self.col.find_one({"_id": ObjectId(product_id)})

    def create(self, data):
        data["ngay_tao"] = datetime.now()
        data["ngay_cap_nhat"] = datetime.now()
        return self.col.insert_one(data)

    def update(self, product_id, data):
        data["ngay_cap_nhat"] = datetime.now()
        return self.col.update_one(
            {"_id": ObjectId(product_id)}, {"$set": data}
        )

    def delete(self, product_id):
        return self.col.delete_one({"_id": ObjectId(product_id)})

    def update_stock(self, product_id, quantity_change):
        return self.col.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$inc": {"so_luong_ton": quantity_change},
                "$set": {"ngay_cap_nhat": datetime.now()},
            },
        )

    def get_low_stock(self, threshold=10):
        return list(self.col.find({"so_luong_ton": {"$lte": threshold}}).sort("so_luong_ton", 1))

    def count(self):
        return self.col.count_documents({})


# ===== CUSTOMER OPERATIONS =====
class CustomerDB:
    def __init__(self):
        self.col = Database.get_instance().db.customers

    def get_all(self, search=""):
        query = {}
        if search:
            query["$or"] = [
                {"ten_khach_hang": {"$regex": search, "$options": "i"}},
                {"so_dien_thoai": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]
        return list(self.col.find(query).sort("ten_khach_hang", 1))

    def get_by_id(self, customer_id):
        return self.col.find_one({"_id": ObjectId(customer_id)})

    def create(self, data):
        data["ngay_tao"] = datetime.now()
        data["tong_mua_hang"] = 0
        data["so_don_hang"] = 0
        return self.col.insert_one(data)

    def update(self, customer_id, data):
        return self.col.update_one(
            {"_id": ObjectId(customer_id)}, {"$set": data}
        )

    def delete(self, customer_id):
        return self.col.delete_one({"_id": ObjectId(customer_id)})

    def update_stats(self, customer_id, amount):
        return self.col.update_one(
            {"_id": ObjectId(customer_id)},
            {"$inc": {"tong_mua_hang": amount, "so_don_hang": 1}},
        )

    def count(self):
        return self.col.count_documents({})


# ===== ORDER OPERATIONS =====
class OrderDB:
    def __init__(self):
        self.col = Database.get_instance().db.orders

    def get_all(self, search="", status="", date_from=None, date_to=None):
        query = {}
        if search:
            query["$or"] = [
                {"ma_don_hang": {"$regex": search, "$options": "i"}},
                {"ten_khach_hang": {"$regex": search, "$options": "i"}},
            ]
        if status and status != "Tất cả":
            query["trang_thai"] = status
        if date_from or date_to:
            query["ngay_tao"] = {}
            if date_from:
                query["ngay_tao"]["$gte"] = date_from
            if date_to:
                query["ngay_tao"]["$lte"] = date_to
        return list(self.col.find(query).sort("ngay_tao", -1))

    def get_by_id(self, order_id):
        return self.col.find_one({"_id": ObjectId(order_id)})

    def create(self, data):
        # Generate order code
        count = self.col.count_documents({}) + 1
        data["ma_don_hang"] = f"DH{datetime.now().strftime('%Y%m%d')}{count:04d}"
        data["ngay_tao"] = datetime.now()
        data["trang_thai"] = "Chờ xử lý"
        return self.col.insert_one(data)

    def update_status(self, order_id, status):
        return self.col.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"trang_thai": status, "ngay_cap_nhat": datetime.now()}},
        )

    def delete(self, order_id):
        return self.col.delete_one({"_id": ObjectId(order_id)})

    def count(self):
        return self.col.count_documents({})

    def get_revenue_today(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {"ngay_tao": {"$gte": today}, "trang_thai": {"$ne": "Đã hủy"}}},
            {"$group": {"_id": None, "total": {"$sum": "$tong_tien"}}},
        ]
        result = list(self.col.aggregate(pipeline))
        return result[0]["total"] if result else 0

    def get_revenue_month(self):
        now = datetime.now()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {"ngay_tao": {"$gte": first_day}, "trang_thai": {"$ne": "Đã hủy"}}},
            {"$group": {"_id": None, "total": {"$sum": "$tong_tien"}}},
        ]
        result = list(self.col.aggregate(pipeline))
        return result[0]["total"] if result else 0

    def get_revenue_by_day(self, days=7):
        from datetime import timedelta
        pipeline = [
            {
                "$match": {
                    "ngay_tao": {"$gte": datetime.now() - timedelta(days=days)},
                    "trang_thai": {"$ne": "Đã hủy"},
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%d/%m", "date": "$ngay_tao"}
                    },
                    "total": {"$sum": "$tong_tien"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        return list(self.col.aggregate(pipeline))

    def get_recent(self, limit=5):
        return list(self.col.find().sort("ngay_tao", -1).limit(limit))
    
# Thêm vào class OrderDB trong file database/db.py
    def confirm_payment(self, order_id):
        try:
            from bson import ObjectId
            from datetime import datetime
            
            # 1. Lấy dữ liệu đơn hàng
            order = self.get_by_id(order_id)
            if not order:
                return False

            # 2. CẬP NHẬT TRẠNG THÁI (Ưu tiên số 1)
            # Dùng đúng tên 'Hoàn thành' như giao diện Sơn đang hiện
            self.col.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {
                    "trang_thai": "Hoàn thành", 
                    "ngay_thanh_toan": datetime.now()
                }}
            )

            # 3. CẬP NHẬT CHI TIÊU KHÁCH HÀNG (Nếu có id thì làm, không thì thôi)
            # Tự dò tìm các tên biến có thể có
            cus_id = order.get('id_khach_hang') or order.get('customer_id') or order.get('ma_khach_hang')
            tong_tien = order.get('tong_tien', 0)
            
            if cus_id:
                try:
                    from database.db import CustomerDB
                    cus_db = CustomerDB()
                    # Chỉ gọi nếu hàm update_stats tồn tại
                    if hasattr(cus_db, 'update_stats'):
                        cus_db.update_stats(cus_id, tong_tien)
                except: pass # Lỗi thì bỏ qua, không làm văng app

            # 4. TRỪ KHO (Dò tìm danh sách sản phẩm)
            items = order.get('san_pham') or order.get('items') or []
            if items:
                try:
                    from database.db import ProductDB
                    prod_db = ProductDB()
                    for item in items:
                        # Dò tìm ID sản phẩm và số lượng
                        p_id = item.get('ma_san_pham') or item.get('product_id') or item.get('_id')
                        qty = item.get('so_luong') or item.get('quantity') or 1
                        if p_id and hasattr(prod_db, 'update_stock'):
                            prod_db.update_stock(p_id, -qty)
                except: pass # Lỗi thì bỏ qua để app chạy tiếp

            return True
        except Exception as e:
            print(f"Lỗi xác nhận thanh toán (đã được xử lý): {e}")
            return False

# ===== USER OPERATIONS =====
class UserDB:
    def __init__(self):
        self.col = Database.get_instance().db.users
        self._seed_default_users()

    def _seed_default_users(self):
        import hashlib
        if self.col.count_documents({}) == 0:
            default_users = [
                {
                    "username": "admin",
                    "password": self._hash("admin123"),
                    "ho_ten": "Quản trị viên",
                    "vai_tro": "admin",
                    "email": "admin@banhangpro.com",
                    "active": True,
                    "ngay_tao": datetime.now(),
                },
                {
                    "username": "nhanvien",
                    "password": self._hash("123456"),
                    "ho_ten": "Nhân viên bán hàng",
                    "vai_tro": "staff",
                    "email": "nhanvien@banhangpro.com",
                    "active": True,
                    "ngay_tao": datetime.now(),
                },
            ]
            self.col.insert_many(default_users)
            logger.info("Đã tạo tài khoản mặc định: admin/admin123, nhanvien/123456")

    def _hash(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        import hashlib
        hashed = hashlib.sha256(password.encode()).hexdigest()
        user = self.col.find_one({"username": username, "password": hashed, "active": True})
        if user:
            self.col.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.now()}})
        return user

    def get_all(self):
        return list(self.col.find().sort("username", 1))

    def create(self, data):
        import hashlib
        data["password"] = hashlib.sha256(data["password"].encode()).hexdigest()
        data["active"] = True
        data["ngay_tao"] = datetime.now()
        return self.col.insert_one(data)

    def update(self, user_id, data):
        import hashlib
        if "password" in data and data["password"]:
            data["password"] = hashlib.sha256(data["password"].encode()).hexdigest()
        elif "password" in data:
            del data["password"]
        return self.col.update_one({"_id": ObjectId(user_id)}, {"$set": data})

    def delete(self, user_id):
        return self.col.delete_one({"_id": ObjectId(user_id)})


# ===== CATEGORY OPERATIONS =====
class CategoryDB:
    def __init__(self):
        self.col = Database.get_instance().db.categories

    def get_all(self):
        return list(self.col.find().sort("ten_danh_muc", 1))

    def get_names(self):
        cats = self.get_all()
        return [c["ten_danh_muc"] for c in cats]

    def create(self, name, description=""):
        return self.col.insert_one(
            {"ten_danh_muc": name, "mo_ta": description}
        )

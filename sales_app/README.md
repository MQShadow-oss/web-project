# 🛍️ QuanLyBanHang Pro

Phần mềm quản lý bán hàng bằng Python, PyQt5 và MongoDB.

## ✅ Tính năng

- **Tổng quan (Dashboard)**: Thống kê doanh thu, biểu đồ, đơn hàng gần đây, sản phẩm sắp hết
- **Quản lý sản phẩm**: Thêm, sửa, xóa, tìm kiếm, lọc danh mục. Kéo thả để sắp xếp thứ tự
- **Quản lý khách hàng**: CRUD khách hàng, phân loại VIP/Thường/Đại lý
- **Quản lý đơn hàng**: Tạo đơn hàng với giao diện trực quan, cập nhật trạng thái, giảm giá
- **MongoDB**: Lưu trữ toàn bộ dữ liệu với các collection tối ưu

## 📋 Yêu cầu

- Python 3.8+
- MongoDB Community Server (chạy trên localhost:27017)
- Các thư viện trong requirements.txt

## 🚀 Cài đặt & Chạy

### 1. Cài MongoDB
- Tải và cài từ: https://www.mongodb.com/try/download/community
- Đảm bảo MongoDB đang chạy (`mongod`)

### 2. Cài thư viện Python
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python main.py
```

## 📁 Cấu trúc thư mục

```
sales_app/
├── main.py                 # Điểm khởi chạy
├── requirements.txt
├── database/
│   ├── __init__.py
│   └── db.py              # Kết nối & thao tác MongoDB
└── ui/
    ├── __init__.py
    ├── main_window.py     # Cửa sổ chính + sidebar
    ├── dashboard.py       # Màn hình tổng quan
    ├── products.py        # Quản lý sản phẩm (drag & drop)
    ├── customers.py       # Quản lý khách hàng
    └── orders.py          # Quản lý đơn hàng
```

## 🗄️ Cơ sở dữ liệu MongoDB

**Database**: `quan_ly_ban_hang`

- **products**: Sản phẩm (mã, tên, danh mục, giá nhập, giá bán, tồn kho)
- **customers**: Khách hàng (tên, SĐT, email, địa chỉ, loại)
- **orders**: Đơn hàng (mã, khách hàng, sản phẩm, tổng tiền, trạng thái)
- **categories**: Danh mục sản phẩm

## 💡 Hướng dẫn sử dụng

1. **Thêm danh mục & sản phẩm** trước khi tạo đơn hàng
2. **Thêm khách hàng** để liên kết với đơn hàng
3. **Tạo đơn hàng**: Double-click sản phẩm để thêm vào đơn
4. **Kéo thả** hàng trong bảng sản phẩm để sắp xếp
5. **Cập nhật trạng thái** đơn hàng trực tiếp từ dropdown

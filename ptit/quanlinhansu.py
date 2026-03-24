import csv
import os

# Đường dẫn file CSV
FILE_PATH = "nhan_su.csv"

# Lớp nhân viên
class NhanVien:
    def __init__(self, id, ten, tuoi, phong_ban, luong):
        self.id = id
        self.ten = ten
        self.tuoi = tuoi
        self.phong_ban = phong_ban
        self.luong = luong

    def hien_thi(self):
        print(f"ID: {self.id}, Tên: {self.ten}, Tuổi: {self.tuoi}, Phòng ban: {self.phong_ban}, Lương: {self.luong}")

# Lớp quản lý nhân sự
class QuanLyNhanSu:
    def __init__(self):
        self.nhan_su = []
        self.load_data()

    # Load dữ liệu từ file CSV
    def load_data(self):
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nv = NhanVien(int(row['ID']), row['Ten'], int(row['Tuoi']), row['PhongBan'], float(row['Luong']))
                    self.nhan_su.append(nv)

    # Lưu dữ liệu vào CSV
    def save_data(self):
        with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['ID', 'Ten', 'Tuoi', 'PhongBan', 'Luong']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for nv in self.nhan_su:
                writer.writerow({
                    'ID': nv.id,
                    'Ten': nv.ten,
                    'Tuoi': nv.tuoi,
                    'PhongBan': nv.phong_ban,
                    'Luong': nv.luong
                })

    # Thêm nhân viên
    def them_nhan_vien(self):
        id = 1 if not self.nhan_su else self.nhan_su[-1].id + 1
        ten = input("Nhập tên: ")
        tuoi = int(input("Nhập tuổi: "))
        phong_ban = input("Nhập phòng ban: ")
        luong = float(input("Nhập lương: "))
        nv = NhanVien(id, ten, tuoi, phong_ban, luong)
        self.nhan_su.append(nv)
        self.save_data()
        print("Đã thêm nhân viên!")

    # Hiển thị danh sách
    def hien_thi_danh_sach(self):
        if not self.nhan_su:
            print("Chưa có nhân viên nào.")
            return
        print("\n--- Danh sách nhân viên ---")
        for nv in self.nhan_su:
            nv.hien_thi()

    # Tìm nhân viên
    def tim_nhan_vien(self):
        tim = input("Nhập tên hoặc ID nhân viên: ")
        ket_qua = []
        if tim.isdigit():
            ket_qua = [nv for nv in self.nhan_su if nv.id == int(tim)]
        else:
            ket_qua = [nv for nv in self.nhan_su if tim.lower() in nv.ten.lower()]
        if ket_qua:
            for nv in ket_qua:
                nv.hien_thi()
        else:
            print("Không tìm thấy nhân viên.")

    # Sửa thông tin nhân viên
    def sua_nhan_vien(self):
        id = int(input("Nhập ID nhân viên muốn sửa: "))
        nv_list = [nv for nv in self.nhan_su if nv.id == id]
        if nv_list:
            nv = nv_list[0]
            nv.ten = input(f"Tên ({nv.ten}): ") or nv.ten
            nv.tuoi = int(input(f"Tuổi ({nv.tuoi}): ") or nv.tuoi)
            nv.phong_ban = input(f"Phòng ban ({nv.phong_ban}): ") or nv.phong_ban
            nv.luong = float(input(f"Lương ({nv.luong}): ") or nv.luong)
            self.save_data()
            print("Đã cập nhật thông tin nhân viên!")
        else:
            print("Không tìm thấy ID nhân viên.")

    # Xóa nhân viên
    def xoa_nhan_vien(self):
        id = int(input("Nhập ID nhân viên muốn xóa: "))
        nv_list = [nv for nv in self.nhan_su if nv.id == id]
        if nv_list:
            self.nhan_su.remove(nv_list[0])
            self.save_data()
            print("Đã xóa nhân viên!")
        else:
            print("Không tìm thấy ID nhân viên.")

    # Tính tổng lương
    def tong_luong(self):
        tong = sum(nv.luong for nv in self.nhan_su)
        print(f"Tổng lương hiện tại: {tong}")

# Menu chính
def menu():
    qlns = QuanLyNhanSu()
    while True:
        print("\n--- Quản lý nhân sự ---")
        print("1. Thêm nhân viên")
        print("2. Hiển thị danh sách nhân viên")
        print("3. Tìm nhân viên")
        print("4. Sửa thông tin nhân viên")
        print("5. Xóa nhân viên")
        print("6. Tính tổng lương")
        print("7. Thoát")
        lua_chon = input("Chọn chức năng: ")
        if lua_chon == "1":
            qlns.them_nhan_vien()
        elif lua_chon == "2":
            qlns.hien_thi_danh_sach()
        elif lua_chon == "3":
            qlns.tim_nhan_vien()
        elif lua_chon == "4":
            qlns.sua_nhan_vien()
        elif lua_chon == "5":
            qlns.xoa_nhan_vien()
        elif lua_chon == "6":
            qlns.tong_luong()
        elif lua_chon == "7":
            print("Thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    menu()
# =========================
# 📁 1. main.py
# =========================
from database.models import init_db
from services.product_service import *
from services.auth_service import *

init_db()

# LOGIN
while True:
    print("""
==== LOGIN ====
1. Login
2. Register
0. Exit
""")

    c = input("Choose: ")

    if c == '1':
        u = input("Username: ")
        p = input("Password: ")
        if login(u, p):
            print("✅ Login success")
            break
        else:
            print("❌ Wrong account")

    elif c == '2':
        register(input("Username: "), input("Password: "))

    elif c == '0':
        exit()

# MENU CHÍNH
while True:
    print("""
==== WAREHOUSE MANAGER ====
1. Add product
2. Show products
3. Import goods
4. Export goods
5. Delete product
6. Stats
0. Exit
""")

    choice = input("Choose: ")

    if choice == '1':
        add_product(input("Name: "), int(input("Qty: ")), float(input("Price: ")))

    elif choice == '2':
        for p in get_products(): print(p)

    elif choice == '3':
        import_goods(int(input("ID: ")), int(input("Amount: ")))

    elif choice == '4':
        export_goods(int(input("ID: ")), int(input("Amount: ")))

    elif choice == '5':
        delete_product(int(input("ID: ")))

    elif choice == '6':
        print(stats())

    elif choice == '0': break


# =========================
# 📁 2. database/db.py
# =========================
import sqlite3

def get_connection():
    return sqlite3.connect("warehouse.db")


# =========================
# 📁 3. database/models.py
# =========================
from database.db import get_connection

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        quantity INTEGER,
        price REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        type TEXT,
        amount INTEGER
    )''')

    conn.commit()
    conn.close()


# =========================
# 📁 4. services/auth_service.py
# =========================
from database.db import get_connection

def register(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (username, password))
        conn.commit()
        print("✅ Register success")
    except:
        print("❌ Username exists")
    conn.close()


def login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None


# =========================
# 📁 5. services/product_service.py
# =========================
from database.db import get_connection

def add_product(name, quantity, price):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO products VALUES (NULL, ?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()


def get_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    data = c.fetchall()
    conn.close()
    return data


def delete_product(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()


def import_goods(id, amount):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE products SET quantity = quantity + ? WHERE id=?", (amount, id))
    c.execute("INSERT INTO history VALUES (NULL, ?, 'import', ?)", (id, amount))
    conn.commit()
    conn.close()


def export_goods(id, amount):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT quantity FROM products WHERE id=?", (id,))
    result = c.fetchone()

    if not result:
        print("❌ Not found")
        return

    if result[0] < amount:
        print("❌ Not enough")
        return

    c.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (amount, id))
    c.execute("INSERT INTO history VALUES (NULL, ?, 'export', ?)", (id, amount))

    conn.commit()
    conn.close()


def stats():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM products")
    total_products = c.fetchone()[0]

    c.execute("SELECT SUM(quantity) FROM products")
    total_quantity = c.fetchone()[0] or 0

    conn.close()

    return {
        "total_products": total_products,
        "total_quantity": total_quantity
    }


# =========================
# 📁 6. FILE BẮT BUỘC
# =========================
# database/__init__.py  (file rỗng)
# services/__init__.py  (file rỗng)
# utils/__init__.py     (file rỗng)


# =========================
# 🚀 CÁCH CHẠY
# =========================
# cd warehouse_manager
# python main.py

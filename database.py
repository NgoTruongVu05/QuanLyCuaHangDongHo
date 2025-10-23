import sqlite3
import hashlib
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path: str = 'watch_store.db'):
        self.conn = sqlite3.connect(db_path)
        # Để trả về dict thay vì tuple, bạn có thể dùng row_factory nếu muốn
        # self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Bảng sản phẩm (liên kết brand_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand_id INTEGER NOT NULL,
                product_type TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                description TEXT,
                movement_type TEXT,
                power_reserve INTEGER,
                water_resistant BOOLEAN,
                battery_life INTEGER,
                features TEXT,
                connectivity TEXT,
                FOREIGN KEY (brand_id) REFERENCES brands (id)
            )
        ''')

        # Bảng nhân viên - BỎ cột username
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                ma_dinh_danh TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                vaitro INTEGER NOT NULL DEFAULT 0,
                phone TEXT,
                email TEXT,
                base_salary REAL DEFAULT 0,
                position TEXT DEFAULT 'sales'
            )
        ''')
        
        # Bảng khách hàng
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        ''')
        
        # Bảng hóa đơn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                employee_id TEXT,
                total_amount REAL NOT NULL,
                created_date TEXT NOT NULL,
                invoice_type TEXT DEFAULT 'sale',
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Bảng chi tiết hóa đơn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Bảng đơn sửa chữa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repair_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                employee_id TEXT,
                watch_description TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                estimated_cost REAL DEFAULT 0,
                actual_cost REAL DEFAULT 0,
                created_date TEXT NOT NULL,
                estimated_completion TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Bảng lương
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                base_salary REAL NOT NULL,
                bonus REAL DEFAULT 0,
                deductions REAL DEFAULT 0,
                total_salary REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Thêm dữ liệu mẫu cho brands
        cursor.executemany('''
            INSERT OR IGNORE INTO brands (name, country) VALUES (?, ?)
        ''', [
            ('Seiko', 'Japan'),
            ('Casio', 'Japan'),
            ('Rolex', 'Switzerland'),
            ('Citizen', 'Japan'),
            ('Omega', 'Switzerland')
        ])
        
        # Thêm admin mặc định - QL + 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, password, full_name, vaitro, base_salary, position)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('ql123456', '123456789012', self.hash_password('admin123'), 'Quản trị viên', 1, 15000000, 'manager'))
        
        # Thêm nhân viên mặc định - NV + 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, password, full_name, vaitro, base_salary, position)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('nv654321', '987654321098', self.hash_password('123456'), 'Nhân Viên Mẫu', 0, 8000000, 'sales'))
        
        self.conn.commit()
    
    def generate_employee_id(self, ma_dinh_danh, vaitro):
        """Tạo ID theo format: nv/ql + 6 số cuối mã định danh"""
        if len(ma_dinh_danh) != 12 or not ma_dinh_danh.isdigit():
            raise ValueError("Mã định danh phải có đúng 12 chữ số")
        
        six_digits = ma_dinh_danh[-6:]  # 6 số cuối
        prefix = "ql" if vaitro == 1 else "nv"  # ql cho quản lý, nv cho nhân viên
        return f"{prefix}{six_digits}"
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, login_input, password):
        """Xác thực đăng nhập: tất cả đều dùng ID"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM employees WHERE id = ? AND password = ?
        ''', (login_input, self.hash_password(password)))
        user = cursor.fetchone()
        
        return user
    
    def check_ma_dinh_danh_exists(self, ma_dinh_danh):
        """Kiểm tra mã định danh đã tồn tại chưa"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM employees WHERE ma_dinh_danh = ?', (ma_dinh_danh,))
        return cursor.fetchone() is not None

    # Một vài hàm CRUD hữu ích cho brands và products
    def add_brand(self, name: str, country: Optional[str] = None) -> int:
        """Thêm thương hiệu mới, trả về id thương hiệu"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO brands (name, country) VALUES (?, ?)', (name, country))
        self.conn.commit()
        # lấy id (nếu đã tồn tại, vẫn trả về id hiện có)
        cursor.execute('SELECT id FROM brands WHERE name = ?', (name,))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_brands(self) -> List[Tuple[int, str, Optional[str]]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, country FROM brands')
        return cursor.fetchall()

    def add_product(self, name: str, brand_id: int, product_type: str, price: float, quantity: int, **kwargs) -> int:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
            
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, brand_id, product_type, price, quantity, description, movement_type, power_reserve, water_resistant, battery_life, features, connectivity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            brand_id,
            product_type,
            price,
            quantity,
            kwargs.get('description'),
            kwargs.get('movement_type'),
            kwargs.get('power_reserve'),
            kwargs.get('water_resistant'),
            kwargs.get('battery_life'),
            kwargs.get('features'),
            kwargs.get('connectivity')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_products_with_brand(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, b.name AS brand, p.product_type, p.price, p.quantity
            FROM products p
            JOIN brands b ON p.brand_id = b.id
        ''')
        return cursor.fetchall()

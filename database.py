import sqlite3
import hashlib
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path: str = 'watch_store.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()

        # Bảng thương hiệu (brands)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                country TEXT
            )
        ''')
        
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

        # Bảng nhân viên - BỎ cột position
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                ma_dinh_danh TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                vaitro INTEGER NOT NULL DEFAULT 0,
                phone TEXT,
                email TEXT,
                base_salary REAL DEFAULT 0
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
                id TEXT PRIMARY KEY,
                customer_id INTEGER,
                employee_id TEXT,
                total_amount REAL NOT NULL,
                created_date TEXT NOT NULL,
                status TEXT DEFAULT '',
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Bảng chi tiết hóa đơn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT,
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
                actual_cost REAL DEFAULT 0,
                created_date TEXT NOT NULL,
                estimated_completion TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Bảng lương - BỎ vì tính tự động
        cursor.execute('DROP TABLE IF EXISTS salaries')
        
        # Thêm admin mặc định - QL + 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, password, full_name, vaitro, base_salary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('ql123456', '777777123456', self.hash_password('admin123'), 'Quản trị viên', 1, 15000000))
        
        # Thêm nhân viên mặc định - NV + 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, password, full_name, vaitro, base_salary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('nv654321', '888888654321', self.hash_password('123456'), 'Nhân Viên Mẫu', 0, 8000000))
        
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

    def get_employee_sales_data(self, employee_id, month, year):
        """Lấy dữ liệu bán hàng của nhân viên theo tháng/năm để tính lương"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(total_amount) as total_sales
            FROM invoices 
            WHERE employee_id = ? 
            AND strftime('%m', created_date) = ? 
            AND strftime('%Y', created_date) = ?
            AND status = ''
        ''', (employee_id, f"{month:02d}", str(year)))
        
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0

    def calculate_salary(self, employee_id, month, year):
        """Tính lương tự động dựa trên lương cơ bản và hoa hồng 10%"""
        cursor = self.conn.cursor()
        
        # Lấy lương cơ bản
        cursor.execute('SELECT base_salary FROM employees WHERE id = ?', (employee_id,))
        result = cursor.fetchone()
        if not result:
            return {
                'base_salary': 0,
                'total_sales': 0,
                'commission': 0,
                'total_salary': 0
            }
        
        base_salary = result[0] if result[0] else 0
        
        # Tính tổng doanh số bán hàng - SỬA LẠI CÂU QUERY
        cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) as total_sales
            FROM invoices 
            WHERE employee_id = ? 
            AND strftime('%m', created_date) = ? 
            AND strftime('%Y', created_date) = ?
        ''', (employee_id, f"{month:02d}", str(year)))
        
        result = cursor.fetchone()
        total_sales = result[0] if result else 0
        
        # Tính hoa hồng %
        commission = total_sales * 0.005
        
        # Tổng lương = lương cơ bản + hoa hồng
        total_salary = base_salary + commission
        
        return {
            'base_salary': base_salary,
            'total_sales': total_sales,
            'commission': commission,
            'total_salary': total_salary
        }

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
    
    def generate_invoice_id(self) -> str:
        """Tạo ID hóa đơn theo format HD001, HD002,..."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM invoices ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        
        if result is None:
            return 'HD001'
        
        last_id = result[0]  # VD: HD001
        num = int(last_id[2:]) + 1  # Lấy phần số và tăng 1
        return f'HD{num:03d}'
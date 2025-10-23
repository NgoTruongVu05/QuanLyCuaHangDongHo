import sqlite3
import hashlib

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('watch_store.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Bảng nhân viên - thêm cột ma_dinh_danh
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                ma_dinh_danh TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
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
        
        # Bảng sản phẩm
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                product_type TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                description TEXT,
                movement_type TEXT,
                power_reserve INTEGER,
                water_resistant BOOLEAN,
                battery_life INTEGER,
                features TEXT,
                connectivity TEXT
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
        
        # Thêm admin mặc định - CHỈ 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, username, password, full_name, vaitro, base_salary, position)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('nv123456', '123456789012', 'admin', self.hash_password('admin123'), 'Quản trị viên', 1, 15000000, 'manager'))
        
        # Thêm nhân viên mặc định - CHỈ 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, username, password, full_name, vaitro, base_salary, position)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('nv654321', '987654321098', 'nhanvien', self.hash_password('123456'), 'Nhân Viên Mẫu', 0, 8000000, 'sales'))
        
        self.conn.commit()
    
    def generate_employee_id(self, ma_dinh_danh):
        """Tạo ID theo format: nv + 6 số cuối mã định danh"""
        if len(ma_dinh_danh) != 12 or not ma_dinh_danh.isdigit():
            raise ValueError("Mã định danh phải có đúng 12 chữ số")
        
        six_digits = ma_dinh_danh[-6:]  # 6 số cuối
        return f"nv{six_digits}"
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, login_input, password):
        """Xác thực đăng nhập: nhân viên dùng ID, quản lý dùng username"""
        cursor = self.conn.cursor()
        
        # Thử đăng nhập bằng ID trước (cho nhân viên)
        cursor.execute('''
            SELECT * FROM employees WHERE id = ? AND password = ?
        ''', (login_input, self.hash_password(password)))
        user = cursor.fetchone()
        
        if user:
            return user
        
        # Nếu không tìm thấy bằng ID, thử bằng username (cho quản lý)
        cursor.execute('''
            SELECT * FROM employees WHERE username = ? AND password = ?
        ''', (login_input, self.hash_password(password)))
        user = cursor.fetchone()
        
        return user
    
    def check_ma_dinh_danh_exists(self, ma_dinh_danh):
        """Kiểm tra mã định danh đã tồn tại chưa"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM employees WHERE ma_dinh_danh = ?', (ma_dinh_danh,))
        return cursor.fetchone() is not None
    
    def check_username_exists(self, username):
        """Kiểm tra username đã tồn tại chưa"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM employees WHERE username = ?', (username,))
        return cursor.fetchone() is not None
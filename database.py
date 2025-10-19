import sqlite3
import hashlib

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('watch_store.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Bảng nhân viên (vaitro: 0=nhân viên, 1=quản lý)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                vaitro INTEGER NOT NULL DEFAULT 0, -- 0=nhân viên, 1=quản lý
                phone TEXT,
                email TEXT
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
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                description TEXT
            )
        ''')
        
        # Bảng hóa đơn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                employee_id INTEGER,
                total_amount REAL NOT NULL,
                created_date TEXT NOT NULL,
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
        
        # Thêm admin mặc định (quản lý)
        cursor.execute('''
            INSERT OR IGNORE INTO employees (username, password, full_name, vaitro)
            VALUES (?, ?, ?, ?)
        ''', ('admin', self.hash_password('admin123'), 'Quản trị viên', 1))
        
        # Thêm nhân viên mặc định
        cursor.execute('''
            INSERT OR IGNORE INTO employees (username, password, full_name, vaitro)
            VALUES (?, ?, ?, ?)
        ''', ('nhanvien', self.hash_password('123456'), 'Nhân Viên Mẫu', 0))
        
        self.conn.commit()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM employees WHERE username = ? AND password = ?
        ''', (username, self.hash_password(password)))
        return cursor.fetchone()
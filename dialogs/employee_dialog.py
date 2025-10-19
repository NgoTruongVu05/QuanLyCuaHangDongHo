from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QComboBox, QMessageBox)

class EmployeeDialog(QDialog):
    def __init__(self, db, employee_id=None):
        super().__init__()
        self.db = db
        self.employee_id = employee_id
        self.init_ui()
        if employee_id:
            self.load_employee_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa nhân viên' if not self.employee_id else 'Sửa nhân viên')
        self.setFixedSize(400, 300)
        
        layout = QFormLayout()
        
        self.username_input = QLineEdit()
        layout.addRow('Tên đăng nhập:', self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow('Mật khẩu:', self.password_input)
        
        self.full_name_input = QLineEdit()
        layout.addRow('Họ tên:', self.full_name_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(['Nhân viên', 'Quản lý'])
        layout.addRow('Vai trò:', self.role_combo)
        
        self.phone_input = QLineEdit()
        layout.addRow('Điện thoại:', self.phone_input)
        
        self.email_input = QLineEdit()
        layout.addRow('Email:', self.email_input)
        
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_employee)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
    
    def load_employee_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE id = ?', (self.employee_id,))
        employee = cursor.fetchone()
        
        if employee:
            self.username_input.setText(employee[1])
            self.full_name_input.setText(employee[3])
            self.role_combo.setCurrentIndex(employee[4])  # 0=nhân viên, 1=quản lý
            self.phone_input.setText(employee[5] if employee[5] else '')
            self.email_input.setText(employee[6] if employee[6] else '')
    
    def save_employee(self):
        username = self.username_input.text()
        password = self.password_input.text()
        full_name = self.full_name_input.text()
        role = self.role_combo.currentIndex()  # 0=nhân viên, 1=quản lý
        phone = self.phone_input.text()
        email = self.email_input.text()
        
        if not username or not full_name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin!')
            return
        
        cursor = self.db.conn.cursor()
        
        # Check if username exists (for new employees)
        if not self.employee_id:
            cursor.execute('SELECT id FROM employees WHERE username = ?', (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, 'Lỗi', 'Tên đăng nhập đã tồn tại!')
                return
        
        if self.employee_id:
            if password:
                hashed_password = self.db.hash_password(password)
                cursor.execute('''
                    UPDATE employees SET username=?, password=?, full_name=?, vaitro=?, phone=?, email=?
                    WHERE id=?
                ''', (username, hashed_password, full_name, role, phone, email, self.employee_id))
            else:
                cursor.execute('''
                    UPDATE employees SET username=?, full_name=?, vaitro=?, phone=?, email=?
                    WHERE id=?
                ''', (username, full_name, role, phone, email, self.employee_id))
        else:
            if not password:
                QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập mật khẩu!')
                return
            hashed_password = self.db.hash_password(password)
            cursor.execute('''
                INSERT INTO employees (username, password, full_name, vaitro, phone, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, full_name, role, phone, email))
        
        self.db.conn.commit()
        self.accept()
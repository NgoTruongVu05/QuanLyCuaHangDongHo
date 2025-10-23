from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QComboBox, QMessageBox, QDoubleSpinBox, QLabel)

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
        self.setFixedSize(450, 500)
        
        layout = QFormLayout()
        
        # Mã định danh (chỉ nhập khi thêm mới)
        if not self.employee_id:
            self.ma_dinh_danh_input = QLineEdit()
            self.ma_dinh_danh_input.setPlaceholderText('Nhập 12 chữ số')
            self.ma_dinh_danh_input.textChanged.connect(self.on_ma_dinh_danh_changed)
            layout.addRow('Mã định danh (12 số):', self.ma_dinh_danh_input)
            
            # Hiển thị ID - không cho phép sửa
            self.id_label = QLabel('Chưa có ID')
            self.id_label.setStyleSheet('color: #2E86AB; font-weight: bold; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
            layout.addRow('ID nhân viên:', self.id_label)
        else:
            # Khi sửa, hiển thị ID readonly
            id_label = QLabel(self.employee_id)
            id_label.setStyleSheet('color: #666; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
            layout.addRow('ID nhân viên:', id_label)
        
        self.username_input = QLineEdit()
        layout.addRow('Tên đăng nhập:', self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        if not self.employee_id:
            self.password_input.setPlaceholderText('Bắt buộc khi thêm mới')
        else:
            self.password_input.setPlaceholderText('Để trống nếu không đổi mật khẩu')
        layout.addRow('Mật khẩu:', self.password_input)
        
        self.full_name_input = QLineEdit()
        layout.addRow('Họ tên:', self.full_name_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(['Nhân viên', 'Quản lý'])
        layout.addRow('Vai trò:', self.role_combo)
        
        self.position_combo = QComboBox()
        self.position_combo.addItems(['Bán hàng', 'Kỹ thuật', 'Quản lý'])
        layout.addRow('Chức vụ:', self.position_combo)
        
        self.base_salary_input = QDoubleSpinBox()
        self.base_salary_input.setMaximum(999999999)
        self.base_salary_input.setPrefix('VND ')
        layout.addRow('Lương cơ bản:', self.base_salary_input)
        
        self.phone_input = QLineEdit()
        layout.addRow('Điện thoại:', self.phone_input)
        
        self.email_input = QLineEdit()
        layout.addRow('Email:', self.email_input)
        
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_employee)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
    
    def on_ma_dinh_danh_changed(self, text):
        """Cập nhật ID khi mã định danh thay đổi"""
        if len(text) == 12 and text.isdigit():
            six_digits = text[-6:]  # Lấy 6 số cuối
            employee_id = f"nv{six_digits}"
            self.id_label.setText(employee_id)
        else:
            self.id_label.setText('Chưa có ID')
    
    def load_employee_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE id = ?', (self.employee_id,))
        employee = cursor.fetchone()
        
        if employee:
            self.username_input.setText(employee[2])
            self.full_name_input.setText(employee[4])
            self.role_combo.setCurrentIndex(employee[5])  # vaitro
            self.position_combo.setCurrentText(self.get_position_text(employee[8]))
            self.base_salary_input.setValue(employee[7] if employee[7] else 0)
            self.phone_input.setText(employee[6] if employee[6] else '')
            self.email_input.setText(employee[6] if employee[6] else '')
    
    def get_position_text(self, position):
        position_map = {'sales': 'Bán hàng', 'technician': 'Kỹ thuật', 'manager': 'Quản lý'}
        return position_map.get(position, 'Bán hàng')
    
    def get_position_value(self, text):
        position_map = {'Bán hàng': 'sales', 'Kỹ thuật': 'technician', 'Quản lý': 'manager'}
        return position_map.get(text, 'sales')
    
    def save_employee(self):
        # Lấy dữ liệu từ form
        username = self.username_input.text().strip()
        password = self.password_input.text()
        full_name = self.full_name_input.text().strip()
        role = self.role_combo.currentIndex()  # 0=nhân viên, 1=quản lý
        position = self.get_position_value(self.position_combo.currentText())
        base_salary = self.base_salary_input.value()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        
        if not username or not full_name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin!')
            return
        
        cursor = self.db.conn.cursor()
        
        if not self.employee_id:
            # THÊM MỚI
            ma_dinh_danh = self.ma_dinh_danh_input.text().strip()
            
            if not ma_dinh_danh:
                QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập mã định danh!')
                return
            
            if len(ma_dinh_danh) != 12 or not ma_dinh_danh.isdigit():
                QMessageBox.warning(self, 'Lỗi', 'Mã định danh phải có đúng 12 chữ số!')
                return
            
            if self.db.check_ma_dinh_danh_exists(ma_dinh_danh):
                QMessageBox.warning(self, 'Lỗi', 'Mã định danh đã tồn tại!')
                return
            
            if not password:
                QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập mật khẩu!')
                return
            
            # Lấy ID từ label (đã được tạo tự động)
            employee_id = self.id_label.text()
            if employee_id == 'Chưa có ID':
                QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập mã định danh hợp lệ!')
                return
            
            # Kiểm tra username trùng
            cursor.execute('SELECT id FROM employees WHERE username = ?', (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, 'Lỗi', 'Tên đăng nhập đã tồn tại!')
                return
            
            hashed_password = self.db.hash_password(password)
            cursor.execute('''
                INSERT INTO employees (id, ma_dinh_danh, username, password, full_name, vaitro, phone, email, base_salary, position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, ma_dinh_danh, username, hashed_password, full_name, role, phone, email, base_salary, position))
        
        else:
            # SỬA
            if password:
                hashed_password = self.db.hash_password(password)
                cursor.execute('''
                    UPDATE employees SET username=?, password=?, full_name=?, vaitro=?, phone=?, email=?, base_salary=?, position=?
                    WHERE id=?
                ''', (username, hashed_password, full_name, role, phone, email, base_salary, position, self.employee_id))
            else:
                cursor.execute('''
                    UPDATE employees SET username=?, full_name=?, vaitro=?, phone=?, email=?, base_salary=?, position=?
                    WHERE id=?
                ''', (username, full_name, role, phone, email, base_salary, position, self.employee_id))
        
        self.db.conn.commit()
        self.accept()
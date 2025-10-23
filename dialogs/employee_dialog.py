from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QComboBox, QMessageBox, QDoubleSpinBox, QLabel,
                             QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy)

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
        self.setFixedSize(450, 450)
        
        form_layout = QFormLayout()
        
        # Mã định danh (chỉ nhập khi thêm mới)
        if not self.employee_id:
            self.ma_dinh_danh_input = QLineEdit()
            self.ma_dinh_danh_input.setPlaceholderText('Nhập 12 chữ số')
            self.ma_dinh_danh_input.textChanged.connect(self.on_ma_dinh_danh_changed)
            form_layout.addRow('Mã định danh (12 số):', self.ma_dinh_danh_input)
            
            # Hiển thị ID - không cho phép sửa
            self.id_label = QLabel('Chưa có ID')
            self.id_label.setStyleSheet('color: #2E86AB; font-weight: bold; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
            form_layout.addRow('ID:', self.id_label)
        else:
            # Khi sửa, hiển thị ID readonly
            id_label = QLabel(self.employee_id)
            id_label.setStyleSheet('color: #666; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
            form_layout.addRow('ID:', id_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        if not self.employee_id:
            self.password_input.setPlaceholderText('Bắt buộc khi thêm mới')
        else:
            self.password_input.setPlaceholderText('Để trống nếu không đổi mật khẩu')
        form_layout.addRow('Mật khẩu:', self.password_input)
        
        self.full_name_input = QLineEdit()
        form_layout.addRow('Họ tên:', self.full_name_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(['Nhân viên', 'Quản lý'])
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        form_layout.addRow('Vai trò:', self.role_combo)
        
        self.position_combo = QComboBox()
        self.position_combo.addItems(['Bán hàng', 'Kỹ thuật', 'Quản lý'])
        form_layout.addRow('Chức vụ:', self.position_combo)
        
        self.base_salary_input = QDoubleSpinBox()
        self.base_salary_input.setMaximum(999999999)
        self.base_salary_input.setPrefix('VND ')
        form_layout.addRow('Lương cơ bản:', self.base_salary_input)
        
        self.phone_input = QLineEdit()
        form_layout.addRow('Điện thoại:', self.phone_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow('Email:', self.email_input)
        
        # nút Lưu - sẽ đặt ở dưới cùng, căn giữa
        self.save_btn = QPushButton('Lưu')
        self.save_btn.clicked.connect(self.save_employee)

        # Main vertical layout: form on top, expanding spacer, button row at bottom centered
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        main_layout.addLayout(btn_row)

        self.setLayout(main_layout)
    
    def on_ma_dinh_danh_changed(self, text):
        """Cập nhật ID khi mã định danh thay đổi"""
        if len(text) == 12 and text.isdigit():
            role = self.role_combo.currentIndex()
            try:
                employee_id = self.db.generate_employee_id(text, role)
                self.id_label.setText(employee_id)
            except ValueError:
                self.id_label.setText('Mã định danh không hợp lệ')
        else:
            self.id_label.setText('Chưa có ID')
    
    def on_role_changed(self, role_text):
        """Cập nhật ID khi vai trò thay đổi"""
        if not self.employee_id and hasattr(self, 'ma_dinh_danh_input'):
            ma_dinh_danh = self.ma_dinh_danh_input.text()
            if len(ma_dinh_danh) == 12 and ma_dinh_danh.isdigit():
                role = 1 if role_text == 'Quản lý' else 0
                try:
                    employee_id = self.db.generate_employee_id(ma_dinh_danh, role)
                    self.id_label.setText(employee_id)
                except ValueError:
                    self.id_label.setText('Mã định danh không hợp lệ')
    
    def load_employee_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE id = ?', (self.employee_id,))
        employee = cursor.fetchone()
        
        if employee:
            self.full_name_input.setText(employee[3])
            self.role_combo.setCurrentIndex(employee[4])  # vaitro
            self.position_combo.setCurrentText(self.get_position_text(employee[7]))
            self.base_salary_input.setValue(employee[6] if employee[6] else 0)
            self.phone_input.setText(employee[5] if employee[5] else '')
            self.email_input.setText(employee[5] if employee[5] else '')
    
    def get_position_text(self, position):
        position_map = {'sales': 'Bán hàng', 'technician': 'Kỹ thuật', 'manager': 'Quản lý'}
        return position_map.get(position, 'Bán hàng')
    
    def save_employee(self):
        # Lấy dữ liệu từ form
        password = self.password_input.text()
        full_name = self.full_name_input.text().strip()
        role = self.role_combo.currentIndex()  # 0=nhân viên, 1=quản lý
        position = self.get_position_value(self.position_combo.currentText())
        base_salary = self.base_salary_input.value()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        
        if not full_name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập họ tên!')
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
            
            hashed_password = self.db.hash_password(password)
            cursor.execute('''
                INSERT INTO employees (id, ma_dinh_danh, password, full_name, vaitro, phone, email, base_salary, position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, ma_dinh_danh, hashed_password, full_name, role, phone, email, base_salary, position))
        
        else:
            # SỬA
            if password:
                hashed_password = self.db.hash_password(password)
                cursor.execute('''
                    UPDATE employees SET password=?, full_name=?, vaitro=?, phone=?, email=?, base_salary=?, position=?
                    WHERE id=?
                ''', (hashed_password, full_name, role, phone, email, base_salary, position, self.employee_id))
            else:
                cursor.execute('''
                    UPDATE employees SET full_name=?, vaitro=?, phone=?, email=?, base_salary=?, position=?
                    WHERE id=?
                ''', (full_name, role, phone, email, base_salary, position, self.employee_id))
        
        self.db.conn.commit()
        self.accept()
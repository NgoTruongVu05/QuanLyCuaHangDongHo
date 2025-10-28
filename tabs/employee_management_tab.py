from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QComboBox, QLineEdit, QLabel)
from PyQt6.QtCore import Qt

class EmployeeManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_btn = QPushButton('Thêm nhân viên')
        add_btn.clicked.connect(self.add_employee)
        controls_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Search area
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel('Tìm kiếm theo:'))
        
        self.search_type = QComboBox()
        self.search_type.addItems(['Tất cả', 'ID', 'Mã ĐD', 'Họ tên', 'Vai trò'])
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        search_layout.addWidget(self.search_type)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        self.search_input.textChanged.connect(self.search_employees)
        search_layout.addWidget(self.search_input)
        
        # Dropdown cho tìm kiếm theo vai trò (ẩn ban đầu)
        self.role_search_combo = QComboBox()
        self.role_search_combo.addItems(['Quản lý', 'Nhân viên'])
        self.role_search_combo.currentTextChanged.connect(self.search_employees)
        self.role_search_combo.setVisible(False)
        search_layout.addWidget(self.role_search_combo)
        
        # Clear search button
        clear_search_btn = QPushButton('Xóa tìm kiếm')
        clear_search_btn.clicked.connect(self.clear_search)
        clear_search_btn.setStyleSheet('''
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        ''')
        search_layout.addWidget(clear_search_btn)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table - BỎ cột position (chức vụ)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Mã ĐD', 'Họ tên', 'Vai trò', 'Lương cơ bản', 'Điện thoại', 'Email', 'Hành động'
        ])
        
        # KHÔNG CHO CHỌN BẤT KỲ Ô NÀO
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Mã ĐD
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Full name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Role
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Salary
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Phone
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Action

        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def on_search_type_changed(self, search_type):
        """Cập nhật giao diện tìm kiếm khi thay đổi loại tìm kiếm"""
        if search_type == 'Vai trò':
            # Ẩn ô nhập và hiện dropdown chọn vai trò
            self.search_input.setVisible(False)
            self.role_search_combo.setVisible(True)
            # Trigger search với giá trị mặc định
            self.search_employees()
        else:
            # Hiện ô nhập và ẩn dropdown
            self.search_input.setVisible(True)
            self.role_search_combo.setVisible(False)
            
            # Cập nhật placeholder text
            if search_type == 'Tất cả':
                self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
            elif search_type == 'ID':
                self.search_input.setPlaceholderText('Nhập ID nhân viên...')
            elif search_type == 'Mã ĐD':
                self.search_input.setPlaceholderText('Nhập mã định danh...')
            elif search_type == 'Họ tên':
                self.search_input.setPlaceholderText('Nhập họ tên nhân viên...')
            
            # Trigger search again when type changes
            self.search_employees()
    
    def search_employees(self):
        """Tìm kiếm nhân viên dựa trên loại và từ khóa"""
        search_type = self.search_type.currentText()
        
        cursor = self.db.conn.cursor()
        
        if search_type == 'Tất cả':
            search_text = self.search_input.text().strip().lower()
            if not search_text:
                # Nếu không có từ khóa, hiển thị tất cả
                self.load_data()
                return
            
            # Tìm kiếm trên tất cả các trường
            cursor.execute('''
                SELECT id, ma_dinh_danh, full_name, vaitro, base_salary, phone 
                FROM employees 
                WHERE LOWER(id) LIKE ? OR LOWER(ma_dinh_danh) LIKE ? OR LOWER(full_name) LIKE ? 
                   OR vaitro = ?
            ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', 
                  1 if search_text in ['quản lý', '1'] else 0))
        
        elif search_type == 'ID':
            search_text = self.search_input.text().strip().lower()
            if not search_text:
                self.load_data()
                return
            cursor.execute('''
                SELECT id, ma_dinh_danh, full_name, vaitro, base_salary, phone 
                FROM employees 
                WHERE LOWER(id) LIKE ?
            ''', (f'%{search_text}%',))
        
        elif search_type == 'Mã ĐD':
            search_text = self.search_input.text().strip().lower()
            if not search_text:
                self.load_data()
                return
            cursor.execute('''
                SELECT id, ma_dinh_danh, full_name, vaitro, base_salary, phone 
                FROM employees 
                WHERE LOWER(ma_dinh_danh) LIKE ?
            ''', (f'%{search_text}%',))
        
        elif search_type == 'Họ tên':
            search_text = self.search_input.text().strip().lower()
            if not search_text:
                self.load_data()
                return
            cursor.execute('''
                SELECT id, ma_dinh_danh, full_name, vaitro, base_salary, phone 
                FROM employees 
                WHERE LOWER(full_name) LIKE ?
            ''', (f'%{search_text}%',))
        
        elif search_type == 'Vai trò':
            # Sử dụng dropdown chọn vai trò
            selected_role = self.role_search_combo.currentText()
            role_value = 1 if selected_role == 'Quản lý' else 0
            cursor.execute('''
                SELECT id, ma_dinh_danh, full_name, vaitro, base_salary, phone 
                FROM employees 
                WHERE vaitro = ?
            ''', (role_value,))
        
        employees = cursor.fetchall()
        self.display_employees(employees)
    
    def clear_search(self):
        """Xóa tìm kiếm và hiển thị tất cả nhân viên"""
        self.search_type.setCurrentText('Tất cả')
        self.search_input.clear()
        self.role_search_combo.setCurrentText('Quản lý')
        self.load_data()
    
    def load_data(self):
        """Tải toàn bộ dữ liệu nhân viên"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, ma_dinh_danh, full_name, vaitro, base_salary, phone, email FROM employees')
        employees = cursor.fetchall()
        self.display_employees(employees)
    
    def display_employees(self, employees):
        """Hiển thị danh sách nhân viên lên table"""
        # XÓA TẤT CẢ TRƯỚC KHI THÊM MỚI
        self.table.setRowCount(0)
        
        # Đặt lại số hàng
        self.table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            for col, value in enumerate(employee):
                if col == 3:  # Cột vai trò
                    role_text = "Quản lý" if value == 1 else "Nhân viên"
                    item = QTableWidgetItem(role_text)
                elif col == 4:  # Cột lương
                    item = QTableWidgetItem(f"{value:,.0f} VND" if value else "0 VND")
                else:
                    item = QTableWidgetItem(str(value) if value else '')
                
                # KHÔNG CHO CHỌN VÀ CHỈNH SỬA
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEditable)
                
                self.table.setItem(row, col, item)
            
            # Nút sửa và xóa cho từng dòng
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            edit_btn = QPushButton('Sửa')
            edit_btn.setStyleSheet('''
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    margin: 0 3px;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 11px;
                    margin-right: 2px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
            ''')
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_employee_row(r))
            action_layout.addWidget(edit_btn)

            # Kiểm tra theo giá trị cột vaitro để không cho xóa quản lý
            employee_role = employee[3]  # vaitro ở index 3
            if employee_role == 0:  # Chỉ cho phép xóa nhân viên (vaitro = 0)
                delete_btn = QPushButton('Xóa')
                delete_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
                        margin: 0 3px;
                        border-radius: 3px;
                        padding: 3px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_employee_row(r))
                action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 7, action_widget)
        
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def add_employee(self):
        from dialogs.employee_dialog import EmployeeDialog
        dialog = EmployeeDialog(self.db)
        if dialog.exec():
            self.load_data()
    
    def edit_employee_row(self, row):
        employee_id = self.table.item(row, 0).text()
        from dialogs.employee_dialog import EmployeeDialog
        dialog = EmployeeDialog(self.db, employee_id)
        if dialog.exec():
            self.load_data()
    
    def delete_employee_row(self, row):
        employee_id = self.table.item(row, 0).text()
        employee_name = self.table.item(row, 2).text()
        
        # Kiểm tra lại để chắc chắn (theo giá trị vaitro)
        employee_role_item = self.table.item(row, 3)
        if employee_role_item and employee_role_item.text() == 'Quản lý':
            QMessageBox.warning(self, 'Lỗi', 'Không thể xóa tài khoản quản lý!')
            return
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa nhân viên "{employee_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
            self.db.conn.commit()
            self.load_data()
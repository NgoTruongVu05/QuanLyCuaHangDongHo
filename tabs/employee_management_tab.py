from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView)

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
        
        # Table - BỎ cột username
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Mã ĐD', 'Họ tên', 'Vai trò', 'Chức vụ', 'Lương cơ bản', 'Điện thoại', 'Hành động'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Mã ĐD
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Full name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Role
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Position
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Salary
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Phone
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Action
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, ma_dinh_danh, full_name, vaitro, position, base_salary, phone FROM employees')
        employees = cursor.fetchall()
        
        self.table.setRowCount(len(employees))
        for row, employee in enumerate(employees):
            for col, value in enumerate(employee):
                if col == 3:  # Cột vai trò
                    role_text = "Quản lý" if value == 1 else "Nhân viên"
                    self.table.setItem(row, col, QTableWidgetItem(role_text))
                elif col == 5:  # Cột lương
                    self.table.setItem(row, col, QTableWidgetItem(f"{value:,.0f} VND" if value else "0 VND"))
                elif col == 4:  # Cột chức vụ
                    position_text = self.get_position_text(value)
                    self.table.setItem(row, col, QTableWidgetItem(position_text))
                else:
                    self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ''))
            
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
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
            ''')
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_employee_row(r))
            action_layout.addWidget(edit_btn)
            
            # Không cho xóa tài khoản quản lý (ID bắt đầu bằng "ql")
            employee_id = employee[0]
            if not employee_id.startswith('ql'):  # Không hiển thị nút xóa cho quản lý
                delete_btn = QPushButton('Xóa')
                delete_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
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
    
    def get_position_text(self, position):
        position_map = {'sales': 'Bán hàng', 'technician': 'Kỹ thuật', 'manager': 'Quản lý'}
        return position_map.get(position, 'Bán hàng')
    
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
        
        # Prevent deleting manager accounts
        if employee_id.startswith('ql'):
            QMessageBox.warning(self, 'Lỗi', 'Không thể xóa tài khoản quản lý!')
            return
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa nhân viên "{employee_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
            self.db.conn.commit()
            self.load_data()
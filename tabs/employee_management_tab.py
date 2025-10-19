from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox)
from dialogs.employee_dialog import EmployeeDialog

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
        
        edit_btn = QPushButton('Sửa nhân viên')
        edit_btn.clicked.connect(self.edit_employee)
        controls_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('Xóa nhân viên')
        delete_btn.clicked.connect(self.delete_employee)
        controls_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Tên đăng nhập', 'Họ tên', 'Vai trò', 'Điện thoại', 'Email'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, username, full_name, vaitro, phone, email FROM employees')
        employees = cursor.fetchall()
        
        self.table.setRowCount(len(employees))
        for row, employee in enumerate(employees):
            for col, value in enumerate(employee):
                if col == 3:  # Cột vai trò
                    role_text = "Quản lý" if value == 1 else "Nhân viên"
                    self.table.setItem(row, col, QTableWidgetItem(role_text))
                else:
                    self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ''))
    
    def add_employee(self):
        dialog = EmployeeDialog(self.db)
        if dialog.exec():
            self.load_data()
    
    def edit_employee(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn nhân viên để sửa!')
            return
        
        employee_id = int(self.table.item(selected, 0).text())
        dialog = EmployeeDialog(self.db, employee_id)
        if dialog.exec():
            self.load_data()
    
    def delete_employee(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn nhân viên để xóa!')
            return
        
        employee_id = int(self.table.item(selected, 0).text())
        employee_name = self.table.item(selected, 2).text()
        
        # Prevent deleting yourself
        if employee_id == 1:  # admin account
            QMessageBox.warning(self, 'Lỗi', 'Không thể xóa tài khoản quản trị!')
            return
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa nhân viên "{employee_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
            self.db.conn.commit()
            self.load_data()
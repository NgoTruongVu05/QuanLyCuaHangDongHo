from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox)
from dialogs.customer_dialog import CustomerDialog

class CustomerManagementTab(QWidget):
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
        
        add_btn = QPushButton('Thêm khách hàng')
        add_btn.clicked.connect(self.add_customer)
        controls_layout.addWidget(add_btn)
        
        edit_btn = QPushButton('Sửa khách hàng')
        edit_btn.clicked.connect(self.edit_customer)
        controls_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('Xóa khách hàng')
        delete_btn.clicked.connect(self.delete_customer)
        controls_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Điện thoại', 'Email', 'Địa chỉ'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers')
        customers = cursor.fetchall()
        
        self.table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            for col, value in enumerate(customer):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ''))
    
    def add_customer(self):
        dialog = CustomerDialog(self.db)
        if dialog.exec():
            self.load_data()
    
    def edit_customer(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn khách hàng để sửa!')
            return
        
        customer_id = int(self.table.item(selected, 0).text())
        dialog = CustomerDialog(self.db, customer_id)
        if dialog.exec():
            self.load_data()
    
    def delete_customer(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn khách hàng để xóa!')
            return
        
        customer_id = int(self.table.item(selected, 0).text())
        customer_name = self.table.item(selected, 1).text()
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa khách hàng "{customer_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
            self.db.conn.commit()
            self.load_data()
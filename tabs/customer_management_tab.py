from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView)

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
        
        if self.user_role == 1:
            add_btn = QPushButton('Thêm khách hàng')
            add_btn.clicked.connect(self.add_customer)
            controls_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Thêm cột hành động
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Điện thoại', 'Email', 'Địa chỉ', 'Hành động'])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Điện thoại
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Địa chỉ
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
        
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
            
            # Nút sửa và xóa cho từng dòng
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            if self.user_role == 1:
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
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_customer_row(r))
                action_layout.addWidget(edit_btn)
                
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
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_customer_row(r))
                action_layout.addWidget(delete_btn)
            else:
                view_btn = QPushButton('Xem')
                view_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #27AE60;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 3px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                ''')
                view_btn.clicked.connect(lambda checked, r=row: self.view_customer_row(r))
                action_layout.addWidget(view_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 5, action_widget)
    
    def add_customer(self):
        from dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.db)
        if dialog.exec():
            self.load_data()
    
    def edit_customer_row(self, row):
        customer_id = int(self.table.item(row, 0).text())
        from dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.db, customer_id)
        if dialog.exec():
            self.load_data()
    
    def delete_customer_row(self, row):
        customer_id = int(self.table.item(row, 0).text())
        customer_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa khách hàng "{customer_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
            self.db.conn.commit()
            self.load_data()
    
    def view_customer_row(self, row):
        customer_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        phone = self.table.item(row, 2).text()
        email = self.table.item(row, 3).text()
        address = self.table.item(row, 4).text()
        
        info_text = f"""
        Thông tin khách hàng:
        
        ID: {customer_id}
        Tên: {name}
        Điện thoại: {phone or 'Chưa có'}
        Email: {email or 'Chưa có'}
        Địa chỉ: {address or 'Chưa có'}
        """
        
        QMessageBox.information(self, 'Chi tiết khách hàng', info_text)
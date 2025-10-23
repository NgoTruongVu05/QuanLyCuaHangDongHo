from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QLineEdit, QLabel, QComboBox)
from PyQt6.QtCore import Qt

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
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Search area
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel('Tìm kiếm:'))
        
        self.search_type = QComboBox()
        self.search_type.addItems(['Tất cả', 'Tên', 'Số điện thoại'])  # BỎ EMAIL
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        search_layout.addWidget(self.search_type)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        self.search_input.textChanged.connect(self.search_customers)
        search_layout.addWidget(self.search_input)
        
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
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Thêm cột hành động
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Điện thoại', 'Email', 'Địa chỉ', 'Hành động'])

        
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
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
    
    def on_search_type_changed(self, search_type):
        """Cập nhật placeholder text khi thay đổi loại tìm kiếm"""
        if search_type == 'Tất cả':
            self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        elif search_type == 'Tên':
            self.search_input.setPlaceholderText('Nhập tên khách hàng...')
        elif search_type == 'Số điện thoại':
            self.search_input.setPlaceholderText('Nhập số điện thoại...')
        # BỎ PHẦN EMAIL
        
        # Trigger search again when type changes
        self.search_customers()
    
    def search_customers(self):
        """Tìm kiếm khách hàng dựa trên loại và từ khóa"""
        search_text = self.search_input.text().strip().lower()
        search_type = self.search_type.currentText()
        
        if not search_text:
            # Nếu không có từ khóa, hiển thị tất cả
            self.load_data()
            return
        
        cursor = self.db.conn.cursor()
        
        if search_type == 'Tất cả':
            # Tìm kiếm trên các trường Tên và Số điện thoại (BỎ EMAIL)
            cursor.execute('''
                SELECT * FROM customers 
                WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ?
            ''', (f'%{search_text}%', f'%{search_text}%'))
        
        elif search_type == 'Tên':
            cursor.execute('''
                SELECT * FROM customers 
                WHERE LOWER(name) LIKE ?
            ''', (f'%{search_text}%',))
        
        elif search_type == 'Số điện thoại':
            cursor.execute('''
                SELECT * FROM customers 
                WHERE LOWER(phone) LIKE ?
            ''', (f'%{search_text}%',))
        
        customers = cursor.fetchall()
        self.display_customers(customers)
    
    def clear_search(self):
        """Xóa tìm kiếm và hiển thị tất cả khách hàng"""
        self.search_type.setCurrentText('Tất cả')
        self.search_input.clear()
        self.load_data()
    
    def load_data(self):
        """Tải toàn bộ dữ liệu khách hàng"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers')
        customers = cursor.fetchall()
        self.display_customers(customers)
    
    def display_customers(self, customers):
        """Hiển thị danh sách khách hàng lên table"""
        # Xóa tất cả trước khi thêm mới
        self.table.setRowCount(0)
        self.table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            for col, value in enumerate(customer):
                # Tạo item riêng
                item = QTableWidgetItem(str(value) if value else '')
                
                # KHÔNG CHO CHỌN VÀ CHỈNH SỬA - THÊM DÒNG NÀY
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEditable)
                
                self.table.setItem(row, col, item)
            
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
                    margin-right: 2px;
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
                        margin: 0 3px;
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
                        margin: 0 3px;
                        padding: 3px 0;
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

        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
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
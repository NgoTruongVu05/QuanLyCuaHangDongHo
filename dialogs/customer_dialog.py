from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                             QPushButton, QMessageBox)

class CustomerDialog(QDialog):
    def __init__(self, db, customer_id=None):
        super().__init__()
        self.db = db
        self.customer_id = customer_id
        self.init_ui()
        if customer_id:
            self.load_customer_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa khách hàng' if not self.customer_id else 'Sửa khách hàng')
        self.setFixedSize(400, 250)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        layout.addRow('Tên khách hàng:', self.name_input)
        
        self.phone_input = QLineEdit()
        layout.addRow('Điện thoại:', self.phone_input)
        
        self.email_input = QLineEdit()
        layout.addRow('Email:', self.email_input)
        
        self.address_input = QLineEdit()
        layout.addRow('Địa chỉ:', self.address_input)
        
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_customer)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
    
    def load_customer_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = ?', (self.customer_id,))
        customer = cursor.fetchone()
        
        if customer:
            self.name_input.setText(customer[1])
            self.phone_input.setText(customer[2] if customer[2] else '')
            self.email_input.setText(customer[3] if customer[3] else '')
            self.address_input.setText(customer[4] if customer[4] else '')
    
    def save_customer(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        address = self.address_input.text()
        
        if not name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập tên khách hàng!')
            return
        
        cursor = self.db.conn.cursor()
        if self.customer_id:
            cursor.execute('''
                UPDATE customers SET name=?, phone=?, email=?, address=?
                WHERE id=?
            ''', (name, phone, email, address, self.customer_id))
        else:
            cursor.execute('''
                INSERT INTO customers (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, email, address))
        
        self.db.conn.commit()
        self.accept()
from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                             QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout,
                             QSpacerItem, QSizePolicy)

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
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow('Tên khách hàng:', self.name_input)
        
        self.phone_input = QLineEdit()
        form_layout.addRow('Điện thoại:', self.phone_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow('Email:', self.email_input)
        
        self.address_input = QLineEdit()
        form_layout.addRow('Địa chỉ:', self.address_input)

        # button as instance so it can be accessed elsewhere if needed
        self.save_btn = QPushButton('Lưu')
        self.save_btn.clicked.connect(self.save_customer)

        # main vertical layout: form on top, spacer expands, button row at bottom centered
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        main_layout.addLayout(btn_row)
        
        self.setLayout(main_layout)
    
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
        
        if phone and not self.is_valid_phone(phone):
            QMessageBox.warning(self, 'Lỗi', 'Số điện thoại không hợp lệ! Vui lòng nhập số điện thoại Việt Nam (10-11 chữ số, bắt đầu bằng 0 hoặc +84).')
            return
        
        # Validate email
        if email and not self.is_valid_email(email):
            QMessageBox.warning(self, 'Lỗi', 'Email không hợp lệ! Vui lòng nhập đúng định dạng email.')
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

    def is_valid_phone(self, phone):
        """
        Validate Vietnamese phone numbers
        Formats: 
        - 0xxxxxxxxx (10 digits)
        - 0xxxxxxxxxx (11 digits) 
        - +84xxxxxxxxx (11 digits with country code)
        - +84xxxxxxxxxx (12 digits with country code)
        """
        import re
        
        # Remove spaces and special characters
        phone = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check for Vietnamese phone number patterns
        patterns = [
            r'^0[3|5|7|8|9][0-9]{8}$',  # 10 digits starting with 0
            r'^0[3|5|7|8|9][0-9]{9}$',  # 11 digits starting with 0
            r'^\+84[3|5|7|8|9][0-9]{8}$',  # 11 digits with +84
            r'^\+84[3|5|7|8|9][0-9]{9}$',  # 12 digits with +84
            r'^84[3|5|7|8|9][0-9]{8}$',   # 11 digits with 84 (without +)
            r'^84[3|5|7|8|9][0-9]{9}$'    # 12 digits with 84 (without +)
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)

    def is_valid_email(self, email):
        """
        Validate email format using regex
        """
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
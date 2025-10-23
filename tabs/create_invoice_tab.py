from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QComboBox, QSpinBox, 
                             QGroupBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import QDate

class CreateInvoiceTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id  # Có thể là None nếu chưa đăng nhập
        self.cart = []
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left side - Product selection
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Product selection
        product_group = QGroupBox('Chọn sản phẩm')
        product_layout = QFormLayout()
        
        self.product_combo = QComboBox()
        self.load_products()
        product_layout.addRow('Sản phẩm:', self.product_combo)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        product_layout.addRow('Số lượng:', self.quantity_spin)
        
        add_to_cart_btn = QPushButton('Thêm')
        add_to_cart_btn.clicked.connect(self.add_to_cart)
        product_layout.addRow(add_to_cart_btn)
        
        product_group.setLayout(product_layout)
        left_layout.addWidget(product_group)
        
        # Customer info
        customer_group = QGroupBox('Thông tin khách hàng')
        customer_layout = QFormLayout()
        
        self.customer_combo = QComboBox()
        self.load_customers()
        customer_layout.addRow('Khách hàng:', self.customer_combo)
        
        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)
        
        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)
        
        # Right side - Cart
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(['Sản phẩm', 'Đơn giá', 'Số lượng', 'Thành tiền'])
        right_layout.addWidget(QLabel('Giỏ hàng:'))
        right_layout.addWidget(self.cart_table)
        
        # Total and create invoice
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel('Tổng cộng:'))
        self.total_label = QLabel('0 VND')
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        
        create_invoice_btn = QPushButton('Tạo hóa đơn')
        create_invoice_btn.clicked.connect(self.create_invoice)
        total_layout.addWidget(create_invoice_btn)
        
        right_layout.addLayout(total_layout)
        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)
        
        self.setLayout(layout)
    
    def load_products(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, name, price FROM products WHERE quantity > 0')
        products = cursor.fetchall()
        
        self.product_combo.clear()
        for product in products:
            self.product_combo.addItem(f"{product[1]} - {product[2]:,} VND", product[0])
    
    def load_customers(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, name FROM customers')
        customers = cursor.fetchall()
        
        self.customer_combo.clear()
        self.customer_combo.addItem('Khách lẻ', -1)
        for customer in customers:
            self.customer_combo.addItem(customer[1], customer[0])
    
    def add_to_cart(self):
        product_id = self.product_combo.currentData()
        product_name = self.product_combo.currentText().split(' - ')[0]
        price = float(self.product_combo.currentText().split(' - ')[1].replace(' VND', '').replace(',', ''))
        quantity = self.quantity_spin.value()
        
        # Check if product already in cart
        for i, item in enumerate(self.cart):
            if item['id'] == product_id:
                self.cart[i]['quantity'] += quantity
                self.update_cart_display()
                return
        
        # Add new item to cart
        self.cart.append({
            'id': product_id,
            'name': product_name,
            'price': price,
            'quantity': quantity
        })
        
        self.update_cart_display()
    
    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        
        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:,} VND"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            
            item_total = item['price'] * item['quantity']
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item_total:,} VND"))
            total += item_total
        
        self.total_label.setText(f"{total:,} VND")
    
    def create_invoice(self):
        if not self.cart:
            QMessageBox.warning(self, 'Lỗi', 'Giỏ hàng trống!')
            return
        
        # Nếu chưa đăng nhập, sử dụng employee_id mặc định (1 - admin)
        employee_id = self.user_id if self.user_id else 1
        
        customer_id = self.customer_combo.currentData()
        if customer_id == -1:
            customer_id = None
        
        cursor = self.db.conn.cursor()
        
        # Create invoice
        total_amount = sum(item['price'] * item['quantity'] for item in self.cart)
        cursor.execute('''
            INSERT INTO invoices (customer_id, employee_id, total_amount, created_date)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, employee_id, total_amount, QDate.currentDate().toString('yyyy-MM-dd')))
        
        invoice_id = cursor.lastrowid
        
        # Add invoice details and update product quantities
        for item in self.cart:
            cursor.execute('''
                INSERT INTO invoice_details (invoice_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (invoice_id, item['id'], item['quantity'], item['price']))
            
            # Update product quantity
            cursor.execute('''
                UPDATE products SET quantity = quantity - ? WHERE id = ?
            ''', (item['quantity'], item['id']))
        
        self.db.conn.commit()
        
        QMessageBox.information(self, 'Thành công', f'Hóa đơn #{invoice_id} đã được tạo!')
        self.cart.clear()
        self.update_cart_display()
        self.load_products()
    
    def load_data(self):
        """Reload all data from database"""
        self.load_products()
        self.load_customers()
        self.cart.clear()
        self.update_cart_display()
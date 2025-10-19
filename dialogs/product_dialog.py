from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                             QPushButton, QDoubleSpinBox, QSpinBox, 
                             QMessageBox)

class ProductDialog(QDialog):
    def __init__(self, db, product_id=None):
        super().__init__()
        self.db = db
        self.product_id = product_id
        self.init_ui()
        if product_id:
            self.load_product_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa sản phẩm' if not self.product_id else 'Sửa sản phẩm')
        self.setFixedSize(400, 300)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        layout.addRow('Tên sản phẩm:', self.name_input)
        
        self.brand_input = QLineEdit()
        layout.addRow('Thương hiệu:', self.brand_input)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999999)
        self.price_input.setPrefix('VND ')
        layout.addRow('Giá:', self.price_input)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMaximum(9999)
        layout.addRow('Số lượng:', self.quantity_input)
        
        self.description_input = QLineEdit()
        layout.addRow('Mô tả:', self.description_input)
        
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_product)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
    
    def load_product_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (self.product_id,))
        product = cursor.fetchone()
        
        if product:
            self.name_input.setText(product[1])
            self.brand_input.setText(product[2])
            self.price_input.setValue(product[3])
            self.quantity_input.setValue(product[4])
            self.description_input.setText(product[5] if product[5] else '')
    
    def save_product(self):
        name = self.name_input.text()
        brand = self.brand_input.text()
        price = self.price_input.value()
        quantity = self.quantity_input.value()
        description = self.description_input.text()
        
        if not name or not brand:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin!')
            return
        
        cursor = self.db.conn.cursor()
        if self.product_id:
            cursor.execute('''
                UPDATE products SET name=?, brand=?, price=?, quantity=?, description=?
                WHERE id=?
            ''', (name, brand, price, quantity, description, self.product_id))
        else:
            cursor.execute('''
                INSERT INTO products (name, brand, price, quantity, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, brand, price, quantity, description))
        
        self.db.conn.commit()
        self.accept()
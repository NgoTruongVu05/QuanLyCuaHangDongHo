from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox)
from dialogs.product_dialog import ProductDialog

class ProductManagementTab(QWidget):
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
        
        add_btn = QPushButton('Thêm sản phẩm')
        add_btn.clicked.connect(self.add_product)
        controls_layout.addWidget(add_btn)
        
        edit_btn = QPushButton('Sửa sản phẩm')
        edit_btn.clicked.connect(self.edit_product)
        controls_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('Xóa sản phẩm')
        delete_btn.clicked.connect(self.delete_product)
        controls_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Thương hiệu', 'Giá', 'Số lượng', 'Mô tả'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, value in enumerate(product):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def add_product(self):
        dialog = ProductDialog(self.db)
        if dialog.exec():
            self.load_data()
    
    def edit_product(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn sản phẩm để sửa!')
            return
        
        product_id = int(self.table.item(selected, 0).text())
        dialog = ProductDialog(self.db, product_id)
        if dialog.exec():
            self.load_data()
    
    def delete_product(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn sản phẩm để xóa!')
            return
        
        product_id = int(self.table.item(selected, 0).text())
        product_name = self.table.item(selected, 1).text()
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa sản phẩm "{product_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            self.db.conn.commit()
            self.load_data()
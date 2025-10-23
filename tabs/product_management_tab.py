from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView)
from PyQt6.QtCore import Qt

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
        
        if self.user_role == 1:
            add_btn = QPushButton('Thêm sản phẩm')
            add_btn.clicked.connect(self.add_product)
            controls_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Table - Thêm cột hành động
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Thêm 1 cột cho nút xóa
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Thương hiệu', 'Loại', 'Giá', 'Số lượng', 'Mô tả', 'Thông số', 'Hành động'])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Thương hiệu
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Loại
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Giá
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Số lượng
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Mô tả
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Thông số
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, value in enumerate(product):
                if col == 3:  # Product type
                    type_text = "Đồng hồ cơ" if value == "mechanical" else "Đồng hồ điện tử"
                    self.table.setItem(row, col, QTableWidgetItem(type_text))
                elif col == 4:  # Price
                    self.table.setItem(row, col, QTableWidgetItem(f"{value:,.0f} VND"))
                elif col == 7:  # Additional info
                    if product[3] == "mechanical":
                        info = f"{product[7] or 'Automatic'}, {product[8] or 0}h"
                        if product[9]:
                            info += ", Chống nước"
                    else:
                        info = f"{product[10] or 0} tháng, {product[12] or 'Không'}"
                    self.table.setItem(row, col, QTableWidgetItem(info))
                else:
                    self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ''))
            
            # Nút sửa và xóa cho từng dòng
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            if self.user_role == 1:  # Chỉ admin mới có nút sửa/xóa
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
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_product_row(r))
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
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_product_row(r))
                action_layout.addWidget(delete_btn)
            else:
                # Nhân viên chỉ xem
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
                view_btn.clicked.connect(lambda checked, r=row: self.view_product_row(r))
                action_layout.addWidget(view_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 8, action_widget)
    
    def add_product(self):
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db)
        if dialog.exec():
            # Tự động cập nhật bảng sau khi thêm
            self.load_data()
            # Thông báo thành công
            QMessageBox.information(self, 'Thành công', 'Đã thêm sản phẩm mới!')
    
    def edit_product_row(self, row):
        product_id = int(self.table.item(row, 0).text())
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db, product_id)
        if dialog.exec():
            # Tự động cập nhật bảng sau khi sửa
            self.load_data()
            # Thông báo thành công
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật sản phẩm!')
    
    def delete_product_row(self, row):
        product_id = int(self.table.item(row, 0).text())
        product_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa sản phẩm "{product_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            self.db.conn.commit()
<<<<<<< HEAD
            self.load_data()
    
    def view_product_row(self, row):
        product_id = int(self.table.item(row, 0).text())
        product_name = self.table.item(row, 1).text()
        brand = self.table.item(row, 2).text()
        product_type = self.table.item(row, 3).text()
        price = self.table.item(row, 4).text()
        quantity = self.table.item(row, 5).text()
        description = self.table.item(row, 6).text()
        specs = self.table.item(row, 7).text()
        
        info_text = f"""
        Thông tin sản phẩm:
        
        ID: {product_id}
        Tên: {product_name}
        Thương hiệu: {brand}
        Loại: {product_type}
        Giá: {price}
        Số lượng: {quantity}
        Mô tả: {description}
        Thông số: {specs}
        """
        
        QMessageBox.information(self, 'Chi tiết sản phẩm', info_text)
=======
            # Tự động cập nhật bảng sau khi xóa
            self.load_data()
            # Thông báo thành công
            QMessageBox.information(self, 'Thành công', 'Đã xóa sản phẩm!')
>>>>>>> e7fdcec20bc832cb76df73ca6e14f621b3b27e81

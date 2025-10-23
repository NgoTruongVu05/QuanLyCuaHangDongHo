from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QHeaderView, QDialog, QFormLayout, QLineEdit)

class BrandDialog(QDialog):
    def __init__(self, db, brand_id=None):
        super().__init__()
        self.db = db
        self.brand_id = brand_id
        self.init_ui()
        if brand_id:
            self.load_brand_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa thương hiệu')
        self.setFixedSize(400, 200)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        layout.addRow('Tên thương hiệu:', self.name_input)
        
        self.country_input = QLineEdit()
        layout.addRow('Quốc gia:', self.country_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_brand)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def load_brand_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name, country FROM brands WHERE id = ?', (self.brand_id,))
        brand = cursor.fetchone()
        
        if brand:
            self.name_input.setText(brand[0])
            self.country_input.setText(brand[1] if brand[1] else '')
    
    def save_brand(self):
        name = self.name_input.text().strip()
        country = self.country_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập tên thương hiệu!')
            return
        
        cursor = self.db.conn.cursor()
        
        if self.brand_id:
            cursor.execute('UPDATE brands SET name=?, country=? WHERE id=?', 
                         (name, country, self.brand_id))
        else:
            cursor.execute('INSERT INTO brands (name, country) VALUES (?, ?)', 
                         (name, country))
        
        self.db.conn.commit()
        self.accept()

class BrandManagementTab(QWidget):
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
        
        if self.user_role == 1:  # Chỉ admin mới được thêm thương hiệu
            add_btn = QPushButton('Thêm thương hiệu')
            add_btn.clicked.connect(self.add_brand)
            controls_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # ID, Tên, Quốc gia, Hành động
        self.table.setHorizontalHeaderLabels(['ID', 'Tên thương hiệu', 'Quốc gia', 'Hành động'])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Quốc gia
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM brands ORDER BY id')
        brands = cursor.fetchall()
        
        self.table.setRowCount(len(brands))
        for row, brand in enumerate(brands):
            # ID, Tên, Quốc gia
            for col in range(3):
                self.table.setItem(row, col, QTableWidgetItem(str(brand[col] or '')))
            
            # Nút hành động
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
                        margin-right: 2px;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                ''')
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_brand_row(r))
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
                        margin: 0 3px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_brand_row(r))
                action_layout.addWidget(delete_btn)
            
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 3, action_widget)
            self.table.resizeRowsToContents()
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def add_brand(self):
        dialog = BrandDialog(self.db)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm thương hiệu mới!')
    
    def edit_brand_row(self, row):
        brand_id = int(self.table.item(row, 0).text())
        dialog = BrandDialog(self.db, brand_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật thương hiệu!')
    
    def delete_brand_row(self, row):
        brand_id = int(self.table.item(row, 0).text())
        brand_name = self.table.item(row, 1).text()
        
        # Kiểm tra xem thương hiệu có sản phẩm không
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products WHERE brand_id = ?', (brand_id,))
        product_count = cursor.fetchone()[0]
        
        if product_count > 0:
            QMessageBox.warning(self, 'Lỗi', 
                              f'Không thể xóa thương hiệu "{brand_name}" vì có {product_count} sản phẩm đang sử dụng!')
            return
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa thương hiệu "{brand_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor.execute('DELETE FROM brands WHERE id = ?', (brand_id,))
            self.db.conn.commit()
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã xóa thương hiệu!')
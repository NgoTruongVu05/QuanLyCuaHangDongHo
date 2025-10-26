from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton,
                             QDoubleSpinBox, QSpinBox, QMessageBox, QComboBox,
                             QCheckBox, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel)
from PyQt6.QtGui import QDoubleValidator

class ProductDialog(QDialog):
    def __init__(self, db, product_id=None):
        super().__init__()
        self.db = db
        self.product_id = product_id
        self.product_type = "mechanical"
        self.init_ui()
        if product_id:
            self.load_product_data()

    def _format_input(self, line_edit):
        text = line_edit.text()
        if text:
            try:
                num = float(text.replace('.', ''))
                formatted = f"{num:,.0f}".replace(',', '.')
                if formatted != text:
                    line_edit.setText(formatted)
                    line_edit.setCursorPosition(len(formatted))
            except ValueError:
                pass
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa sản phẩm' if not self.product_id else 'Sửa sản phẩm')
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Basic info
        basic_group = QGroupBox('Thông tin cơ bản')
        basic_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        basic_layout.addRow('Tên sản phẩm:', self.name_input)
        
        # Replace LineEdit with ComboBox for brands
        self.brand_combo = QComboBox()
        self.load_brands()  # Load brands from database
        basic_layout.addRow('Thương hiệu:', self.brand_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Đồng hồ cơ', 'Đồng hồ điện tử'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        basic_layout.addRow('Loại đồng hồ:', self.type_combo)
        
        # Price input with VND label
        price_layout = QHBoxLayout()
        self.price_input = QLineEdit()
        self.price_input.setMaxLength(20)  # Allow more for dots
        self.price_input.textChanged.connect(lambda: self._format_input(self.price_input))
        price_label = QLabel('VND')
        price_layout.addWidget(self.price_input)
        price_layout.addWidget(price_label)
        price_layout.addStretch()
        basic_layout.addRow('Giá:', price_layout)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)  # Prevent negative values
        self.quantity_input.setMaximum(100)  # Maximum 100 units per product
        basic_layout.addRow('Số lượng:', self.quantity_input)
        
        self.description_input = QLineEdit()
        basic_layout.addRow('Mô tả:', self.description_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Mechanical watch specific
        self.mech_group = QGroupBox('Thông số đồng hồ cơ')
        mech_layout = QFormLayout()
        
        self.movement_combo = QComboBox()
        self.movement_combo.addItems(['Automatic', 'Manual'])
        mech_layout.addRow('Loại máy:', self.movement_combo)
        
        # Power reserve input with hours label
        power_reserve_layout = QHBoxLayout()
        self.power_reserve_input = QSpinBox()
        self.power_reserve_input.setMinimum(30)
        self.power_reserve_input.setMaximum(999)
        power_reserve_label = QLabel('giờ')
        power_reserve_layout.addWidget(self.power_reserve_input)
        power_reserve_layout.addWidget(power_reserve_label)
        power_reserve_layout.addStretch()
        mech_layout.addRow('Dự trữ năng lượng:', power_reserve_layout)
        
        self.water_resistant_check = QCheckBox('Chống nước')
        mech_layout.addRow(self.water_resistant_check)
        
        self.mech_group.setLayout(mech_layout)
        layout.addWidget(self.mech_group)
        
        # Electronic watch specific
        self.elec_group = QGroupBox('Thông số đồng hồ điện tử')
        elec_layout = QFormLayout()
        
        # Battery life input with hours label
        battery_life_layout = QHBoxLayout()
        self.battery_life_input = QSpinBox()
        self.battery_life_input.setMaximum(99)
        battery_life_label = QLabel('năm')
        battery_life_layout.addWidget(self.battery_life_input)
        battery_life_layout.addWidget(battery_life_label)
        battery_life_layout.addStretch()
        elec_layout.addRow('Thời lượng pin:', battery_life_layout)
        
        self.features_layout = QVBoxLayout()
        self.heart_rate_check = QCheckBox('Theo dõi nhịp tim')
        self.gps_check = QCheckBox('GPS')
        self.steps_check = QCheckBox('Đếm bước chân')
        self.sleep_check = QCheckBox('Theo dõi giấc ngủ')
        
        self.features_layout.addWidget(self.heart_rate_check)
        self.features_layout.addWidget(self.gps_check)
        self.features_layout.addWidget(self.steps_check)
        self.features_layout.addWidget(self.sleep_check)
        
        features_group = QGroupBox('Tính năng')
        features_group.setLayout(self.features_layout)
        elec_layout.addRow(features_group)
        
        self.connectivity_combo = QComboBox()
        self.connectivity_combo.addItems(['Không', 'Bluetooth', 'WiFi', 'Cả hai'])
        elec_layout.addRow('Kết nối:', self.connectivity_combo)
        
        self.elec_group.setLayout(elec_layout)
        layout.addWidget(self.elec_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_product)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.on_type_changed('Đồng hồ cơ')
    
    def on_type_changed(self, product_type):
        if product_type == 'Đồng hồ cơ':
            self.product_type = "mechanical"
            self.mech_group.show()
            self.elec_group.hide()
        else:
            self.product_type = "electronic"
            self.mech_group.hide()
            self.elec_group.show()
    
    def load_brands(self):
        """Load brands from database into combo box"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM brands ORDER BY name')
        brands = cursor.fetchall()
        self.brand_combo.clear()
        for brand in brands:
            self.brand_combo.addItem(brand[0])
    
    def load_product_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.*, b.name as brand_name 
            FROM products p
            JOIN brands b ON p.brand_id = b.id
            WHERE p.id = ?
        ''', (self.product_id,))
        product_data = cursor.fetchone()
        
        if product_data:
            # Basic info
            self.name_input.setText(product_data[1])
            self.brand_combo.setCurrentText(product_data[-1])  # Set brand from joined query
            self.price_input.setText(f"{product_data[4]:,.0f}".replace(',', '.'))
            self.quantity_input.setValue(product_data[5])
            self.description_input.setText(product_data[6] if product_data[6] else '')
            
            # Set product type
            if product_data[3] == "mechanical":
                self.type_combo.setCurrentText('Đồng hồ cơ')
                self.movement_combo.setCurrentText(product_data[7] if product_data[7] else 'Automatic')
                self.power_reserve_input.setValue(product_data[8] if product_data[8] else 0)
                self.water_resistant_check.setChecked(bool(product_data[9]))
            else:
                self.type_combo.setCurrentText('Đồng hồ điện tử')
                self.battery_life_input.setValue(product_data[10] if product_data[10] else 0)
                
                # Features
                features = product_data[11].split(',') if product_data[11] else []
                self.heart_rate_check.setChecked('heart_rate' in features)
                self.gps_check.setChecked('gps' in features)
                self.steps_check.setChecked('steps' in features)
                self.sleep_check.setChecked('sleep' in features)
                
                self.connectivity_combo.setCurrentText(product_data[12] if product_data[12] else 'Không')
    
    def save_product(self):
        name = self.name_input.text()
        brand = self.brand_combo.currentText()
        
        # Get brand_id from selected brand name
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id FROM brands WHERE name = ?', (brand,))
        brand_id = cursor.fetchone()[0]
        
        try:
            price_text = self.price_input.text().replace('.', '')
            price = float(price_text)
        except ValueError:
            QMessageBox.warning(self, 'Lỗi', 'Giá phải là số hợp lệ!')
            return
        quantity = self.quantity_input.value()
        description = self.description_input.text()
        
        if not name or not brand:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin!')
            return
        
        cursor = self.db.conn.cursor()
        
        if self.product_type == "mechanical":
            movement_type = self.movement_combo.currentText().lower()
            power_reserve = self.power_reserve_input.value()
            water_resistant = 1 if self.water_resistant_check.isChecked() else 0
            
            if self.product_id:
                cursor.execute('''
                    UPDATE products SET name=?, brand_id=?, product_type=?, price=?, quantity=?, description=?,
                    movement_type=?, power_reserve=?, water_resistant=?, battery_life=NULL, features=NULL, connectivity=NULL
                    WHERE id=?
                ''', (name, brand_id, self.product_type, price, quantity, description,
                     movement_type, power_reserve, water_resistant, self.product_id))
            else:
                cursor.execute('''
                    INSERT INTO products (name, brand_id, product_type, price, quantity, description,
                    movement_type, power_reserve, water_resistant)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, brand_id, self.product_type, price, quantity, description,
                     movement_type, power_reserve, water_resistant))
        
        else:  # electronic
            battery_life = self.battery_life_input.value()
            connectivity = self.connectivity_combo.currentText()
            
            features = []
            if self.heart_rate_check.isChecked(): features.append('heart_rate')
            if self.gps_check.isChecked(): features.append('gps')
            if self.steps_check.isChecked(): features.append('steps')
            if self.sleep_check.isChecked(): features.append('sleep')
            features_str = ','.join(features)
            
            if self.product_id:
                cursor.execute('''
                    UPDATE products SET name=?, brand_id=?, product_type=?, price=?, quantity=?, description=?,
                    movement_type=NULL, power_reserve=NULL, water_resistant=NULL, battery_life=?, features=?, connectivity=?
                    WHERE id=?
                ''', (name, brand_id, self.product_type, price, quantity, description,
                     battery_life, features_str, connectivity, self.product_id))
            else:
                cursor.execute('''
                    INSERT INTO products (name, brand_id, product_type, price, quantity, description,
                    battery_life, features, connectivity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, brand_id, self.product_type, price, quantity, description,
                     battery_life, features_str, connectivity))
        
        self.db.conn.commit()
        self.accept()
from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QDoubleSpinBox, QSpinBox, QMessageBox, QComboBox,
                             QCheckBox, QVBoxLayout, QGroupBox, QHBoxLayout)

class ProductDialog(QDialog):
    def __init__(self, db, product_id=None):
        super().__init__()
        self.db = db
        self.product_id = product_id
        self.product_type = "mechanical"
        self.init_ui()
        if product_id:
            self.load_product_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa sản phẩm' if not self.product_id else 'Sửa sản phẩm')
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Basic info
        basic_group = QGroupBox('Thông tin cơ bản')
        basic_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        basic_layout.addRow('Tên sản phẩm:', self.name_input)
        
        self.brand_input = QLineEdit()
        basic_layout.addRow('Thương hiệu:', self.brand_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Đồng hồ cơ', 'Đồng hồ điện tử'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        basic_layout.addRow('Loại đồng hồ:', self.type_combo)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999999)
        self.price_input.setPrefix('VND ')
        basic_layout.addRow('Giá:', self.price_input)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMaximum(9999)
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
        
        self.power_reserve_input = QSpinBox()
        self.power_reserve_input.setMaximum(500)
        self.power_reserve_input.setSuffix(' giờ')
        mech_layout.addRow('Dự trữ năng lượng:', self.power_reserve_input)
        
        self.water_resistant_check = QCheckBox('Chống nước')
        mech_layout.addRow(self.water_resistant_check)
        
        self.mech_group.setLayout(mech_layout)
        layout.addWidget(self.mech_group)
        
        # Electronic watch specific
        self.elec_group = QGroupBox('Thông số đồng hồ điện tử')
        elec_layout = QFormLayout()
        
        self.battery_life_input = QSpinBox()
        self.battery_life_input.setMaximum(60)
        self.battery_life_input.setSuffix(' tháng')
        elec_layout.addRow('Thời lượng pin:', self.battery_life_input)
        
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
    
    def load_product_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (self.product_id,))
        product_data = cursor.fetchone()
        
        if product_data:
            # Basic info
            self.name_input.setText(product_data[1])
            self.brand_input.setText(product_data[2])
            self.price_input.setValue(product_data[4])
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
        brand = self.brand_input.text()
        price = self.price_input.value()
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
                    UPDATE products SET name=?, brand=?, product_type=?, price=?, quantity=?, description=?,
                    movement_type=?, power_reserve=?, water_resistant=?, battery_life=NULL, features=NULL, connectivity=NULL
                    WHERE id=?
                ''', (name, brand, self.product_type, price, quantity, description,
                     movement_type, power_reserve, water_resistant, self.product_id))
            else:
                cursor.execute('''
                    INSERT INTO products (name, brand, product_type, price, quantity, description,
                    movement_type, power_reserve, water_resistant)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, brand, self.product_type, price, quantity, description,
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
                    UPDATE products SET name=?, brand=?, product_type=?, price=?, quantity=?, description=?,
                    movement_type=NULL, power_reserve=NULL, water_resistant=NULL, battery_life=?, features=?, connectivity=?
                    WHERE id=?
                ''', (name, brand, self.product_type, price, quantity, description,
                     battery_life, features_str, connectivity, self.product_id))
            else:
                cursor.execute('''
                    INSERT INTO products (name, brand, product_type, price, quantity, description,
                    battery_life, features, connectivity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, brand, self.product_type, price, quantity, description,
                     battery_life, features_str, connectivity))
        
        self.db.conn.commit()
        self.accept()
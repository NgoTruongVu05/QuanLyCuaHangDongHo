from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QLabel, QDialog, QDialogButtonBox,
                             QTextEdit, QSizePolicy, QLineEdit, QComboBox,
                             QGraphicsDropShadowEffect, QScrollArea, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QFont

class ProductManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.products = []  # Lưu products khi load_data để lấy info khi cần
        self.proxy_model = None  # For sorting and filtering
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel('Tìm kiếm:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập tên sản phẩm hoặc thương hiệu...')
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Filters
        filter_layout = QHBoxLayout()
        brand_label = QLabel('Thương hiệu:')
        self.brand_filter = QComboBox()
        self.brand_filter.addItem('Tất cả')
        self.brand_filter.currentTextChanged.connect(self.filter_products)

        type_label = QLabel('Loại:')
        self.type_filter = QComboBox()
        self.type_filter.addItems(['Tất cả', 'Đồng hồ cơ', 'Đồng hồ điện tử'])
        self.type_filter.currentTextChanged.connect(self.filter_products)

        price_min_label = QLabel('Giá từ:')
        self.price_min_input = QLineEdit()
        self.price_min_input.setPlaceholderText('VNĐ')
        self.price_min_input.textChanged.connect(self.filter_products)

        price_max_label = QLabel('đến:')
        self.price_max_input = QLineEdit()
        self.price_max_input.setPlaceholderText('VNĐ')
        self.price_max_input.textChanged.connect(self.filter_products)

        filter_layout.addWidget(brand_label)
        filter_layout.addWidget(self.brand_filter)
        filter_layout.addWidget(type_label)
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(price_min_label)
        filter_layout.addWidget(self.price_min_input)
        filter_layout.addWidget(price_max_label)
        filter_layout.addWidget(self.price_max_input)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Advanced filters
        advanced_layout = QHBoxLayout()
        self.power_reserve_label = QLabel('Thời gian trữ cót  (h):')
        self.power_reserve_input = QLineEdit()
        self.power_reserve_input.setPlaceholderText('Min')
        self.power_reserve_input.textChanged.connect(self.filter_products)

        self.battery_life_label = QLabel('Thời lượng pin (tháng):')
        self.battery_life_input = QLineEdit()
        self.battery_life_input.setPlaceholderText('Min')
        self.battery_life_input.textChanged.connect(self.filter_products)

        self.connectivity_label = QLabel('Kết nối:')
        self.connectivity_filter = QComboBox()
        self.connectivity_filter.addItems(['Tất cả', 'Bluetooth', 'Wi-Fi', 'GPS', 'NFC'])
        self.connectivity_filter.currentTextChanged.connect(self.filter_products)

        advanced_layout.addWidget(self.power_reserve_label)
        advanced_layout.addWidget(self.power_reserve_input)
        advanced_layout.addWidget(self.battery_life_label)
        advanced_layout.addWidget(self.battery_life_input)
        advanced_layout.addWidget(self.connectivity_label)
        advanced_layout.addWidget(self.connectivity_filter)
        advanced_layout.addStretch()
        layout.addLayout(advanced_layout)

        # Connect type filter to update advanced filters visibility
        self.type_filter.currentTextChanged.connect(self.update_advanced_filters_visibility)
        self.update_advanced_filters_visibility()  # Initial setup

        # Controls
        controls_layout = QHBoxLayout()

        if self.user_role == 1:
            add_btn = QPushButton('Thêm sản phẩm')
            add_btn.setIcon(QIcon())  # Add icon if available
            add_btn.setStyleSheet('''
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            ''')
            add_btn.clicked.connect(self.add_product)
            controls_layout.addWidget(add_btn)



        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Table settings
        self.table = QTableWidget()
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        # --- Thay đổi: chỉ còn 8 cột (gộp mô tả + thông số thành "Chi tiết sản phẩm") ---
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Thương hiệu', 'Loại', 'Giá', 'Số lượng', 'Chi tiết sản phẩm', 'Hành động'])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Thương hiệu
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Loại
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Giá
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Số lượng
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Chi tiết sản phẩm (mô tả + thông số)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Hành động

        # Enable sorting
        self.table.setSortingEnabled(True)

        # Allow deselection by clicking empty area
        self.table.clicked.connect(self.handle_click)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def _create_qty_widget(self, quantity: int):
        qty_widget = QWidget()
        layout = QHBoxLayout(qty_widget)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        qty_label = QLabel(str(quantity))
        qty_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        qty_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 600;
                font-size: 13px;
                padding: 2px 0px;
            }
        """)
        layout.addWidget(qty_label)
        layout.addStretch()

        badge_label = QLabel()
        badge_label.setFixedHeight(20)
        badge_label.setFixedWidth(42)
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 60))
        badge_label.setGraphicsEffect(shadow)

        if quantity <= 2:
            badge_label.setText(f"⚠ {quantity}")
            badge_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF6B6B, stop:1 #E74C3C);
                    color: white;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 1px 4px;
                    border: 1px solid #C0392B;
                }
                QLabel:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF7979, stop:1 #FF6B6B);
                }
            """)
        elif quantity <= 5:
            badge_label.setText(f"⚠ {quantity}")
            badge_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FFA726, stop:1 #F39C12);
                    color: #2C3E50;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 1px 4px;
                    border: 1px solid #E67E22;
                }
                QLabel:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FFB74D, stop:1 #FFA726);
                }
            """)
        else:
            badge_label.hide()

        layout.addWidget(badge_label)

        if quantity <= 5:
            if quantity <= 2:
                tooltip_text = f"Cảnh báo: Chỉ còn {quantity} sản phẩm - Sắp hết hàng!"
            else:
                tooltip_text = f"Cảnh báo: Chỉ còn {quantity} sản phẩm - Số lượng thấp"
            qty_widget.setToolTip(tooltip_text)
            badge_label.setToolTip(tooltip_text)

        return qty_widget

    def load_data(self):
        """
        Lấy dữ liệu sản phẩm kèm tên brand qua JOIN,
        rồi fill vào 8 cột của table: ID, Tên, Thương hiệu, Loại, Giá, Số lượng, Chi tiết sản phẩm, Hành động
        """
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, b.name AS brand, p.product_type, p.price, p.quantity,
                   p.description, p.movement_type, p.power_reserve, p.water_resistant,
                   p.battery_life, p.features, p.connectivity
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.id
            ORDER BY p.id
        ''')
        products = cursor.fetchall()
        # Lưu lại danh sách products để dùng khi hiển thị dialog
        self.products = products

        # Populate brand filter
        brands = set()
        for product in products:
            brand = product[2] or ''
            if brand:
                brands.add(brand)
        self.brand_filter.clear()
        self.brand_filter.addItem('Tất cả')
        for brand in sorted(brands):
            self.brand_filter.addItem(brand)

        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            pid = product[0]
            name = product[1] or ''
            brand = product[2] or ''
            ptype = (product[3] or '').lower()
            price = product[4]
            quantity = product[5] if product[5] is not None else 0
            description = product[6] or ''

            movement_type = product[7] or ''
            power_reserve = product[8]
            water_resistant = product[9]
            battery_life = product[10]
            features = product[11] or ''
            connectivity = product[12] or ''

            # Col 0: ID
            id_item = QTableWidgetItem(str(pid))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, id_item)

            # Col 1: Tên
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, name_item)

            # Col 2: Thương hiệu (tên)
            brand_item = QTableWidgetItem(brand)
            brand_item.setFlags(brand_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, brand_item)

            # Col 3: Loại
            if ptype in ('mechanical', 'm', 'coil'):
                type_text = "Đồng hồ cơ"
            elif ptype in ('digital', 'smart', 'electronic'):
                type_text = "Đồng hồ điện tử"
            else:
                type_text = product[3] or ''
            type_item = QTableWidgetItem(type_text)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, type_item)

            # Col 4: Giá
            if price is None:
                price_text = ''
            else:
                try:
                    price_text = f"{price:,.0f} VND"
                except Exception:
                    price_text = str(price)
            price_item = QTableWidgetItem(price_text)
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 4, price_item)

            # Col 5: Số lượng -> dùng custom widget có badge
            qty_widget = self._create_qty_widget(int(quantity))
            self.table.setCellWidget(row, 5, qty_widget)

            # Col 6: Chi tiết sản phẩm - nút "Xem chi tiết"
            detail_widget = QWidget()
            detail_layout = QHBoxLayout(detail_widget)
            detail_layout.setContentsMargins(5, 2, 5, 2)

            view_detail_btn = QPushButton('Xem chi tiết')
            view_detail_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            view_detail_btn.setStyleSheet('''
                QPushButton {
                    background-color: #2ECC71;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #27AE60;
                }
            ''')
            view_detail_btn.clicked.connect(lambda checked, r=row: self.show_details_dialog(r))
            detail_layout.addWidget(view_detail_btn)
            self.table.setCellWidget(row, 6, detail_widget)

            # Col 7: Action buttons (Sửa, Xóa)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)

            if self.user_role == 1:  # admin: thêm Sửa và Xóa
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
                        margin: 0 3px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_product_row(r))
                action_layout.addWidget(delete_btn)

            action_layout.addStretch()
            self.table.setCellWidget(row, 7, action_widget)

        # Sau khi fill data
        self.table.resizeRowsToContents()
        for r in range(self.table.rowCount()):
            self.table.setRowHeight(r, 40)

    # --- Hiển thị dialog chi tiết ---
    def show_details_dialog(self, row):
        """
        Mở dialog hiển thị mô tả và thông số chi tiết sản phẩm — dark theme.
        """
        if row < 0 or row >= len(self.products):
            return

        prod = self.products[row]
        pid = prod[0]
        name = prod[1] or ''
        brand = prod[2] or ''
        ptype_raw = prod[3] or ''
        description = prod[6] or ''
        movement_type = prod[7] or ''
        power_reserve = prod[8]
        water_resistant = prod[9]
        battery_life = prod[10]
        features = prod[11] or ''
        connectivity = prod[12] or ''

        specs = {}
        if (ptype_raw or '').lower() in ('mechanical', 'm', 'coil'):
            specs['Loại'] = f"Đồng hồ cơ ({movement_type or 'Automatic'})"
            if power_reserve:
                specs['Thời gian trữ cót'] = f"{power_reserve} giờ"
            if water_resistant:
                specs['Chống nước'] = str(water_resistant)
        else:
            specs['Loại'] = ptype_raw or 'Điện tử'
            specs['Thời lượng pin'] = f"{battery_life or 0} tháng"
            if connectivity:
                specs['Kết nối'] = connectivity
        if features:
            specs['Tính năng khác'] = features
        specs['Mã sản phẩm'] = str(pid)

        # --- dialog setup ---
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Chi tiết sản phẩm — {name}")
        dialog.setMinimumWidth(560)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # ----- header -----
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(name)
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #ffffff;")

        brand_label = QLabel(f"<i>{brand}</i>") if brand else QLabel("<i>Thương hiệu: Không rõ</i>")
        brand_label.setTextFormat(Qt.TextFormat.RichText)
        brand_label.setStyleSheet("color: #cccccc;")
        brand_label.setWordWrap(True)

        header_layout.addWidget(title_label)
        header_layout.addWidget(brand_label)
        main_layout.addWidget(header_widget)

        # ----- body (mô tả + thông số) -----
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(12)

        # Mô tả
        desc_container = QScrollArea()
        desc_container.setWidgetResizable(True)
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        desc_layout.setContentsMargins(8, 8, 8, 8)

        desc_label_title = QLabel("<b>Mô tả sản phẩm</b>")
        desc_label_title.setTextFormat(Qt.TextFormat.RichText)
        desc_label_title.setStyleSheet("color: #f0f0f0; font-size: 12.5px;")

        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setAcceptRichText(False)
        desc_text.setPlainText(description or "Không có mô tả.")
        desc_text.setMinimumHeight(160)
        desc_text.setStyleSheet("""
            QTextEdit {
                background-color: #2e2e2e;
                color: #f0f0f0;
                border: 1px solid #505050;
                border-radius: 6px;
                font-size: 12.5px;
                padding: 6px;
            }
        """)

        desc_layout.addWidget(desc_label_title)
        desc_layout.addWidget(desc_text)
        desc_widget.setLayout(desc_layout)
        desc_container.setWidget(desc_widget)
        desc_container.setMinimumWidth(320)
        body_layout.addWidget(desc_container, stretch=2)

        # Thông số kỹ thuật
        specs_container = QScrollArea()
        specs_container.setWidgetResizable(True)
        specs_widget = QWidget()
        specs_layout = QFormLayout(specs_widget)
        specs_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        specs_layout.setHorizontalSpacing(12)
        specs_layout.setVerticalSpacing(8)
        specs_layout.setContentsMargins(8, 8, 8, 8)

        for key, val in specs.items():
            label_key = QLabel(f"{key}:")
            label_key.setStyleSheet("color: #cccccc; font-weight: 500;")
            label_val = QLabel(str(val))
            label_val.setWordWrap(True)
            label_val.setStyleSheet("color: #f0f0f0;")
            specs_layout.addRow(label_key, label_val)

        if not specs:
            specs_layout.addRow(QLabel("Không có thông số kỹ thuật."), QLabel(""))

        specs_widget.setLayout(specs_layout)
        specs_container.setWidget(specs_widget)
        specs_container.setMinimumWidth(220)
        body_layout.addWidget(specs_container, stretch=1)

        main_layout.addWidget(body_widget)

        # ----- footer -----
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet("""
            QPushButton {
                background-color: #3A8DFF;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #5BA3FF;
            }
        """)
        buttons.accepted.connect(dialog.accept)
        main_layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignRight)

        # Tổng thể dialog style
        dialog.setStyleSheet("""
            QDialog {
                background-color: #353535;
                border: 1px solid #505050;
            }
            QLabel {
                font-size: 12.5px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        dialog.exec()
    # --- Các hàm khác giữ nguyên (chỉ sửa view/edit/delete để dùng self.products khi cần) ---
    def add_product(self):
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm sản phẩm mới!')

    def edit_product_row(self, row):
        # Lấy product id từ self.products để đảm bảo đúng (không phụ thuộc row thay đổi)
        if row < 0 or row >= len(self.products):
            return
        product_id = int(self.products[row][0])
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db, product_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật sản phẩm!')

    def delete_product_row(self, row):
        if row < 0 or row >= len(self.products):
            return
        product_id = int(self.products[row][0])
        product_name = self.products[row][1] or ''

        # Check if product has been sold
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM invoice_details WHERE product_id = ?', (product_id,))
        sold_count = cursor.fetchone()[0]

        if sold_count > 0:
            QMessageBox.warning(self, 'Không thể xóa',
                                f'Sản phẩm \"{product_name}\" đã được bán ra và không thể xóa!')
            return

        reply = QMessageBox.question(self, 'Xác nhận',
                                     f'Bạn có chắc muốn xóa sản phẩm \"{product_name}\"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            self.db.conn.commit()
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã xóa sản phẩm!')

    def filter_products(self):
        """
        Filter products based on search input, brand, type, price range, and specifications.
        """
        search_text = self.search_input.text().lower()
        selected_brand = self.brand_filter.currentText()
        selected_type = self.type_filter.currentText()

        # Price filters
        price_min_text = self.price_min_input.text().strip()
        price_max_text = self.price_max_input.text().strip()
        price_min = float(price_min_text.replace(',', '').replace(' VND', '')) if price_min_text else None
        price_max = float(price_max_text.replace(',', '').replace(' VND', '')) if price_max_text else None

        # Advanced filters
        power_reserve_min_text = self.power_reserve_input.text().strip()
        power_reserve_min = float(power_reserve_min_text) if power_reserve_min_text else None

        battery_life_min_text = self.battery_life_input.text().strip()
        battery_life_min = float(battery_life_min_text) if battery_life_min_text else None

        selected_connectivity = self.connectivity_filter.currentText()

        for row in range(self.table.rowCount()):
            if row >= len(self.products):
                continue

            product = self.products[row]
            name = (product[1] or '').lower()
            brand = (product[2] or '').lower()
            ptype_raw = product[3] or ''
            price = product[4] or 0
            power_reserve = product[8] or 0
            battery_life = product[10] or 0
            connectivity = product[12] or ''

            # Determine display type
            if ptype_raw.lower() in ('mechanical', 'm', 'coil'):
                display_type = "Đồng hồ cơ"
            elif ptype_raw.lower() in ('digital', 'smart', 'electronic'):
                display_type = "Đồng hồ điện tử"
            else:
                display_type = ptype_raw

            # Check search
            search_match = not search_text or search_text in name or search_text in brand

            # Check brand
            brand_match = selected_brand == 'Tất cả' or selected_brand.lower() == brand

            # Check type
            type_match = selected_type == 'Tất cả' or selected_type == display_type

            # Check price range
            price_match = True
            if price_min is not None and price < price_min:
                price_match = False
            if price_max is not None and price > price_max:
                price_match = False

            # Check specifications based on type
            spec_match = True
            if display_type == "Đồng hồ cơ":
                if power_reserve_min is not None and power_reserve < power_reserve_min:
                    spec_match = False
            elif display_type == "Đồng hồ điện tử":
                if battery_life_min is not None and battery_life < battery_life_min:
                    spec_match = False
                if selected_connectivity != 'Tất cả' and selected_connectivity not in connectivity:
                    spec_match = False

            if search_match and brand_match and type_match and price_match and spec_match:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def view_product_row(self, row):
        """
        Giữ cho tương thích: mở dialog chi tiết (nếu có)
        """
        self.show_details_dialog(row)

    def update_advanced_filters_visibility(self):
        """
        Update visibility of advanced filters based on selected watch type.
        """
        selected_type = self.type_filter.currentText()

        if selected_type == 'Tất cả':
            # Show all filters
            self.power_reserve_label.show()
            self.power_reserve_input.show()
            self.battery_life_label.show()
            self.battery_life_input.show()
            self.connectivity_label.show()
            self.connectivity_filter.show()
        elif selected_type == 'Đồng hồ cơ':
            # Show only mechanical watch filters
            self.power_reserve_label.show()
            self.power_reserve_input.show()
            self.battery_life_label.hide()
            self.battery_life_input.hide()
            self.connectivity_label.hide()
            self.connectivity_filter.hide()
        elif selected_type == 'Đồng hồ điện tử':
            # Show only digital watch filters
            self.power_reserve_label.hide()
            self.power_reserve_input.hide()
            self.battery_life_label.show()
            self.battery_life_input.show()
            self.connectivity_label.show()
            self.connectivity_filter.show()

    def handle_click(self, index):
        if not index.isValid():
            self.table.clearSelection()
            return

        selected = self.table.selectedItems()
        if selected and selected[0].row() == index.row():
            self.table.clearSelection()

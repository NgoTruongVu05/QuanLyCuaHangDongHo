from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QLabel, QDialog, QDialogButtonBox,
                             QTextEdit, QSizePolicy, QLineEdit, QComboBox,
                             QGraphicsDropShadowEffect, QScrollArea, QFormLayout,
                             QFileDialog, QProgressDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QFont, QIntValidator, QDoubleValidator
import csv
import os

class ProductManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.products = []  # Current page products
        self.page_size = 50  # Items per page
        self.current_page = 1
        self.total_pages = 1
        self.total_products = 0
        self.current_filters = {}  # Store current filter state
        self.init_ui()
        self.load_data()

    def _format_input(self, line_edit):
        text = line_edit.text()
        if text:
            try:
                num = float(text.replace(',', ''))
                formatted = f"{num:,.0f}"
                if formatted != text:
                    line_edit.setText(formatted)
                    line_edit.setCursorPosition(len(formatted))
            except ValueError:
                pass

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
        self.price_min_input.setMaxLength(20)
        self.price_min_input.textChanged.connect(lambda: self._format_input(self.price_min_input))
        self.price_min_input.textChanged.connect(self.filter_products)

        price_max_label = QLabel('đến:')
        self.price_max_input = QLineEdit()
        self.price_max_input.setPlaceholderText('VNĐ')
        self.price_max_input.setMaxLength(20)
        self.price_max_input.textChanged.connect(lambda: self._format_input(self.price_max_input))
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
        self.power_reserve_label = QLabel('Thời gian trữ cót  (giờ):')
        self.power_reserve_input = QLineEdit()
        self.power_reserve_input.setPlaceholderText('(tối đa 3 số)')
        self.power_reserve_input.setMaxLength(3)
        self.power_reserve_input.setValidator(QDoubleValidator(0, 999, 1))
        self.power_reserve_input.textChanged.connect(self.filter_products)

        self.battery_life_label = QLabel('Thời lượng pin (năm):')
        self.battery_life_input = QLineEdit()
        self.battery_life_input.setPlaceholderText('(tối đa 2 số))')
        self.battery_life_input.setMaxLength(2)
        self.battery_life_input.setValidator(QIntValidator(0, 99))
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
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            ''')
            add_btn.clicked.connect(self.add_product)
            controls_layout.addWidget(add_btn)

            import_csv_btn = QPushButton('Nhập CSV')
            import_csv_btn.setStyleSheet('''
                QPushButton {
                    background-color: #9B59B6;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #8E44AD;
                }
            ''')
            import_csv_btn.clicked.connect(self.import_csv)
            controls_layout.addWidget(import_csv_btn)

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

        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()

        self.page_label = QLabel("Trang 1 / 1")
        pagination_layout.addWidget(self.page_label)

        self.prev_btn = QPushButton('Trước')
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton('Sau')
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)

        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)

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
        Lấy dữ liệu sản phẩm kèm tên brand qua JOIN với pagination,
        rồi fill vào 8 cột của table: ID, Tên, Thương hiệu, Loại, Giá, Số lượng, Chi tiết sản phẩm, Hành động
        """
        try:
            cursor = self.db.conn.cursor()

            # Get total count for pagination
            cursor.execute('SELECT COUNT(*) FROM products')
            result = cursor.fetchone()
            if result is None:
                self.total_products = 0
            else:
                self.total_products = result[0]
            self.total_pages = (self.total_products + self.page_size - 1) // self.page_size
            if self.total_pages == 0:
                self.total_pages = 1

            # Ensure current_page is within bounds
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            if self.current_page < 1:
                self.current_page = 1

            # Fetch paginated products
            offset = (self.current_page - 1) * self.page_size
            cursor.execute('''
                SELECT p.id, p.name, b.name AS brand, p.product_type, p.price, p.quantity,
                       p.description, p.movement_type, p.power_reserve, p.water_resistant,
                       p.battery_life, p.features, p.connectivity
                FROM products p
                LEFT JOIN brands b ON p.brand_id = b.id
                ORDER BY p.quantity ASC, p.id ASC
                LIMIT ? OFFSET ?
            ''', (self.page_size, offset))
            products = cursor.fetchall()
            # Lưu lại danh sách products cho trang hiện tại để dùng khi hiển thị dialog
            self.products = products

            # Populate brand filter with all brands from database (only if not already done)
            if self.brand_filter.count() == 1:  # Only 'Tất cả' means not populated yet
                cursor.execute('SELECT name FROM brands ORDER BY name')
                all_brands = cursor.fetchall()
                for brand_row in all_brands:
                    brand_name = brand_row[0]
                    if brand_name:
                        self.brand_filter.addItem(brand_name)
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi tải dữ liệu', f'Không thể tải dữ liệu sản phẩm từ cơ sở dữ liệu.\nChi tiết lỗi: {str(e)}')
            self.products = []
            self.total_products = 0
            self.total_pages = 1
            self.current_page = 1

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

        # Update pagination controls
        self.page_label.setText(f"Trang {self.current_page} / {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

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

        # Dictionary for translating features to Vietnamese
        feature_translations = {
            'gps': 'GPS',
            'step_counter': 'Đếm bước',
            'waterproof': 'Chống nước',
            'heart_rate': 'Đo nhịp tim',
            'music_control': 'Điều khiển nhạc'
        }

        # Dictionary for translating movement types to Vietnamese
        movement_translations = {
            'automatic': 'Tự động',
            'manual': 'Thủ công',
            'quartz': 'Quartz',
            'kinetic': 'Kinetic'
        }

        specs = {}
        if (ptype_raw or '').lower() in ('mechanical', 'm', 'coil'):
            movement_vn = movement_translations.get((movement_type or 'automatic').lower(), movement_type or 'Tự động')
            specs['Loại máy'] = f"Đồng hồ cơ ({movement_vn})"
            if power_reserve:
                specs['Thời gian trữ cót'] = f"{power_reserve} giờ"
            if water_resistant:
                specs['Chống nước'] = str(water_resistant)
        else:
            specs['Loại máy'] = 'Điện tử'
            specs['Thời lượng pin'] = f"{battery_life or 0} năm"
            if connectivity:
                specs['Kết nối'] = connectivity
        if features:
            feature_list = [feature_translations.get(f.strip(), f.strip()) for f in features.split(';') if f.strip()]
            if feature_list:
                specs['Tính năng khác'] = '<ul style="margin: 0; padding-left: 20px; color: #f0f0f0;"><li>' + '</li><li>'.join(feature_list) + '</li></ul>'
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
        body_layout = QVBoxLayout(body_widget)
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
        desc_container.setMinimumHeight(200)
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
            label_val.setTextFormat(Qt.TextFormat.RichText)
            label_val.setStyleSheet("color: #f0f0f0;")
            specs_layout.addRow(label_key, label_val)

        if not specs:
            specs_layout.addRow(QLabel("Không có thông số kỹ thuật."), QLabel(""))

        specs_widget.setLayout(specs_layout)
        specs_container.setWidget(specs_widget)
        specs_container.setMinimumHeight(150)
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

        try:
            # Check if product has been sold
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM invoice_details WHERE product_id = ?', (product_id,))
            result = cursor.fetchone()
            if result is None:
                sold_count = 0
            else:
                sold_count = result[0]

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
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi xóa sản phẩm', f'Không thể xóa sản phẩm \"{product_name}\".\nChi tiết lỗi: {str(e)}')

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
        try:
            price_min = float(price_min_text.replace(',', '').replace(' VND', '')) if price_min_text else None
        except ValueError:
            price_min = None
        try:
            price_max = float(price_max_text.replace(',', '').replace(' VND', '')) if price_max_text else None
        except ValueError:
            price_max = None

        # Advanced filters
        power_reserve_min_text = self.power_reserve_input.text().strip()
        try:
            power_reserve_min = float(power_reserve_min_text) if power_reserve_min_text else None
        except ValueError:
            power_reserve_min = None

        battery_life_min_text = self.battery_life_input.text().strip()
        try:
            battery_life_min = float(battery_life_min_text) if battery_life_min_text else None
        except ValueError:
            battery_life_min = None

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
            if selected_type == 'Tất cả':
                # When "Tất cả" is selected, apply filters to all products based on entered values
                if power_reserve_min is not None:
                    if display_type != "Đồng hồ cơ" or power_reserve < power_reserve_min:
                        spec_match = False
                if battery_life_min is not None:
                    if display_type != "Đồng hồ điện tử" or battery_life < battery_life_min:
                        spec_match = False
                if selected_connectivity != 'Tất cả':
                    if display_type != "Đồng hồ điện tử" or selected_connectivity not in connectivity:
                        spec_match = False
            else:
                # When specific type is selected, apply filters only to that type
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

    def import_csv(self):
        """
        Import products from CSV file.
        Expected CSV headers: name, brand, product_type, price, quantity, description,
        movement_type, power_reserve, water_resistant, battery_life, features, connectivity
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file CSV", "", "CSV files (*.csv);;All files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            if not rows:
                QMessageBox.warning(self, 'Lỗi', 'File CSV trống hoặc không có dữ liệu.')
                return

            # Validate headers
            required_headers = ['name', 'brand', 'product_type', 'price', 'quantity']
            if not all(header in reader.fieldnames for header in required_headers):
                QMessageBox.warning(self, 'Lỗi', f'File CSV thiếu các cột bắt buộc: {", ".join(required_headers)}')
                return

            # Validate all rows first before importing
            errors = []
            cursor = self.db.conn.cursor()
            for i, row in enumerate(rows):
                try:
                    # Parse data for validation
                    name = row.get('name', '').strip()
                    brand_name = row.get('brand', '').strip()
                    # Check if brand exists
                    cursor.execute('SELECT id FROM brands WHERE name = ?', (brand_name,))
                    brand_result = cursor.fetchone()
                    if not brand_result:
                        errors.append(f"Dòng {i+2}: Thương hiệu '{brand_name}' không tồn tại trong cơ sở dữ liệu")
                        continue
                    product_type = row.get('product_type', '').strip()
                    price = float(row.get('price', 0)) if row.get('price') else 0
                    # Validate price range: 500k to 1 trillion VND
                    if price < 500000 or price > 1000000000000:
                        errors.append(f"Dòng {i+2}: Giá phải từ 500,000 đến 1,000,000,000,000 VND")
                        continue
                    quantity = int(float(row.get('quantity', 0))) if row.get('quantity') else 0
                    # Validate quantity: must be positive
                    if quantity < 0:
                        errors.append(f"Dòng {i+2}: Số lượng không được âm")
                        continue
                    power_reserve = float(row.get('power_reserve', 0)) if row.get('power_reserve') else None
                    # Validate power reserve: max 999 hours
                    if power_reserve is not None and power_reserve > 999:
                        errors.append(f"Dòng {i+2}: Thời gian trữ cót không được vượt quá 999 giờ")
                        continue
                    battery_life = int(float(row.get('battery_life', 0))) if row.get('battery_life') else None
                    # Validate battery life: max 99 years
                    if battery_life is not None and battery_life > 99:
                        errors.append(f"Dòng {i+2}: Thời lượng pin không được vượt quá 99 năm")
                        continue
                except Exception as e:
                    errors.append(f"Dòng {i+2}: {str(e)}")

            # If any errors found, block import
            if errors:
                error_msg = '\n'.join(errors[:10])  # Show first 10 errors
                if len(errors) > 10:
                    error_msg += f'\n... và {len(errors) - 10} lỗi khác'
                QMessageBox.warning(self, 'Lỗi nhập dữ liệu', f'Không thể nhập dữ liệu do có lỗi:\n{error_msg}')
                return

            # If validation passed, proceed with import
            # Show progress dialog
            progress = QProgressDialog("Đang nhập dữ liệu...", "Hủy", 0, len(rows), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            cursor = self.db.conn.cursor()
            imported_count = 0
            updated_count = 0
            skipped_count = 0

            for i, row in enumerate(rows):
                if progress.wasCanceled():
                    break

                progress.setValue(i)

                try:
                    # Get brand_id
                    brand_name = row.get('brand', '').strip()
                    if brand_name:
                        cursor.execute('SELECT id FROM brands WHERE name = ?', (brand_name,))
                        brand_result = cursor.fetchone()
                        if brand_result:
                            brand_id = brand_result[0]
                        else:
                            cursor.execute('INSERT INTO brands (name) VALUES (?)', (brand_name,))
                            brand_id = cursor.lastrowid
                    else:
                        brand_id = None

                    # Parse data
                    name = row.get('name', '').strip()
                    product_type = row.get('product_type', '').strip()
                    price = float(row.get('price', 0)) if row.get('price') else 0
                    new_quantity = int(float(row.get('quantity', 0))) if row.get('quantity') else 0
                    description = row.get('description', '').strip()
                    movement_type = row.get('movement_type', '').strip()
                    power_reserve = float(row.get('power_reserve', 0)) if row.get('power_reserve') else None
                    water_resistant = row.get('water_resistant', '').strip() or None
                    battery_life = int(float(row.get('battery_life', 0))) if row.get('battery_life') else None
                    features = row.get('features', '').strip()
                    connectivity = row.get('connectivity', '').strip()

                    # Check if product already exists
                    cursor.execute('SELECT id, quantity FROM products WHERE name = ? AND brand_id = ?', (name, brand_id))
                    existing_product = cursor.fetchone()

                    if existing_product:
                        product_id, current_quantity = existing_product
                        total_quantity = current_quantity + new_quantity

                        if total_quantity <= 100:
                            # Update existing product quantity
                            cursor.execute('UPDATE products SET quantity = ? WHERE id = ?', (total_quantity, product_id))
                            updated_count += 1
                        else:
                            # Skip if would exceed max quantity
                            skipped_count += 1
                            continue
                    else:
                        # Insert new product
                        cursor.execute('''
                            INSERT INTO products (name, brand_id, product_type, price, quantity,
                                               description, movement_type, power_reserve, water_resistant,
                                               battery_life, features, connectivity)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (name, brand_id, product_type, price, new_quantity, description,
                              movement_type, power_reserve, water_resistant, battery_life, features, connectivity))
                        imported_count += 1

                except Exception as e:
                    # This shouldn't happen since we validated, but just in case
                    QMessageBox.warning(self, 'Lỗi', f'Lỗi không mong muốn ở dòng {i+2}: {str(e)}')
                    return

            self.db.conn.commit()
            progress.setValue(len(rows))

            # Show success
            self.load_data()
            success_msg = f'Đã nhập thành công {imported_count} sản phẩm mới.'
            if updated_count > 0:
                success_msg += f'\nĐã cập nhật số lượng cho {updated_count} sản phẩm hiện có.'
            if skipped_count > 0:
                success_msg += f'\nĐã bỏ qua {skipped_count} sản phẩm (vượt quá số lượng tối đa).'
            QMessageBox.information(self, 'Thành công', success_msg)

        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể đọc file CSV: {str(e)}')

    def handle_click(self, index):
        if not index.isValid():
            self.table.clearSelection()
            return

        selected = self.table.selectedItems()
        if selected and selected[0].row() == index.row():
            self.table.clearSelection()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

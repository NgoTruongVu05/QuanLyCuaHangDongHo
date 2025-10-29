from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QLineEdit, QTableWidgetItem, QSpinBox,
    QGroupBox, QMessageBox, QCheckBox, QHeaderView, QMessageBox
)
from PyQt6.QtCore import QDate, Qt


class CreateInvoiceTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.cart = []
        self.selected_customer = None
        self.current_page = 1
        self.items_per_page = 10
        self.all_products = []
        self.filtered_products = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # ===== LEFT SIDE =====
        left_layout = QVBoxLayout()

        # --- Product selection ---
        product_group = QGroupBox('Chọn sản phẩm')
        product_layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Tìm kiếm sản phẩm...")
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        product_layout.addLayout(search_layout)

        # Product table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(['Chọn', 'Tên', 'Giá', 'Tồn kho', 'Số lượng', 'ID'])
        self.product_table.setColumnHidden(5, True)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.verticalHeader().setDefaultSectionSize(36)

        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.product_table.setColumnWidth(0, 50)

        product_layout.addWidget(self.product_table)

        # Pagination
        pagination_layout = QHBoxLayout()
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_btn = QPushButton("◀ Trước")
        self.next_btn = QPushButton("Sau ▶")
        self.page_label = QLabel("Trang 1/1")
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        product_layout.addLayout(pagination_layout)

        add_to_cart_btn = QPushButton('Thêm vào giỏ')
        add_to_cart_btn.clicked.connect(self.add_selected_products_to_cart)
        product_layout.addWidget(add_to_cart_btn)

        product_group.setLayout(product_layout)
        left_layout.addWidget(product_group)

        # --- Customer info ---
        customer_group = QGroupBox('Thông tin khách hàng')
        customer_layout = QVBoxLayout()

        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Tìm khách hàng theo SĐT...")
        self.customer_search.textChanged.connect(self.search_customers)
        customer_layout.addWidget(self.customer_search)

        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(['Chọn', 'Tên', 'Số điện thoại', 'Địa chỉ'])
        self.customer_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customer_table.setAlternatingRowColors(True)

        header = self.customer_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        header.setMinimumSectionSize(50)
        self.customer_table.setColumnWidth(0, 50)

        self.customer_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.customer_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.customer_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        customer_layout.addWidget(self.customer_table)
        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)

        # ===== RIGHT SIDE =====
        right_layout = QVBoxLayout()

        self.customer_label = QLabel("Khách hàng: (chưa chọn)")
        self.customer_label.setStyleSheet("font-weight: bold; color: white; margin-bottom: 4px;")
        right_layout.addWidget(self.customer_label)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['Sản phẩm', 'Đơn giá', 'Số lượng', 'Thành tiền', 'Hành động'])
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cart_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.cart_table)

        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel('Tổng cộng:'))
        self.total_label = QLabel('0 VND')
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()

        create_invoice_btn = QPushButton('Tạo hóa đơn')
        create_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #388E3C;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
        """)
        create_invoice_btn.clicked.connect(self.create_invoice)
        total_layout.addWidget(create_invoice_btn)
        right_layout.addLayout(total_layout)

        # Gắn hai cột vào layout chính
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)
        self.setLayout(layout)

        self.product_table.resizeColumnsToContents()
        self.customer_table.resizeColumnsToContents()
        self.cart_table.resizeColumnsToContents()
        self.cart_table.horizontalHeader().setStretchLastSection(True)

    # ==============================
    def search_products(self):
        search_text = self.product_search.text().strip().lower()

        if search_text:
            # Lọc từ danh sách self.all_products đã có sẵn
            self.filtered_products = [
                p for p in self.all_products
                if search_text in p[1].lower()  # p[1] là tên sản phẩm
            ]
        else:
            # Nếu không nhập gì thì hiển thị lại toàn bộ
            self.filtered_products = self.all_products[:]

        # Sau khi lọc, luôn quay về trang đầu tiên
        self.current_page = 1
        self.display_page(self.current_page)

    def search_customers(self):
        search_text = self.customer_search.text()
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT name, phone, address
            FROM customers
            WHERE phone LIKE ?
        ''', (f'%{search_text}%',))
        customers = cursor.fetchall()

        self.customer_table.setRowCount(len(customers))
        for row, (name, phone, address) in enumerate(customers):
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda _, r=row: self.select_single_customer(r))
            self.customer_table.setCellWidget(row, 0, checkbox)

            self.customer_table.setItem(row, 1, QTableWidgetItem(name))
            self.customer_table.setItem(row, 2, QTableWidgetItem(phone))
            self.customer_table.setItem(row, 3, QTableWidgetItem(address))

    def select_single_customer(self, selected_row):
        """Đảm bảo chỉ chọn 1 khách hàng duy nhất"""
        for row in range(self.customer_table.rowCount()):
            checkbox = self.customer_table.cellWidget(row, 0)
            if row != selected_row:
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)

        checkbox = self.customer_table.cellWidget(selected_row, 0)
        if checkbox.isChecked():
            self.selected_customer = {
                'name': self.customer_table.item(selected_row, 1).text(),
                'phone': self.customer_table.item(selected_row, 2).text()
            }
            self.customer_label.setText(f"Khách hàng: {self.selected_customer['name']}")
        else:
            self.selected_customer = None
            self.customer_label.setText("Khách hàng: (chưa chọn)")

    def add_selected_products_to_cart(self):
        selected_products = []
        total_qty_in_cart = sum(item['quantity'] for item in self.cart)
        selected_any = False

        for row in range(self.product_table.rowCount()):
            checkbox = self.product_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_any = True
                pid = int(self.product_table.item(row, 5).text())
                name = self.product_table.item(row, 1).text()
                price = float(self.product_table.item(row, 2).text().replace(' VND', '').replace(',', ''))
                available_qty = int(self.product_table.item(row, 3).text())
                spin = self.product_table.cellWidget(row, 4)
                qty = spin.value()

                selected_products.append({
                    'id': pid,
                    'name': name,
                    'price': price,
                    'available_qty': available_qty,
                    'quantity': qty
                })

        if not selected_any:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất một sản phẩm!")
            return

        # Tính tổng số lượng sau khi thêm
        total_selected_qty = sum(p['quantity'] for p in selected_products)
        if total_qty_in_cart + total_selected_qty > 5:
            remaining = max(0, 5 - total_qty_in_cart)
            QMessageBox.warning(
                self,
                "Giới hạn giỏ hàng",
                f"Tổng số lượng sản phẩm trong giỏ hàng không được vượt quá 5.\n"
                f"Hiện tại bạn còn có thể thêm tối đa {remaining} sản phẩm."
            )
            return

        # Nếu hợp lệ thì thêm từng sản phẩm
        for p in selected_products:
            existing = next((item for item in self.cart if item['id'] == p['id']), None)
            if existing:
                if existing['quantity'] + p['quantity'] > p['available_qty']:
                    QMessageBox.warning(self, "Lỗi", f"Sản phẩm '{p['name']}' chỉ còn {p['available_qty']} trong kho.")
                    continue
                existing['quantity'] += p['quantity']
            else:
                self.cart.append({'id': p['id'], 'name': p['name'], 'price': p['price'], 'quantity': p['quantity']})

        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0

        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{int(item['price']):,} VND"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            total_item = int(item['price'] * item['quantity'])
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{total_item:,} VND"))
            total += total_item

            remove_btn = QPushButton("Xóa")
            remove_btn.setStyleSheet("""
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
            """)
            remove_btn.clicked.connect(lambda _, r=row: self.remove_item_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)

        self.total_label.setText(f"{int(total):,} VND")
        self.cart_table.resizeColumnsToContents()
        self.cart_table.horizontalHeader().setStretchLastSection(True)

    def create_invoice(self):
        if not self.cart:
            QMessageBox.warning(self, 'Lỗi', 'Giỏ hàng trống!')
            return

        if not self.selected_customer:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn khách hàng!')
            return
        
        cursor = self.db.conn.cursor()

        # Lấy ID khách hàng nếu có
        customer_id = None
        if self.selected_customer:
            cursor.execute('SELECT id FROM customers WHERE phone = ?', (self.selected_customer['phone'],))
            res = cursor.fetchone()
            if not res:
                QMessageBox.warning(self, 'Lỗi', 'Không tìm thấy thông tin khách hàng!')
                return

        customer_id = res[0]
        employee_id = self.user_id
        total = sum(item['price'] * item['quantity'] for item in self.cart)

        invoice_id = self.db.generate_invoice_id()

        cursor.execute('''
            INSERT INTO invoices (id, customer_id, employee_id, total_amount, created_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (invoice_id, customer_id, employee_id, total, QDate.currentDate().toString('yyyy-MM-dd')))

        for item in self.cart:
            cursor.execute('''
                INSERT INTO invoice_details (invoice_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (invoice_id, item['id'], item['quantity'], item['price']))

            cursor.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', (item['quantity'], item['id']))

        self.db.conn.commit()

        QMessageBox.information(self, 'Thành công', f'Hóa đơn #{invoice_id} đã được tạo thành công!')
        self.load_data()

    def load_data(self):
        self.reset_form()

        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, name, price, quantity
            FROM products
            WHERE quantity > 0
        ''')
        self.all_products = cursor.fetchall()
        self.filtered_products = self.all_products[:]
        self.current_page = 1
        self.display_page(self.current_page)

        # Load lại khách hàng
        cursor.execute('SELECT name, phone, address FROM customers')
        customers = cursor.fetchall()
        self.customer_table.setRowCount(len(customers))
        for row, (name, phone, address) in enumerate(customers):
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda _, r=row: self.select_single_customer(r))
            self.customer_table.setCellWidget(row, 0, checkbox)
            self.customer_table.setItem(row, 1, QTableWidgetItem(name))
            self.customer_table.setItem(row, 2, QTableWidgetItem(phone))
            self.customer_table.setItem(row, 3, QTableWidgetItem(address))

    def reset_form(self):
        self.cart.clear()
        self.selected_customer = None
        self.product_search.clear()
        self.customer_search.clear()
        self.update_cart_display()
        self.customer_label.setText("Khách hàng: (chưa chọn)")

    def remove_item_from_cart(self, row):
        if 0 <= row < len(self.cart):
            item_name = self.cart[row]['name']
            reply = QMessageBox.question(
                self, "Xác nhận",
                f"Bạn có chắc muốn xóa sản phẩm '{item_name}' khỏi giỏ hàng?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.cart[row]
                self.update_cart_display()

    def display_page(self, page):
        self.product_table.setRowCount(0)

        data_source = self.filtered_products
        start = (page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_items = data_source[start:end]

        self.product_table.setRowCount(len(page_items))
        self.product_table.verticalHeader().setDefaultSectionSize(30)

        for row, (pid, name, price, qty) in enumerate(page_items):
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin-left:10px;")
            self.product_table.setCellWidget(row, 0, checkbox)

            self.product_table.setItem(row, 1, QTableWidgetItem(name))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{int(price):,} VND"))
            self.product_table.setItem(row, 3, QTableWidgetItem(str(qty)))

            spin = QSpinBox()
            spin.setRange(1, qty)
            spin.setValue(1)
            spin.setFixedHeight(24)
            spin.setStyleSheet("QSpinBox { padding: 0 2px; font-size: 13px; }")
            self.product_table.setCellWidget(row, 4, spin)

            self.product_table.setItem(row, 5, QTableWidgetItem(str(pid)))

        total_pages = max(1, (len(data_source) + self.items_per_page - 1) // self.items_per_page)
        self.page_label.setText(f"Trang {self.current_page}/{total_pages}")

        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

    def next_page(self):
        total_pages = (len(self.all_products) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_page(self.current_page)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page(self.current_page)

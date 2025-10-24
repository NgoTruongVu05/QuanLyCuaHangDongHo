from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QLineEdit, QTableWidgetItem, QSpinBox,
    QGroupBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import QDate, Qt


class CreateInvoiceTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.cart = []
        self.selected_customer = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # ===== LEFT SIDE =====
        left_layout = QVBoxLayout()

        # --- Product selection ---
        product_group = QGroupBox('Chọn sản phẩm')
        product_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Tìm kiếm sản phẩm...")
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        product_layout.addLayout(search_layout)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(['Chọn', 'Tên', 'Giá', 'Tồn kho', 'ID'])
        self.product_table.setColumnHidden(4, True)  # Ẩn ID
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        product_layout.addWidget(self.product_table)

        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel('Số lượng mỗi sản phẩm:'))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        qty_layout.addWidget(self.quantity_spin)

        add_to_cart_btn = QPushButton('Thêm')
        add_to_cart_btn.clicked.connect(self.add_selected_products_to_cart)
        qty_layout.addWidget(add_to_cart_btn)
        product_layout.addLayout(qty_layout)

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
        customer_layout.addWidget(self.customer_table)

        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)

        # ===== RIGHT SIDE =====
        right_layout = QVBoxLayout()
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['Sản phẩm', 'Đơn giá', 'Số lượng', 'Thành tiền', 'Hành động'])
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.cart_table)

        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel('Tổng cộng:'))
        self.total_label = QLabel('0 VND')
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()

        create_invoice_btn = QPushButton('Tạo hóa đơn')
        create_invoice_btn.clicked.connect(self.create_invoice)
        total_layout.addWidget(create_invoice_btn)

        right_layout.addLayout(total_layout)

        # Gắn hai cột vào layout chính
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)
        self.setLayout(layout)

    # ==============================
    def search_products(self):
        search_text = self.product_search.text().lower()
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, name, price, quantity
            FROM products
            WHERE LOWER(name) LIKE ? AND quantity > 0
        ''', (f'%{search_text}%',))
        products = cursor.fetchall()

        self.product_table.setRowCount(len(products))
        for row, (pid, name, price, qty) in enumerate(products):
            # Checkbox chọn sản phẩm
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin-left:20px;")
            self.product_table.setCellWidget(row, 0, checkbox)

            self.product_table.setItem(row, 1, QTableWidgetItem(name))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{price:,} VND"))
            self.product_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            self.product_table.setItem(row, 4, QTableWidgetItem(str(pid)))

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
        else:
            self.selected_customer = None

    def add_selected_products_to_cart(self):
        selected_any = False
        for row in range(self.product_table.rowCount()):
            checkbox = self.product_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_any = True
                pid = int(self.product_table.item(row, 4).text())
                name = self.product_table.item(row, 1).text()
                price = float(self.product_table.item(row, 2).text().replace(' VND', '').replace(',', ''))
                available_qty = int(self.product_table.item(row, 3).text())
                qty = self.quantity_spin.value()

                existing = next((item for item in self.cart if item['id'] == pid), None)

                # Nếu sản phẩm đã có trong giỏ, tính tổng dự kiến
                current_in_cart = existing['quantity'] if existing else 0
                new_total_qty = current_in_cart + qty

                if new_total_qty > available_qty:
                    QMessageBox.warning(
                        self,
                        'Lỗi',
                        f'Sản phẩm "{name}" chỉ còn {available_qty} trong kho.\n'
                        f'Hiện đã có {current_in_cart} trong giỏ, bạn chỉ có thể thêm tối đa {available_qty - current_in_cart}.'
                    )
                    continue

                # Cập nhật giỏ hàng hợp lệ
                if existing:
                    existing['quantity'] = new_total_qty
                else:
                    self.cart.append({'id': pid, 'name': name, 'price': price, 'quantity': qty})

        if not selected_any:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn ít nhất 1 sản phẩm!')
            return

        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0

        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:,} VND"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            total_item = item['price'] * item['quantity']
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

        self.total_label.setText(f"{total:,} VND")
        self.cart_table.resizeColumnsToContents()
        self.cart_table.horizontalHeader().setStretchLastSection(True)

    def create_invoice(self):
        if not self.cart:
            QMessageBox.warning(self, 'Lỗi', 'Giỏ hàng trống!')
            return

        cursor = self.db.conn.cursor()

        # Lấy ID khách hàng nếu có
        customer_id = None
        if self.selected_customer:
            cursor.execute('SELECT id FROM customers WHERE phone = ?', (self.selected_customer['phone'],))
            res = cursor.fetchone()
            if res:
                customer_id = res[0]

        employee_id = self.user_id if self.user_id else 1
        total = sum(item['price'] * item['quantity'] for item in self.cart)

        cursor.execute('''
            INSERT INTO invoices (customer_id, employee_id, total_amount, created_date)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, employee_id, total, QDate.currentDate().toString('yyyy-MM-dd')))

        invoice_id = cursor.lastrowid

        for item in self.cart:
            cursor.execute('''
                INSERT INTO invoice_details (invoice_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (invoice_id, item['id'], item['quantity'], item['price']))

            cursor.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', (item['quantity'], item['id']))

        self.db.conn.commit()

        QMessageBox.information(self, 'Thành công', f'Hóa đơn #{invoice_id} đã được tạo thành công!')
        self.reset_form()

    def load_data(self):
        """Refresh both product and customer data"""
        # Clear search boxes to show all data
        self.product_search.clear()
        self.customer_search.clear()
        
        # Reload products
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, name, price, quantity
            FROM products
            WHERE quantity > 0
        ''')
        products = cursor.fetchall()

        self.product_table.setRowCount(len(products))
        for row, (pid, name, price, qty) in enumerate(products):
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin-left:20px;")
            self.product_table.setCellWidget(row, 0, checkbox)

            self.product_table.setItem(row, 1, QTableWidgetItem(name))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{price:,} VND"))
            self.product_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            self.product_table.setItem(row, 4, QTableWidgetItem(str(pid)))

        # Reload customers
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
        self.load_data()

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

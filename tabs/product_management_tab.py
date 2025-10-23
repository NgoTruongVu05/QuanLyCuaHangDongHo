from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

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

        # Table settings
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make table read-only
        self.table.setColumnCount(9)
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

        # Selection behavior (optional)
        # self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        # self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Allow deselection by clicking empty area
        self.table.clicked.connect(self.handle_click)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        """
        Lấy dữ liệu sản phẩm kèm tên brand qua JOIN,
        rồi fill vào đúng 9 cột của table.
        Nếu quantity <= 5 sẽ đánh dấu ô và hiện cảnh báo sau khi load.
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

        self.table.setRowCount(len(products))
        low_stock = []  # list of tuples (id, name, quantity)

        for row, product in enumerate(products):
            # product tuple indices based on SELECT above
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

            # Col 3: Loại (hiển thị thân thiện)
            if ptype in ('mechanical', 'm', 'coil'):
                type_text = "Đồng hồ cơ"
            elif ptype in ('digital', 'smart', 'electronic'):
                type_text = "Đồng hồ điện tử"
            else:
                type_text = product[3] or ''
            type_item = QTableWidgetItem(type_text)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, type_item)

            # Col 4: Giá — format có xử lý None
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

            # Col 5: Số lượng
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Highlight low stock: <=5 => mark màu vàng cam, <=2 => đỏ
            try:
                qnum = int(quantity)
            except Exception:
                qnum = 0

            if qnum <= 2:
                qty_item.setBackground(QColor("#E74C3C"))   # red
                qty_item.setForeground(QColor("white"))
                low_stock.append((pid, name, qnum))
            elif qnum <= 5:
                qty_item.setBackground(QColor("#F39C12"))   # orange
                qty_item.setForeground(QColor("black"))
                low_stock.append((pid, name, qnum))

            self.table.setItem(row, 5, qty_item)

            # Col 6: Mô tả
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 6, desc_item)

            # Col 7: Thông số (tổng hợp)
            if ptype == "mechanical":
                pr = f"{movement_type or 'Automatic'}"
                if power_reserve:
                    pr += f", {power_reserve}h"
                if water_resistant:
                    pr += ", Chống nước"
                if features:
                    pr += f", {features}"
                specs = pr
            else:
                # digital / smart
                specs = f"{battery_life or 0} tháng"
                if connectivity:
                    specs += f", {connectivity}"
                if features:
                    specs += f", {features}"
            specs_item = QTableWidgetItem(specs)
            specs_item.setFlags(specs_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 7, specs_item)

            # Col 8: Action buttons (Sửa / Xóa / Xem)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)

            if self.user_role == 1:  # admin
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
                        margin-right: 2px
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_product_row(r))
                action_layout.addWidget(delete_btn)
            else:
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
            self.table.resizeRowsToContents()

        # Nếu có sản phẩm low stock, hiện cảnh báo tổng hợp
        if low_stock:
            # build thông báo ngắn gọn
            lines = [f"- {name} (ID: {pid}) — {qty} cái" for pid, name, qty in low_stock]
            msg = "Có sản phẩm sắp hết hàng (<= 5):\n\n" + "\n".join(lines)
            QMessageBox.warning(self, "Cảnh báo tồn kho", msg)

    def add_product(self):
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm sản phẩm mới!')

    def edit_product_row(self, row):
        # bảo đảm ô ID tồn tại trước khi parse
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        product_id = int(id_item.text())
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db, product_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật sản phẩm!')

    def delete_product_row(self, row):
        id_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        if not id_item:
            return
        product_id = int(id_item.text())
        product_name = name_item.text() if name_item else ''

        reply = QMessageBox.question(self, 'Xác nhận',
                                     f'Bạn có chắc muốn xóa sản phẩm \"{product_name}\"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            self.db.conn.commit()
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã xóa sản phẩm!')

    def view_product_row(self, row):
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        product_id = int(id_item.text())
        product_name = self.table.item(row, 1).text() if self.table.item(row, 1) else ''
        brand = self.table.item(row, 2).text() if self.table.item(row, 2) else ''
        product_type = self.table.item(row, 3).text() if self.table.item(row, 3) else ''
        price = self.table.item(row, 4).text() if self.table.item(row, 4) else ''
        quantity = self.table.item(row, 5).text() if self.table.item(row, 5) else ''
        description = self.table.item(row, 6).text() if self.table.item(row, 6) else ''
        specs = self.table.item(row, 7).text() if self.table.item(row, 7) else ''

        info_text = f"""
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

    def handle_click(self, index):
        """Handle click events to allow deselection"""
        if not index.isValid():
            self.table.clearSelection()
            return

        selected = self.table.selectedItems()
        if selected:
            # nếu click cùng hàng đã chọn -> bỏ chọn
            if selected[0].row() == index.row():
                self.table.clearSelection()

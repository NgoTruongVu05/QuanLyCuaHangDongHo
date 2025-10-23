from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

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

        # Allow deselection by clicking empty area
        self.table.clicked.connect(self.handle_click)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def _create_qty_widget(self, quantity: int):
        """
        Tạo widget cho ô Số lượng gồm:
        [ QLabel(quantity) , stretch , QLabel(badge) ]
        badge chỉ hiện nếu quantity <= 5.
        """
        qty_widget = QWidget()
        layout = QHBoxLayout(qty_widget)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        # Label hiển thị số lượng với styling đẹp hơn
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

        # Badge với thiết kế hiện đại
        badge_label = QLabel()
        badge_label.setFixedHeight(20)
        badge_label.setFixedWidth(42)
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Hiệu ứng shadow cho badge
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 60))
        badge_label.setGraphicsEffect(shadow)

        if quantity <= 2:
            # Màu đỏ - mức độ nguy hiểm cao
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
            # Màu cam - mức độ cảnh báo
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
            # Không hiện badge nhưng có thể hiện indicator nhỏ nếu muốn
            badge_label.hide()

        layout.addWidget(badge_label)
        
        # Tooltip hữu ích
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
        rồi fill vào đúng 9 cột của table.
        Badge hiển thị ở cuối ô Số lượng nếu <=5.
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
        low_stock = []

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

            # Col 6: Mô tả
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 6, desc_item)

            # Col 7: Thông số
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
                specs = f"{battery_life or 0} tháng"
                if connectivity:
                    specs += f", {connectivity}"
                if features:
                    specs += f", {features}"
            specs_item = QTableWidgetItem(specs)
            specs_item.setFlags(specs_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 7, specs_item)

            # Col 8: Action buttons
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
            self.table.setCellWidget(row, 8, action_widget)
            self.table.resizeRowsToContents()            
            for row in range(self.table.rowCount()):
                self.table.setRowHeight(row, 40)

    # --- Các hàm khác giữ nguyên ---
    def add_product(self):
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm sản phẩm mới!')

    def edit_product_row(self, row):
        id_item = self.table.item(row, 0)
        if not id_item:
            # nếu ID không ở dạng item (vì ta dùng cellWidget cho qty), vẫn lấy qua cell(0,row)
            # nhưng ở đây ID là QTableWidgetItem, nên chỉ cần check
            return
        product_id = int(id_item.text())
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db, product_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật sản phẩm!')

    def delete_product_row(self, row):
        # Lấy ID từ item
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
        # quantity là cellWidget -> lấy text từ widget
        qty_widget = self.table.cellWidget(row, 5)
        if qty_widget:
            qty_label = qty_widget.findChild(QLabel)
            quantity = qty_label.text() if qty_label else ''
        else:
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
        if not index.isValid():
            self.table.clearSelection()
            return

        selected = self.table.selectedItems()
        if selected and selected[0].row() == index.row():
            self.table.clearSelection()

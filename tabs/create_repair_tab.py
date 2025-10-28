from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QComboBox, QDoubleSpinBox, 
                             QGroupBox, QFormLayout, QMessageBox, QTextEdit,
                             QDateEdit)
from PyQt6.QtCore import QDate

class CreateRepairTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Customer info
        customer_group = QGroupBox('Thông tin khách hàng')
        customer_layout = QFormLayout()
        
        self.customer_combo = QComboBox()
        self.load_customers()
        customer_layout.addRow('Khách hàng:', self.customer_combo)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Repair details
        repair_group = QGroupBox('Thông tin sửa chữa')
        repair_layout = QFormLayout()
        
        self.watch_desc_input = QTextEdit()
        self.watch_desc_input.setMaximumHeight(80)
        # Cho phép chọn một đồng hồ có sẵn từ database (nếu muốn)
        self.product_combo = QComboBox()
        self.product_combo.addItem('--- Chọn đồng hồ ---', -1)
        self.load_products()
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        repair_layout.addRow('Chọn đồng hồ:', self.product_combo)

        repair_layout.addRow('Mô tả đồng hồ:', self.watch_desc_input)
        
        self.issue_desc_input = QTextEdit()
        self.issue_desc_input.setMaximumHeight(80)
        repair_layout.addRow('Mô tả lỗi:', self.issue_desc_input)
        
        
        # Không hiển thị input chi phí khi tạo đơn
        
        date_layout = QHBoxLayout()
        self.estimated_completion_input = QDateEdit()
        self.estimated_completion_input.setDate(QDate.currentDate().addDays(7))
        self.estimated_completion_input.setCalendarPopup(True)
        date_layout.addWidget(QLabel('Dự kiến hoàn thành:'))
        date_layout.addWidget(self.estimated_completion_input)
        
        repair_layout.addRow(date_layout)
        
        repair_group.setLayout(repair_layout)
        layout.addWidget(repair_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton('Tạo đơn sửa chữa')
        create_btn.clicked.connect(self.create_repair_order)
        button_layout.addWidget(create_btn)
        
        clear_btn = QPushButton('Làm mới')
        # Làm mới form và tải lại danh sách sản phẩm/khách hàng mới (nếu có)
        clear_btn.clicked.connect(self.refresh_form)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def load_customers(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, name FROM customers')
        customers = cursor.fetchall()
        
        self.customer_combo.clear()
        self.customer_combo.addItem('Khách lẻ', -1)
        for customer in customers:
            self.customer_combo.addItem(customer[1], customer[0])

    def load_products(self):
        """Tải danh sách sản phẩm (đồng hồ) từ database vào combobox."""
        try:
            cursor = self.db.conn.cursor()
            # Sắp xếp theo tên để sản phẩm mới dễ tìm
            cursor.execute('SELECT id, name FROM products ORDER BY name')
            products = cursor.fetchall()

            # Giữ item mặc định ở vị trí 0
            self.product_combo.clear()
            self.product_combo.addItem('--- Chọn đồng hồ ---', -1)
            for p in products:
                self.product_combo.addItem(p[1], p[0])
        except Exception:
            # Nếu lỗi DB, giữ combobox rỗng (ngoại trừ placeholder)
            self.product_combo.clear()
            self.product_combo.addItem('--- Chọn đồng hồ ---', -1)

    def showEvent(self, event):
        """Khi tab/Widget hiện lên, reload products để cập nhật các thay đổi gần đây."""
        try:
            self.load_products()
        except Exception:
            pass
        return super().showEvent(event)

    def on_product_selected(self, index):
        """Khi chọn sản phẩm: tự động điền mô tả đồng hồ (không ép buộc)."""
        pid = self.product_combo.currentData()
        if pid and pid != -1:
            name = self.product_combo.currentText()
            # Nếu người dùng chưa nhập mô tả, tự động điền
            if not self.watch_desc_input.toPlainText().strip():
                self.watch_desc_input.setPlainText(name)
    
    def create_repair_order(self):
        customer_id = self.customer_combo.currentData()
        watch_desc = self.watch_desc_input.toPlainText()
        issue_desc = self.issue_desc_input.toPlainText()
        estimated_completion = self.estimated_completion_input.date().toString('yyyy-MM-dd')
        # Mặc định trạng thái là "Chờ xử lý"
        status = 'Chờ xử lý'
        
        if not watch_desc or not issue_desc:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin!')
            return
        
        # Nếu chưa đăng nhập, sử dụng employee_id mặc định
        employee_id = self.user_id if self.user_id else 1
        
        if customer_id == -1:
            customer_id = None
        
        cursor = self.db.conn.cursor()
        
        cursor.execute('''
            INSERT INTO repair_orders 
            (customer_id, employee_id, watch_description, issue_description, 
             actual_cost, created_date, estimated_completion, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, employee_id, watch_desc, issue_desc, 
             0, QDate.currentDate().toString('yyyy-MM-dd'), estimated_completion, status))
        
        repair_id = cursor.lastrowid
        self.db.conn.commit()
        
        QMessageBox.information(self, 'Thành công', f'Đơn sửa chữa #{repair_id} đã được tạo!')
        self.clear_form()
    
    def get_status_value(self, status_text):
        status_map = {
            'Chờ xử lý': 'pending',
            'Đang sửa': 'in_progress', 
            'Hoàn thành': 'completed',
            'Đã hủy': 'cancelled'
        }
        return status_map.get(status_text, 'pending')
    
    def clear_form(self):
        self.watch_desc_input.clear()
        self.issue_desc_input.clear()
        self.estimated_completion_input.setDate(QDate.currentDate().addDays(7))

    def refresh_form(self):
        """Làm mới form và reload dữ liệu tham chiếu (sản phẩm, khách hàng)."""
        # Giữ hành vi clear hiện tại
        self.clear_form()
        # Reload danh sách sản phẩm và khách hàng trong combobox
        try:
            self.load_products()
        except Exception:
            pass
        try:
            self.load_customers()
        except Exception:
            pass
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
        repair_layout.addRow('Mô tả đồng hồ:', self.watch_desc_input)
        
        self.issue_desc_input = QTextEdit()
        self.issue_desc_input.setMaximumHeight(80)
        repair_layout.addRow('Mô tả lỗi:', self.issue_desc_input)
        
        cost_layout = QHBoxLayout()
        self.estimated_cost_input = QDoubleSpinBox()
        self.estimated_cost_input.setMaximum(999999999)
        self.estimated_cost_input.setPrefix('VND ')
        cost_layout.addWidget(QLabel('Chi phí dự kiến:'))
        cost_layout.addWidget(self.estimated_cost_input)
        
        self.actual_cost_input = QDoubleSpinBox()
        self.actual_cost_input.setMaximum(999999999)
        self.actual_cost_input.setPrefix('VND ')
        cost_layout.addWidget(QLabel('Chi phí thực tế:'))
        cost_layout.addWidget(self.actual_cost_input)
        
        repair_layout.addRow(cost_layout)
        
        date_layout = QHBoxLayout()
        self.estimated_completion_input = QDateEdit()
        self.estimated_completion_input.setDate(QDate.currentDate().addDays(7))
        self.estimated_completion_input.setCalendarPopup(True)
        date_layout.addWidget(QLabel('Dự kiến hoàn thành:'))
        date_layout.addWidget(self.estimated_completion_input)
        
        repair_layout.addRow(date_layout)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Chờ xử lý', 'Đang sửa', 'Hoàn thành', 'Đã hủy'])
        repair_layout.addRow('Trạng thái:', self.status_combo)
        
        repair_group.setLayout(repair_layout)
        layout.addWidget(repair_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton('Tạo đơn sửa chữa')
        create_btn.clicked.connect(self.create_repair_order)
        button_layout.addWidget(create_btn)
        
        clear_btn = QPushButton('Làm mới')
        clear_btn.clicked.connect(self.clear_form)
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
    
    def create_repair_order(self):
        customer_id = self.customer_combo.currentData()
        watch_desc = self.watch_desc_input.toPlainText()
        issue_desc = self.issue_desc_input.toPlainText()
        estimated_cost = self.estimated_cost_input.value()
        actual_cost = self.actual_cost_input.value()
        estimated_completion = self.estimated_completion_input.date().toString('yyyy-MM-dd')
        status = self.get_status_value(self.status_combo.currentText())
        
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
            (customer_id, employee_id, watch_description, issue_description, estimated_cost, 
             actual_cost, created_date, estimated_completion, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, employee_id, watch_desc, issue_desc, estimated_cost,
             actual_cost, QDate.currentDate().toString('yyyy-MM-dd'), estimated_completion, status))
        
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
        self.estimated_cost_input.setValue(0)
        self.actual_cost_input.setValue(0)
        self.estimated_completion_input.setDate(QDate.currentDate().addDays(7))
        self.status_combo.setCurrentIndex(0)
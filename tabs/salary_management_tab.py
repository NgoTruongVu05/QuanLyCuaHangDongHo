from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QSpinBox, QLabel, QGroupBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QFont

class SalaryManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        # Tự động load data khi khởi tạo
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Filter section
        filter_group = QGroupBox('Lọc dữ liệu')
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel('Tháng:'))
        self.month_filter = QSpinBox()
        self.month_filter.setRange(1, 12)
        self.month_filter.setValue(QDate.currentDate().month())
        self.month_filter.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.month_filter)
        
        filter_layout.addWidget(QLabel('Năm:'))
        self.year_filter = QSpinBox()
        self.year_filter.setRange(2020, 2030)
        self.year_filter.setValue(QDate.currentDate().year())
        self.year_filter.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.year_filter)
        
        filter_layout.addStretch()
        
        # Nút tính lương
        calculate_btn = QPushButton('Tính lương tháng này')
        calculate_btn.clicked.connect(self.calculate_all_salaries)
        calculate_btn.setStyleSheet('''
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        ''')
        filter_layout.addWidget(calculate_btn)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
       
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID NV', 'Họ tên', 'Vai trò', 'Lương cơ bản', 'Doanh số', 'Hoa hồng 0.5%', 'Tổng lương'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID NV
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên NV
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Vai trò
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Lương cơ bản
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Doanh số
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Hoa hồng
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Tổng lương
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def showEvent(self, event):
        """Tự động làm mới dữ liệu khi tab được hiển thị"""
        self.load_data()
        super().showEvent(event)
    
    def calculate_all_salaries(self):
        """Tính lương cho tất cả nhân viên"""
        month = self.month_filter.value()
        year = self.year_filter.value()
        
        QMessageBox.information(self, 'Thông báo', 
                              f'Đã tính lương tự động cho tháng {month}/{year}!\n\n'
                              f'Công thức: Tổng lương = Lương cơ bản + 10% doanh số bán hàng')
        self.load_data()
    
    def debug_data(self):
        """Kiểm tra dữ liệu để debug"""
        month = self.month_filter.value()
        year = self.year_filter.value()
        
        cursor = self.db.conn.cursor()
        
        # Kiểm tra nhân viên
        cursor.execute('SELECT id, full_name, base_salary FROM employees')
        employees = cursor.fetchall()
        
        debug_info = f"Tháng {month}/{year}\n\n"
        debug_info += f"Tổng số nhân viên: {len(employees)}\n\n"
        
        for emp in employees:
            emp_id, name, base_salary = emp
            salary_data = self.db.calculate_salary(emp_id, month, year)
            
            debug_info += f"NV: {name} ({emp_id})\n"
            debug_info += f"  - Lương cơ bản: {base_salary:,.0f} VND\n"
            debug_info += f"  - Doanh số: {salary_data['total_sales']:,.0f} VND\n"
            debug_info += f"  - Hoa hồng: {salary_data['commission']:,.0f} VND\n"
            debug_info += f"  - Tổng lương: {salary_data['total_salary']:,.0f} VND\n\n"
        
        # Kiểm tra hóa đơn
        cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
            FROM invoices 
            WHERE strftime('%m', created_date) = ? 
            AND strftime('%Y', created_date) = ?
        ''', (f"{month:02d}", str(year)))
        
        invoice_result = cursor.fetchone()
        debug_info += f"Hóa đơn tháng {month}/{year}:\n"
        debug_info += f"  - Số hóa đơn: {invoice_result[0]}\n"
        debug_info += f"  - Tổng doanh số: {invoice_result[1]:,.0f} VND"
        
        QMessageBox.information(self, 'Debug Info', debug_info)
    
    def load_data(self):
        month = self.month_filter.value()
        year = self.year_filter.value()
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, full_name, vaitro, base_salary FROM employees')
        employees = cursor.fetchall()
        
        self.table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            employee_id, full_name, vaitro, base_salary = employee
            
            # Tính lương tự động
            salary_data = self.db.calculate_salary(employee_id, month, year)
            
            # Hiển thị thông tin nhân viên
            self.table.setItem(row, 0, QTableWidgetItem(employee_id))
            self.table.setItem(row, 1, QTableWidgetItem(full_name))
            
            # Vai trò
            role_item = QTableWidgetItem("Quản lý" if vaitro == 1 else "Nhân viên")
            self.table.setItem(row, 2, role_item)
            
            # Lương cơ bản
            base_salary_item = QTableWidgetItem(f"{base_salary:,.0f} VND")
            self.table.setItem(row, 3, base_salary_item)
            
            # Doanh số
            sales_item = QTableWidgetItem(f"{salary_data['total_sales']:,.0f} VND")
            self.table.setItem(row, 4, sales_item)
            
            # Hoa hồng 10%
            commission_item = QTableWidgetItem(f"{salary_data['commission']:,.0f} VND")
            self.table.setItem(row, 5, commission_item)
            
            # Tổng lương - với style đặc biệt
            total_salary_item = QTableWidgetItem(f"{salary_data['total_salary']:,.0f} VND")
            
            # Sử dụng setForeground và setFont thay vì setStyleSheet
            total_salary_item.setForeground(QColor('#27AE60'))  # Màu xanh
            font = QFont()
            font.setBold(True)
            total_salary_item.setFont(font)
            
            self.table.setItem(row, 6, total_salary_item)
            
            # Đặt style cho các ô không được chọn/chỉnh sửa
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEditable)
        
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
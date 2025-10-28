from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QSpinBox, QLabel, QGroupBox, QDateEdit)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QFont
from datetime import datetime

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
        filter_group = QGroupBox('Lọc dữ liệu theo ngày')
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel('Từ ngày:'))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))  # Mặc định 1 tháng trước
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat('dd/MM/yyyy')
        self.from_date.dateChanged.connect(self.load_data)
        filter_layout.addWidget(self.from_date)
        
        filter_layout.addWidget(QLabel('Đến ngày:'))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())  # Mặc định hôm nay
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat('dd/MM/yyyy')
        self.to_date.dateChanged.connect(self.load_data)
        filter_layout.addWidget(self.to_date)
        
        filter_layout.addStretch()
        
        # Nút làm mới
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        refresh_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        ''')
        filter_layout.addWidget(refresh_btn)
        
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
    
    def convert_date_format(self, date_str):
        """Chuyển đổi định dạng ngày từ text sang đối tượng datetime"""
        if not date_str:
            return None
            
        # Thử các định dạng ngày phổ biến
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%d/%m/%Y %H:%M:%S',
            '%Y/%m/%d',
            '%Y/%m/%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def is_date_in_range(self, date_str, from_date, to_date):
        """Kiểm tra xem ngày có nằm trong khoảng không"""
        date_obj = self.convert_date_format(date_str)
        if not date_obj:
            return False
            
        # Chuyển QDate thành datetime để so sánh
        from_datetime = datetime(from_date.year(), from_date.month(), from_date.day())
        to_datetime = datetime(to_date.year(), to_date.month(), to_date.day())
        
        return from_datetime <= date_obj <= to_datetime
    
    def calculate_all_salaries(self):
        """Tính lương cho tất cả nhân viên"""
        from_date = self.from_date.date().toString('dd/MM/yyyy')
        to_date = self.to_date.date().toString('dd/MM/yyyy')
        
        QMessageBox.information(self, 'Thông báo', 
                              f'Đã tính lương tự động từ {from_date} đến {to_date}!\n\n'
                              f'Công thức: Tổng lương = Lương cơ bản + 0.5% doanh số bán hàng')
        self.load_data()
    
    def debug_data(self):
        """Kiểm tra dữ liệu để debug"""
        from_date = self.from_date.date()
        to_date = self.to_date.date()
        
        cursor = self.db.conn.cursor()
        
        # Kiểm tra nhân viên
        cursor.execute('SELECT id, full_name, base_salary FROM employees')
        employees = cursor.fetchall()
        
        debug_info = f"Khoảng thời gian: {from_date.toString('dd/MM/yyyy')} đến {to_date.toString('dd/MM/yyyy')}\n\n"
        debug_info += f"Tổng số nhân viên: {len(employees)}\n\n"
        
        for emp in employees:
            emp_id, name, base_salary = emp
            salary_data = self.calculate_salary_by_date(emp_id, from_date, to_date)
            
            debug_info += f"NV: {name} ({emp_id})\n"
            debug_info += f"  - Lương cơ bản: {base_salary:,.0f} VND\n"
            debug_info += f"  - Doanh số: {salary_data['total_sales']:,.0f} VND\n"
            debug_info += f"  - Hoa hồng: {salary_data['commission']:,.0f} VND\n"
            debug_info += f"  - Tổng lương: {salary_data['total_salary']:,.0f} VND\n\n"
        
        # Kiểm tra hóa đơn trong khoảng thời gian
        cursor.execute('SELECT created_date, total_amount FROM invoices')
        all_invoices = cursor.fetchall()
        
        filtered_invoices = []
        total_sales_in_range = 0
        
        for invoice_date, amount in all_invoices:
            if self.is_date_in_range(invoice_date, from_date, to_date):
                filtered_invoices.append((invoice_date, amount))
                total_sales_in_range += amount if amount else 0
        
        debug_info += f"Hóa đơn từ {from_date.toString('dd/MM/yyyy')} đến {to_date.toString('dd/MM/yyyy')}:\n"
        debug_info += f"  - Số hóa đơn: {len(filtered_invoices)}\n"
        debug_info += f"  - Tổng doanh số: {total_sales_in_range:,.0f} VND\n\n"
        
        # Hiển thị một vài hóa đơn mẫu để debug định dạng ngày
        debug_info += "5 hóa đơn gần nhất:\n"
        cursor.execute('SELECT created_date, total_amount FROM invoices ORDER BY created_date DESC LIMIT 5')
        recent_invoices = cursor.fetchall()
        
        for i, (inv_date, amount) in enumerate(recent_invoices, 1):
            date_obj = self.convert_date_format(inv_date)
            formatted_date = date_obj.strftime('%d/%m/%Y') if date_obj else 'Invalid Date'
            debug_info += f"  {i}. {inv_date} -> {formatted_date}: {amount:,.0f} VND\n"
        
        QMessageBox.information(self, 'Debug Info', debug_info)
    
    def calculate_salary_by_date(self, employee_id, from_date, to_date):
        """Tính lương theo khoảng ngày với định dạng text"""
        cursor = self.db.conn.cursor()
        
        # Lấy lương cơ bản
        cursor.execute('SELECT base_salary FROM employees WHERE id = ?', (employee_id,))
        result = cursor.fetchone()
        base_salary = result[0] if result else 0
        
        # Lấy tất cả hóa đơn của nhân viên
        cursor.execute('''
            SELECT created_date, total_amount 
            FROM invoices 
            WHERE employee_id = ?
        ''', (employee_id,))
        
        invoices = cursor.fetchall()
        
        # Lọc hóa đơn trong khoảng thời gian
        total_sales = 0
        for invoice_date, amount in invoices:
            if self.is_date_in_range(invoice_date, from_date, to_date):
                total_sales += amount if amount else 0
        
        # Tính hoa hồng 0.5%
        commission = total_sales * 0.005
        
        # Tổng lương
        total_salary = base_salary + commission
        
        return {
            'base_salary': base_salary,
            'total_sales': total_sales,
            'commission': commission,
            'total_salary': total_salary
        }
    
    def load_data(self):
        from_date = self.from_date.date()
        to_date = self.to_date.date()
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, full_name, vaitro, base_salary FROM employees')
        employees = cursor.fetchall()
        
        self.table.setRowCount(len(employees))
        
        total_base_salary = 0
        total_sales = 0
        total_commission = 0
        total_salary = 0
        
        for row, employee in enumerate(employees):
            employee_id, full_name, vaitro, base_salary = employee
            
            # Tính lương theo khoảng ngày
            salary_data = self.calculate_salary_by_date(employee_id, from_date, to_date)
            
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
            
            # Hoa hồng 0.5%
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
            
            # Cộng dồn tổng
            total_base_salary += base_salary
            total_sales += salary_data['total_sales']
            total_commission += salary_data['commission']
            total_salary += salary_data['total_salary']
            
            # Đặt style cho các ô không được chọn/chỉnh sửa
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEditable)
        
        # Thêm dòng tổng cộng
        self.table.setRowCount(len(employees) + 1)
        total_row = len(employees)
        
        # Tạo các item cho dòng tổng cộng
        total_items = [
            QTableWidgetItem("TỔNG CỘNG"),
            QTableWidgetItem(""),
            QTableWidgetItem(""),
            QTableWidgetItem(f"{total_base_salary:,.0f} VND"),
            QTableWidgetItem(f"{total_sales:,.0f} VND"),
            QTableWidgetItem(f"{total_commission:,.0f} VND"),
            QTableWidgetItem(f"{total_salary:,.0f} VND")
        ]
        
        for col, item in enumerate(total_items):
            # Style cho dòng tổng cộng
            item.setForeground(QColor('#E74C3C'))  # Màu đỏ
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)
            item.setFont(font)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(total_row, col, item)
        
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
        
        # Cập nhật tiêu đề với thông tin khoảng thời gian
        from_date_display = from_date.toString('dd/MM/yyyy')
        to_date_display = to_date.toString('dd/MM/yyyy')
        self.table.setToolTip(f"Dữ liệu lương từ {from_date_display} đến {to_date_display}")
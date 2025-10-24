from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QGridLayout, QComboBox, QSpinBox)
from PyQt6.QtCore import QDate

class StatisticsTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Tháng:'))
        
        self.month_filter = QComboBox()
        self.month_filter.addItems(['Tất cả', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        self.month_filter.currentTextChanged.connect(self.load_statistics)
        filter_layout.addWidget(self.month_filter)
        
        filter_layout.addWidget(QLabel('Năm:'))
        self.year_filter = QSpinBox()
        self.year_filter.setRange(2020, 2030)
        self.year_filter.setValue(QDate.currentDate().year())
        self.year_filter.valueChanged.connect(self.load_statistics)
        filter_layout.addWidget(self.year_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Statistics grid
        grid_layout = QGridLayout()
        
        # Sales statistics
        sales_group = QGroupBox('Thống kê bán hàng')
        sales_layout = QVBoxLayout()
        
        self.total_revenue_label = QLabel('Tổng doanh thu: 0 VND')
        self.total_sales_label = QLabel('Tổng số hóa đơn bán hàng: 0')
        self.avg_sale_label = QLabel('Giá trị trung bình mỗi hóa đơn: 0 VND')
        
        sales_layout.addWidget(self.total_revenue_label)
        sales_layout.addWidget(self.total_sales_label)
        sales_layout.addWidget(self.avg_sale_label)
        sales_group.setLayout(sales_layout)
        grid_layout.addWidget(sales_group, 0, 0)
        
        # Repair statistics
        repair_group = QGroupBox('Thống kê sửa chữa')
        repair_layout = QVBoxLayout()
        
        self.total_repair_revenue_label = QLabel('Tổng doanh thu sửa chữa: 0 VND')
        self.total_repairs_label = QLabel('Tổng số đơn sửa chữa: 0')
        self.completed_repairs_label = QLabel('Đơn đã hoàn thành: 0')
        
        repair_layout.addWidget(self.total_repair_revenue_label)
        repair_layout.addWidget(self.total_repairs_label)
        repair_layout.addWidget(self.completed_repairs_label)
        repair_group.setLayout(repair_layout)
        grid_layout.addWidget(repair_group, 0, 1)
        
        # Inventory statistics
        inventory_group = QGroupBox('Thống kê kho')
        inventory_layout = QVBoxLayout()
        
        self.total_products_label = QLabel('Tổng số sản phẩm: 0')
        self.mechanical_watches_label = QLabel('Đồng hồ cơ: 0')
        self.electronic_watches_label = QLabel('Đồng hồ điện tử: 0')
        self.low_stock_label = QLabel('Sản phẩm sắp hết: 0')
        
        inventory_layout.addWidget(self.total_products_label)
        inventory_layout.addWidget(self.mechanical_watches_label)
        inventory_layout.addWidget(self.electronic_watches_label)
        inventory_layout.addWidget(self.low_stock_label)
        inventory_group.setLayout(inventory_layout)
        grid_layout.addWidget(inventory_group, 1, 0)
        
        # Customer statistics
        customer_group = QGroupBox('Thống kê khách hàng')
        customer_layout = QVBoxLayout()
        
        self.total_customers_label = QLabel('Tổng số khách hàng: 0')
        self.repeat_customers_label = QLabel('Khách hàng thân thiết: 0')
        self.new_customers_month_label = QLabel('Khách hàng mới (tháng): Không có dữ liệu')
        
        customer_layout.addWidget(self.total_customers_label)
        customer_layout.addWidget(self.repeat_customers_label)
        customer_layout.addWidget(self.new_customers_month_label)
        customer_group.setLayout(customer_layout)
        grid_layout.addWidget(customer_group, 1, 1)
        
        layout.addLayout(grid_layout)
        self.setLayout(layout)
    
    def load_statistics(self):
        month = self.month_filter.currentText()
        year = self.year_filter.value()
        
        cursor = self.db.conn.cursor()
        
        # Sales statistics
        if month == 'Tất cả':
            cursor.execute('SELECT SUM(total_amount), COUNT(*) FROM invoices WHERE strftime("%Y", created_date) = ?', (str(year),))
        else:
            cursor.execute('SELECT SUM(total_amount), COUNT(*) FROM invoices WHERE strftime("%m", created_date) = ? AND strftime("%Y", created_date) = ?', 
                          (month.zfill(2), str(year)))
        
        sales_result = cursor.fetchone()
        total_revenue = sales_result[0] or 0
        total_sales = sales_result[1] or 0
        avg_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        self.total_revenue_label.setText(f'Tổng doanh thu: {total_revenue:,.0f} VND')
        self.total_sales_label.setText(f'Tổng số hóa đơn bán hàng: {total_sales}')
        self.avg_sale_label.setText(f'Giá trị trung bình mỗi hóa đơn: {avg_sale:,.0f} VND')
        
        # Repair statistics
        if month == 'Tất cả':
            cursor.execute('SELECT SUM(actual_cost), COUNT(*), SUM(CASE WHEN status = "completed" THEN 1 ELSE 0 END) FROM repair_orders WHERE strftime("%Y", created_date) = ?', (str(year),))
        else:
            cursor.execute('SELECT SUM(actual_cost), COUNT(*), SUM(CASE WHEN status = "completed" THEN 1 ELSE 0 END) FROM repair_orders WHERE strftime("%m", created_date) = ? AND strftime("%Y", created_date) = ?', 
                          (month.zfill(2), str(year)))
        
        repair_result = cursor.fetchone()
        repair_revenue = repair_result[0] or 0
        total_repairs = repair_result[1] or 0
        completed_repairs = repair_result[2] or 0
        
        self.total_repair_revenue_label.setText(f'Tổng doanh thu sửa chữa: {repair_revenue:,.0f} VND')
        self.total_repairs_label.setText(f'Tổng số đơn sửa chữa: {total_repairs}')
        self.completed_repairs_label.setText(f'Đơn đã hoàn thành: {completed_repairs}')
        
        # Inventory statistics
        cursor.execute('SELECT COUNT(*), SUM(CASE WHEN product_type = "mechanical" THEN 1 ELSE 0 END), SUM(CASE WHEN product_type = "electronic" THEN 1 ELSE 0 END), SUM(CASE WHEN quantity < 5 THEN 1 ELSE 0 END) FROM products')
        inventory_result = cursor.fetchone()
        
        self.total_products_label.setText(f'Tổng số sản phẩm: {inventory_result[0] or 0}')
        self.mechanical_watches_label.setText(f'Đồng hồ cơ: {inventory_result[1] or 0}')
        self.electronic_watches_label.setText(f'Đồng hồ điện tử: {inventory_result[2] or 0}')
        self.low_stock_label.setText(f'Sản phẩm sắp hết: {inventory_result[3] or 0}')
        
        # Customer statistics - Sửa phần này
        cursor.execute('SELECT COUNT(*) FROM customers')
        total_customers = cursor.fetchone()[0] or 0
        
        # Repeat customers (customers with more than 1 invoice)
        cursor.execute('''
            SELECT COUNT(*) FROM (
                SELECT customer_id FROM invoices 
                WHERE customer_id IS NOT NULL 
                GROUP BY customer_id HAVING COUNT(*) > 1
            )
        ''')
        repeat_customers = cursor.fetchone()[0] or 0
        
        # Vì bảng customers không có created_date, nên không thể tính khách hàng mới theo tháng
        # Thay vào đó hiển thị thông báo
        self.total_customers_label.setText(f'Tổng số khách hàng: {total_customers}')
        self.repeat_customers_label.setText(f'Khách hàng thân thiết: {repeat_customers}')
        self.new_customers_month_label.setText('Khách hàng mới (tháng): Không có dữ liệu ngày tạo')
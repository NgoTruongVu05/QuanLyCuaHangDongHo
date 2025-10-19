from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class StatisticsTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Statistics labels
        self.total_revenue_label = QLabel('Tổng doanh thu: 0 VND')
        self.total_invoices_label = QLabel('Tổng số hóa đơn: 0')
        self.total_products_label = QLabel('Tổng số sản phẩm: 0')
        self.total_customers_label = QLabel('Tổng số khách hàng: 0')
        
        layout.addWidget(self.total_revenue_label)
        layout.addWidget(self.total_invoices_label)
        layout.addWidget(self.total_products_label)
        layout.addWidget(self.total_customers_label)
        
        self.setLayout(layout)
    
    def load_statistics(self):
        cursor = self.db.conn.cursor()
        
        # Total revenue
        cursor.execute('SELECT SUM(total_amount) FROM invoices')
        total_revenue = cursor.fetchone()[0] or 0
        self.total_revenue_label.setText(f'Tổng doanh thu: {total_revenue:,} VND')
        
        # Total invoices
        cursor.execute('SELECT COUNT(*) FROM invoices')
        total_invoices = cursor.fetchone()[0]
        self.total_invoices_label.setText(f'Tổng số hóa đơn: {total_invoices}')
        
        # Total products
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        self.total_products_label.setText(f'Tổng số sản phẩm: {total_products}')
        
        # Total customers
        cursor.execute('SELECT COUNT(*) FROM customers')
        total_customers = cursor.fetchone()[0]
        self.total_customers_label.setText(f'Tổng số khách hàng: {total_customers}')
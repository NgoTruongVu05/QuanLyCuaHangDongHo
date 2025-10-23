from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt  # Add this import

class InvoiceManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Khách hàng', 'Nhân viên', 'Tổng tiền', 'Ngày tạo', 'Chi tiết'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT i.id, c.name, e.full_name, i.total_amount, i.created_date
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN employees e ON i.employee_id = e.id
            ORDER BY i.id DESC
        ''')
        invoices = cursor.fetchall()
        
        self.table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            for col, value in enumerate(invoice):
                item = QTableWidgetItem(str(value) if value else 'Khách lẻ')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
            
            # Detail button with custom styling
            detail_btn = QPushButton('Xem chi tiết')
            detail_btn.setStyleSheet("""
                QPushButton {
                    margin: 3px;
                    padding: 5px;
                }
            """)
            detail_btn.setFixedHeight(30)
            detail_btn.clicked.connect(lambda checked, inv_id=invoice[0]: self.show_invoice_details(inv_id))
            self.table.setCellWidget(row, 5, detail_btn)
        
        # Adjust column sizes
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setColumnWidth(5, 120)

    def show_invoice_details(self, invoice_id):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.name, id.quantity, id.price, (id.quantity * id.price) as total
            FROM invoice_details id
            JOIN products p ON id.product_id = p.id
            WHERE id.invoice_id = ?
        ''', (invoice_id,))
        details = cursor.fetchall()
        
        detail_text = f"Chi tiết hóa đơn #{invoice_id}:\n\n"
        for detail in details:
            detail_text += f"{detail[0]} - {detail[1]} x {detail[2]:,} = {detail[3]:,} VND\n"
        
        QMessageBox.information(self, 'Chi tiết hóa đơn', detail_text)
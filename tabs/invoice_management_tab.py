from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox,
                             QHeaderView, QComboBox, QHBoxLayout, QLabel)

class InvoiceManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Loại hóa đơn:'))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(['Tất cả', 'Bán hàng', 'Sửa chữa'])
        self.type_filter.currentTextChanged.connect(self.load_data)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Thêm cột hành động
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Tổng tiền', 'Ngày tạo', 'Loại', 'Chi tiết', 'Hành động'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Khách hàng
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nhân viên
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Tổng tiền
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Ngày tạo
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Loại
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Chi tiết
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        invoice_type = self.type_filter.currentText()
        
        if invoice_type == 'Tất cả':
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT i.id, c.name, e.full_name, i.total_amount, i.created_date, i.invoice_type
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                LEFT JOIN employees e ON i.employee_id = e.id
                ORDER BY i.id DESC
            ''')
        elif invoice_type == 'Bán hàng':
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT i.id, c.name, e.full_name, i.total_amount, i.created_date, i.invoice_type
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                LEFT JOIN employees e ON i.employee_id = e.id
                WHERE i.invoice_type = 'sale'
                ORDER BY i.id DESC
            ''')
        else:  # Sửa chữa
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT r.id, c.name, e.full_name, r.actual_cost, r.created_date, 'repair'
                FROM repair_orders r
                LEFT JOIN customers c ON r.customer_id = c.id
                LEFT JOIN employees e ON r.employee_id = e.id
                ORDER BY r.id DESC
            ''')
        
        invoices = cursor.fetchall()
        
        self.table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            for col, value in enumerate(invoice):
                if col == 3:  # Total amount
                    item = QTableWidgetItem(f"{value:,.0f} VND" if value else "0 VND")
                elif col == 5:  # Type
                    type_text = "Bán hàng" if value == 'sale' else "Sửa chữa"
                    item = QTableWidgetItem(type_text)
                else:
                    item = QTableWidgetItem(str(value) if value else 'Khách lẻ')
                
                self.table.setItem(row, col, item)
            
            # Nút chi tiết
            detail_btn = QPushButton('Xem chi tiết')
            detail_btn.setStyleSheet('''
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
            detail_btn.clicked.connect(lambda checked, inv_id=invoice[0], inv_type=invoice[5]: 
                                     self.show_invoice_details(inv_id, inv_type))
            self.table.setCellWidget(row, 6, detail_btn)
            
            # Nút xóa (chỉ cho admin)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            if self.user_role == 1:
                delete_btn = QPushButton('Xóa')
                delete_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 3px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, r=row, inv_id=invoice[0], inv_type=invoice[5]: 
                                         self.delete_invoice_row(r, inv_id, inv_type))
                action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 7, action_widget)
    
    def show_invoice_details(self, invoice_id, invoice_type):
        cursor = self.db.conn.cursor()
        
        if invoice_type == 'sale':
            cursor.execute('''
                SELECT p.name, id.quantity, id.price, (id.quantity * id.price) as total
                FROM invoice_details id
                JOIN products p ON id.product_id = p.id
                WHERE id.invoice_id = ?
            ''', (invoice_id,))
            details = cursor.fetchall()
            
            detail_text = f"Chi tiết hóa đơn bán hàng #{invoice_id}:\n\n"
            total_amount = 0
            for detail in details:
                detail_text += f"{detail[0]} - {detail[1]} x {detail[2]:,} = {detail[3]:,} VND\n"
                total_amount += detail[3]
            detail_text += f"\nTổng cộng: {total_amount:,} VND"
        else:
            cursor.execute('''
                SELECT watch_description, issue_description, estimated_cost, actual_cost, status
                FROM repair_orders WHERE id = ?
            ''', (invoice_id,))
            repair = cursor.fetchone()
            
            detail_text = f"Chi tiết đơn sửa chữa #{invoice_id}:\n\n"
            detail_text += f"Đồng hồ: {repair[0]}\n"
            detail_text += f"Lỗi: {repair[1]}\n"
            detail_text += f"Chi phí dự kiến: {repair[2]:,} VND\n"
            detail_text += f"Chi phí thực tế: {repair[3]:,} VND\n"
            detail_text += f"Trạng thái: {self.get_repair_status_text(repair[4])}\n"
        
        QMessageBox.information(self, 'Chi tiết', detail_text)
    
    def get_repair_status_text(self, status):
        status_map = {
            'pending': 'Chờ xử lý',
            'in_progress': 'Đang sửa',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(status, status)
    
    def delete_invoice_row(self, row, invoice_id, invoice_type):
        invoice_type_text = "hóa đơn bán hàng" if invoice_type == 'sale' else "đơn sửa chữa"
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa {invoice_type_text} #{invoice_id}?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            if invoice_type == 'sale':
                cursor.execute('DELETE FROM invoices WHERE id = ?', (invoice_id,))
            else:
                cursor.execute('DELETE FROM repair_orders WHERE id = ?', (invoice_id,))
            self.db.conn.commit()
            self.load_data()
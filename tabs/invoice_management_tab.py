from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox,
                             QHeaderView, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt

class InvoiceManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.current_mode = "invoices"  # "invoices" hoặc "repairs"
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls layout với 2 button chuyển đổi
        controls_layout = QHBoxLayout()
        
        # Button Quản lý Hóa đơn
        self.invoice_btn = QPushButton('Hóa đơn')
        self.invoice_btn.setFixedHeight(35)
        self.invoice_btn.clicked.connect(lambda: self.switch_mode("invoices"))
        
        # Button Quản lý Sửa chữa
        self.repair_btn = QPushButton('Sửa chữa')
        self.repair_btn.setFixedHeight(35)
        self.repair_btn.clicked.connect(lambda: self.switch_mode("repairs"))
        
        controls_layout.addWidget(self.invoice_btn)
        controls_layout.addWidget(self.repair_btn)
        controls_layout.addStretch()
        
        # Nút làm mới
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.setFixedHeight(35)
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
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Bảng chính
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # Cập nhật trạng thái button ban đầu
        self.update_button_styles()
    
    def switch_mode(self, mode):
        """Chuyển đổi giữa chế độ xem hóa đơn và sửa chữa"""
        self.current_mode = mode
        self.load_data()
        self.update_button_styles()
    
    def update_button_styles(self):
        """Cập nhật style cho button để thể hiện trạng thái active"""
        # Style cho button ACTIVE (đang được chọn)
        active_style = '''
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: 3px solid #F39C12;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
        '''
        
        # Style cho button INACTIVE (không được chọn)
        inactive_invoice_style = '''
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: 2px solid #145A32;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
                border: 2px solid #F39C12;
            }
        '''
        
        inactive_repair_style = '''
            QPushButton {
                background-color: #7D3C98;
                color: white;
                border: 2px solid #4A235A;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #6C3483;
                border: 2px solid #F39C12;
            }
        '''
        
        if self.current_mode == "invoices":
            self.invoice_btn.setStyleSheet(active_style)
            self.repair_btn.setStyleSheet(inactive_repair_style)
        else:
            self.invoice_btn.setStyleSheet(inactive_invoice_style)
            self.repair_btn.setStyleSheet(active_style)
    
    def load_data(self):
        if self.current_mode == "invoices":
            self.load_invoices_data()
        else:
            self.load_repairs_data()
    
    def load_invoices_data(self):
        """Tải dữ liệu hóa đơn - ĐÃ BỎ BỘ LỌC"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT i.id, c.name, e.full_name, i.total_amount, i.created_date, i.invoice_type
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN employees e ON i.employee_id = e.id
            ORDER BY i.id DESC
        ''')
        
        invoices = cursor.fetchall()
        
        self.setup_invoices_table()
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
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
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
    
    def load_repairs_data(self):
        """Tải dữ liệu sửa chữa"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT r.id, c.name, e.full_name, r.watch_description, r.issue_description,
                   r.estimated_cost, r.actual_cost, r.created_date, r.estimated_completion, r.status
            FROM repair_orders r
            LEFT JOIN customers c ON r.customer_id = c.id
            LEFT JOIN employees e ON r.employee_id = e.id
            ORDER BY r.id DESC
        ''')
        repairs = cursor.fetchall()
        
        self.setup_repairs_table()
        self.table.setRowCount(len(repairs))
        
        for row, repair in enumerate(repairs):
            for col, value in enumerate(repair):
                if col in [5, 6]:  # Cost columns
                    item = QTableWidgetItem(f"{value:,.0f} VND" if value else "0 VND")
                elif col == 9:  # Status column
                    status_text = self.get_repair_status_text(value)
                    item = QTableWidgetItem(status_text)
                else:
                    item = QTableWidgetItem(str(value) if value else 'Khách lẻ')
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
            
            # Nút hành động cho từng dòng
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            # Nút xem chi tiết cho tất cả user
            view_btn = QPushButton('Xem chi tiết')
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
            view_btn.clicked.connect(lambda checked, r=row: self.view_repair_details(r))
            action_layout.addWidget(view_btn)
            
            if self.user_role == 1:  # Chỉ admin mới được sửa/xóa
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
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_repair_row(r))
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
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_repair_row(r))
                action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 10, action_widget)
    
    def setup_invoices_table(self):
        """Thiết lập bảng cho chế độ hóa đơn"""
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Tổng tiền', 'Ngày tạo', 'Loại', 'Chi tiết', 'Hành động'
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Khách hàng
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nhân viên
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Tổng tiền
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Ngày tạo
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Loại
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Chi tiết
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
    
    def setup_repairs_table(self):
        """Thiết lập bảng cho chế độ sửa chữa"""
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Đồng hồ', 'Lỗi', 
            'Chi phí dự kiến', 'Chi phí thực', 'Ngày tạo', 'Dự kiến hoàn thành', 'Trạng thái', 'Hành động'
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Khách hàng
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Nhân viên
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Đồng hồ
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Lỗi
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Chi phí dự kiến
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Chi phí thực
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Ngày tạo
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Dự kiến hoàn thành
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Trạng thái
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
    
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
    
    def view_repair_details(self, row):
        repair_id = int(self.table.item(row, 0).text())
        customer = self.table.item(row, 1).text()
        employee = self.table.item(row, 2).text()
        watch_desc = self.table.item(row, 3).text()
        issue_desc = self.table.item(row, 4).text()
        estimated_cost = self.table.item(row, 5).text()
        actual_cost = self.table.item(row, 6).text()
        created_date = self.table.item(row, 7).text()
        estimated_completion = self.table.item(row, 8).text()
        status = self.table.item(row, 9).text()
        
        info_text = f"""
        Thông tin đơn sửa chữa #{repair_id}:
        
        Khách hàng: {customer}
        Nhân viên: {employee}
        Đồng hồ: {watch_desc}
        Lỗi: {issue_desc}
        Chi phí dự kiến: {estimated_cost}
        Chi phí thực tế: {actual_cost}
        Ngày tạo: {created_date}
        Dự kiến hoàn thành: {estimated_completion}
        Trạng thái: {status}
        """
        
        QMessageBox.information(self, 'Chi tiết sửa chữa', info_text)
    
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
    
    def edit_repair_row(self, row):
        repair_id = int(self.table.item(row, 0).text())
        # TODO: Triển khai dialog sửa đơn sửa chữa
        QMessageBox.information(self, 'Thông báo', f'Sửa đơn sửa chữa #{repair_id}')
    
    def delete_repair_row(self, row):
        repair_id = int(self.table.item(row, 0).text())
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa đơn sửa chữa #{repair_id}?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM repair_orders WHERE id = ?', (repair_id,))
            self.db.conn.commit()
            self.load_data()
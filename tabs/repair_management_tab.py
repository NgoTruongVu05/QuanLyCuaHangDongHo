from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView)

class RepairManagementTab(QWidget):
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
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)  # Thêm cột hành động
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Đồng hồ', 'Lỗi', 
            'Chi phí dự kiến', 'Chi phí thực', 'Ngày tạo', 'Dự kiến hoàn thành', 'Trạng thái', 'Hành động'
        ])
        
        # Set column widths
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
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
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
        
        self.table.setRowCount(len(repairs))
        for row, repair in enumerate(repairs):
            for col, value in enumerate(repair):
                if col in [5, 6]:  # Cost columns
                    item = QTableWidgetItem(f"{value:,.0f} VND" if value else "0 VND")
                elif col == 9:  # Status column
                    status_text = self.get_status_text(value)
                    item = QTableWidgetItem(status_text)
                else:
                    item = QTableWidgetItem(str(value) if value else 'Khách lẻ')
                
                self.table.setItem(row, col, item)
            
            # Nút hành động cho từng dòng
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
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
            else:
                # Nhân viên chỉ xem chi tiết
                view_btn = QPushButton('Xem')
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
                view_btn.clicked.connect(lambda checked, r=row: self.view_repair_row(r))
                action_layout.addWidget(view_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 10, action_widget)
    
    def get_status_text(self, status):
        status_map = {
            'pending': 'Chờ xử lý',
            'in_progress': 'Đang sửa',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(status, status)
    
    def edit_repair_row(self, row):
        repair_id = int(self.table.item(row, 0).text())
        # Cần tạo RepairDialog tương tự như các dialog khác
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
    
    def view_repair_row(self, row):
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
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox,
                             QHeaderView, QHBoxLayout, QLabel, QDialog, QWidget as _QWidget,
                             QLineEdit, QDateEdit, QComboBox, QSizePolicy)
from PyQt6.QtCore import Qt, QDate
from dialogs.edit_repair_dialog import EditRepairDialog
from datetime import datetime

def _format_date(val: str) -> str:
    if not val:
        return ''
    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d'):
        try:
            return datetime.strptime(val, fmt).strftime('%d/%m/%Y')
        except Exception:
            continue
    return val

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
        self.invoice_btn = QPushButton('Hóa đơn bán hàng')
        self.invoice_btn.setFixedHeight(35)
        self.invoice_btn.clicked.connect(lambda: self.switch_mode("invoices"))
        
        # Button Quản lý Sửa chữa
        self.repair_btn = QPushButton('Hóa đơn sửa chữa')
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
        
        # Layout tìm kiếm cho hóa đơn bán hàng
        self.invoice_search_layout = QHBoxLayout()
        self.invoice_search_layout.addWidget(QLabel('Loại tìm kiếm:'))
        
        self.search_type = QComboBox()
        self.search_type.addItems(['Tất cả', 'ID hóa đơn', 'Tên khách hàng', 'Tên nhân viên'])
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        self.invoice_search_layout.addWidget(self.search_type)
        
        self.invoice_search_layout.addWidget(QLabel('Từ khóa:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        self.search_input.textChanged.connect(self.search_data)
        self.invoice_search_layout.addWidget(self.search_input)
        self.invoice_search_layout.addWidget(QLabel('Từ ngày:'))
        self.invoice_from_date = QDateEdit()
        self.invoice_from_date.setDate(QDate.currentDate().addMonths(-1))
        self.invoice_from_date.setCalendarPopup(True)
        self.invoice_from_date.dateChanged.connect(self.load_data)
        self.invoice_search_layout.addWidget(self.invoice_from_date)
        
        self.invoice_search_layout.addWidget(QLabel('Đến ngày:'))
        self.invoice_to_date = QDateEdit()
        self.invoice_to_date.setDate(QDate.currentDate())
        self.invoice_to_date.setCalendarPopup(True)
        self.invoice_to_date.dateChanged.connect(self.load_data)
        self.invoice_search_layout.addWidget(self.invoice_to_date)

        self.invoice_search_layout.addStretch()
        
        # Clear button for invoices
        clear_invoice_btn = QPushButton('Xóa tìm kiếm')
        clear_invoice_btn.clicked.connect(self.clear_search)
        clear_invoice_btn.setStyleSheet('''
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        ''')
        self.invoice_search_layout.addWidget(clear_invoice_btn)
        
        # Layout tìm kiếm cho hóa đơn sửa chữa
        self.repair_search_layout = QHBoxLayout()
        
        # Tìm kiếm theo tên đồng hồ
        self.repair_search_layout.addWidget(QLabel('Tìm theo tên đồng hồ:'))
        self.repair_search_input = QLineEdit()
        self.repair_search_input.setPlaceholderText('Nhập tên đồng hồ cần tìm...')
        self.repair_search_input.textChanged.connect(self.load_data)
        self.repair_search_layout.addWidget(self.repair_search_input)
        
        # Thêm lọc theo ngày cho sửa chữa
        self.repair_search_layout.addWidget(QLabel('Từ ngày:'))
        self.repair_date_from = QDateEdit()
        self.repair_date_from.setDate(QDate.currentDate().addMonths(-1))
        self.repair_date_from.setCalendarPopup(True)
        self.repair_date_from.dateChanged.connect(self.load_data)
        self.repair_search_layout.addWidget(self.repair_date_from)
        
        self.repair_search_layout.addWidget(QLabel('Đến ngày:'))
        self.repair_date_to = QDateEdit()
        self.repair_date_to.setDate(QDate.currentDate())
        self.repair_date_to.setCalendarPopup(True)
        self.repair_date_to.dateChanged.connect(self.load_data)
        self.repair_search_layout.addWidget(self.repair_date_to)
        
        # Clear button for repairs
        clear_repair_btn = QPushButton('Xóa tìm kiếm')
        clear_repair_btn.clicked.connect(self.clear_search)
        clear_repair_btn.setStyleSheet('''
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        ''')
        self.repair_search_layout.addWidget(clear_repair_btn)
        
        # Thêm các layout tìm kiếm vào layout chính
        layout.addLayout(self.invoice_search_layout)
        layout.addLayout(self.repair_search_layout)
        
        # Bảng chính
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # Ẩn/hiện các controls tìm kiếm theo mode
        self.update_search_controls()
        # Cập nhật trạng thái button ban đầu
        self.update_button_styles()

    def on_search_type_changed(self, search_type):
        """Cập nhật placeholder khi loại tìm kiếm thay đổi"""
        if search_type == 'ID hóa đơn':
            self.search_input.setPlaceholderText('Nhập ID hóa đơn...')
        elif search_type == 'Tên khách hàng':
            self.search_input.setPlaceholderText('Nhập tên khách hàng...')
        elif search_type == 'Tên nhân viên':
            self.search_input.setPlaceholderText('Nhập tên nhân viên...')
        else:
            self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')

    def search_data(self):
        """Tìm kiếm dữ liệu dựa trên loại tìm kiếm và từ khóa"""
        if self.current_mode == "invoices":
            self.search_invoices()
        else:
            self.load_repairs_data()

    def search_invoices(self):
        """Tìm kiếm hóa đơn dựa trên loại và từ khóa"""
        search_type = self.search_type.currentText()
        search_text = self.search_input.text().strip()
        from_date = self.invoice_from_date.date().toString('yyyy-MM-dd')
        to_date = self.invoice_to_date.date().toString('yyyy-MM-dd')
        
        cursor = self.db.conn.cursor()
        
        base_query = '''
            SELECT i.id, c.name, e.full_name, i.total_amount, i.created_date
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN employees e ON i.employee_id = e.id
            WHERE i.created_date BETWEEN ? AND ?
        '''
        params = [from_date, to_date]
        
        if search_text:
            if search_type == 'Tất cả':
                base_query += ' AND (LOWER(i.id) LIKE ? OR LOWER(c.name) LIKE ? OR LOWER(e.full_name) LIKE ?)'
                search_term = f'%{search_text.lower()}%'
                params.extend([search_term, search_term, search_term])
            elif search_type == 'ID hóa đơn':
                base_query += ' AND LOWER(i.id) LIKE ?'
                params.append(f'%{search_text.lower()}%')
            elif search_type == 'Tên khách hàng':
                base_query += ' AND LOWER(c.name) LIKE ?'
                params.append(f'%{search_text.lower()}%')
            elif search_type == 'Tên nhân viên':
                base_query += ' AND LOWER(e.full_name) LIKE ?'
                params.append(f'%{search_text.lower()}%')
        
        base_query += ' ORDER BY i.id DESC'
        
        cursor.execute(base_query, params)
        invoices = cursor.fetchall()
        
        self.setup_invoices_table()
        self.table.setRowCount(len(invoices))
        
        for row, invoice in enumerate(invoices):
            for col, value in enumerate(invoice):
                if col == 3:  # Total amount
                    item = QTableWidgetItem(f"{value:,.0f} VND" if value else "0 VND")
                elif col == 4:
                    item = QTableWidgetItem(_format_date(value))
                else:
                    item = QTableWidgetItem(str(value) if value else 'Khách lẻ')
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

            detail_widget = QWidget()
            detail_layout = QHBoxLayout(detail_widget)
            detail_layout.setContentsMargins(4, 0, 4, 0)
            detail_layout.setSpacing(0)
            
            # Nút chi tiết
            detail_btn = QPushButton('Xem chi tiết')
            detail_btn.setFixedSize(72, 26)
            detail_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            detail_btn.setStyleSheet('''
                QPushButton {
                    background-color: #1E88E5;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 3px 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
            ''')
            detail_btn.clicked.connect(lambda checked, inv_id=invoice[0]: 
                                    self.show_invoice_details(inv_id))
            detail_layout.addStretch()
            detail_layout.addWidget(detail_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            detail_layout.addStretch()
            self.table.setCellWidget(row, 5, detail_widget)
            self.table.setRowHeight(row, max(self.table.rowHeight(row), 36))

    def clear_search(self):
        """Xóa tất cả các điều kiện tìm kiếm"""
        if self.current_mode == "invoices":
            self.search_type.setCurrentText('Tất cả')
            self.search_input.clear()
            self.invoice_from_date.setDate(QDate.currentDate().addMonths(-1))
            self.invoice_to_date.setDate(QDate.currentDate())
        else:
            # Xóa cả tìm kiếm tên đồng hồ và reset ngày
            self.repair_search_input.clear()
            self.repair_date_from.setDate(QDate.currentDate().addMonths(-1))
            self.repair_date_to.setDate(QDate.currentDate())
        self.load_data()
    
    def switch_mode(self, mode):
        """Chuyển đổi giữa chế độ xem hóa đơn và sửa chữa"""
        self.current_mode = mode
        self.update_search_controls()
        self.load_data()
        self.update_button_styles()
        
    def update_search_controls(self):
        """Ẩn/hiện các controls tìm kiếm tương ứng với mode hiện tại"""
        if self.current_mode == "invoices":
            # Hiện tìm kiếm theo ngày cho hóa đơn
            for i in range(self.invoice_search_layout.count()):
                widget = self.invoice_search_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            # Ẩn tìm kiếm theo tên đồng hồ
            for i in range(self.repair_search_layout.count()):
                widget = self.repair_search_layout.itemAt(i).widget()
                if widget:
                    widget.hide()
        else:
            # Ẩn tìm kiếm theo ngày
            for i in range(self.invoice_search_layout.count()):
                widget = self.invoice_search_layout.itemAt(i).widget()
                if widget:
                    widget.hide()
            # Hiện tìm kiếm theo tên đồng hồ
            for i in range(self.repair_search_layout.count()):
                widget = self.repair_search_layout.itemAt(i).widget()
                if widget:
                    widget.show()

    def edit_repair_row(self, row):
        """Mở dialog sửa đơn sửa chữa; reload khi dialog trả về Accepted"""
        repair_id = int(self.table.item(row, 0).text())
        dialog = EditRepairDialog(self.db, repair_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
    
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
                background-color:#27AE60;
                color: white;
                border: 2px solid #4A235A;
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
        
        if self.current_mode == "invoices":
            self.invoice_btn.setStyleSheet(active_style)
            self.repair_btn.setStyleSheet(inactive_repair_style)
        else:
            self.invoice_btn.setStyleSheet(inactive_invoice_style)
            self.repair_btn.setStyleSheet(active_style)
    
    def load_data(self):
        """Tải dữ liệu theo chế độ hiện tại"""
        if self.current_mode == "invoices":
            self.load_invoices_data()
        else:
            self.load_repairs_data()
    
    def load_invoices_data(self):
        """Tải dữ liệu hóa đơn - không lọc"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT i.id, c.name, e.full_name, i.total_amount, i.created_date
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
                elif col == 4:
                    item = QTableWidgetItem(_format_date(value))
                else:
                    item = QTableWidgetItem(str(value) if value else 'Khách lẻ')
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

            detail_widget = QWidget()
            detail_layout = QHBoxLayout(detail_widget)
            detail_layout.setContentsMargins(4, 0, 4, 0)
            detail_layout.setSpacing(0)
            
            # Nút chi tiết
            detail_btn = QPushButton('Xem chi tiết')
            detail_btn.setFixedSize(72, 26)
            detail_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            detail_btn.setStyleSheet('''
                QPushButton {
                    background-color: #1E88E5;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 3px 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
            ''')
            detail_btn.clicked.connect(lambda checked, inv_id=invoice[0]:
                                    self.show_invoice_details(inv_id))
            detail_layout.addStretch()
            detail_layout.addWidget(detail_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            detail_layout.addStretch()
            self.table.setCellWidget(row, 5, detail_widget)
            self.table.setRowHeight(row, max(self.table.rowHeight(row), 36))
    
    def load_repairs_data(self):
        """Tải dữ liệu sửa chữa và lọc theo tên đồng hồ và khoảng thời gian"""
        cursor = self.db.conn.cursor()
        
        # Lấy các điều kiện lọc
        watch_search = self.repair_search_input.text().strip().lower()
        from_date = self.repair_date_from.date().toString('yyyy-MM-dd')
        to_date = self.repair_date_to.date().toString('yyyy-MM-dd')
        
        # Xây dựng query với điều kiện lọc ngày
        query = '''
            SELECT r.id, c.name, e.full_name, r.watch_description, r.issue_description,
                   COALESCE(r.actual_cost, 0.0) as actual_cost, r.created_date, 
                   r.estimated_completion, r.status
            FROM repair_orders r
            LEFT JOIN customers c ON r.customer_id = c.id
            LEFT JOIN employees e ON r.employee_id = e.id
            WHERE DATE(r.created_date) BETWEEN ? AND ?
        '''
        params = [from_date, to_date]
        
        # Thêm điều kiện tìm kiếm theo tên đồng hồ nếu có
        if watch_search:
            query += ' AND LOWER(r.watch_description) LIKE ?'
            params.append(f'%{watch_search}%')
        
        query += ' ORDER BY r.id DESC'
        
        cursor.execute(query, params)
        
        repairs = cursor.fetchall()
        
        self.setup_repairs_table()
        self.table.setRowCount(len(repairs))
        
        for row, rep in enumerate(repairs):
            (rid, cust_name, emp_name, watch_desc, issue_desc,
             actual_cost, created_date, est_completion, status) = rep

            # ID
            item = QTableWidgetItem(str(rid))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, item)

            # Khách hàng
            item = QTableWidgetItem(str(cust_name) if cust_name else 'Khách lẻ')
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, item)
            # Nhân viên
            item = QTableWidgetItem(str(emp_name) if emp_name else '')
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, item)

            # Đồng hồ
            item = QTableWidgetItem(str(watch_desc) if watch_desc else '')
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, item)

            # Lỗi
            item = QTableWidgetItem(str(issue_desc) if issue_desc else '')
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 4, item)

            # Chi phí
            try:
                item = QTableWidgetItem(f"{float(actual_cost):,.0f} VND")
            except Exception:
                item = QTableWidgetItem("0 VND")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 5, item)

            # Ngày tạo
            item = QTableWidgetItem(str(created_date) if created_date else '')
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 6, item)

            # Dự kiến hoàn thành
            item = QTableWidgetItem(str(est_completion) if est_completion else '')
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 7, item)

            # Trạng thái 
            item = QTableWidgetItem(self.get_repair_status_text(status))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 8, item)
            # Nút hành động cho từng dòng
            action_widget = _QWidget()
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
            self.table.setCellWidget(row, 9, action_widget)
    
    def setup_invoices_table(self):
        """Thiết lập bảng cho chế độ hóa đơn"""
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Tổng tiền', 'Ngày tạo', 'Chi tiết'
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Khách hàng
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nhân viên
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Tổng tiền
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Ngày tạo
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Chi tiết
    
    def setup_repairs_table(self):
        """Thiết lập bảng cho chế độ sửa chữa"""
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Đồng hồ', 'Lỗi'
            , 'Chi phí', 'Ngày tạo', 'Dự kiến hoàn thành', 'Trạng thái', 'Hành động'
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Khách hàng
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Nhân viên
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Đồng hồ
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Lỗi
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Chi phí
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Ngày tạo
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Dự kiến hoàn thành
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Trạng thái
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
    
    def show_invoice_details(self, invoice_id):
        cursor = self.db.conn.cursor()
        # Lấy header hóa đơn
        cursor.execute('''
            SELECT i.id, i.created_date, i.total_amount,
                   c.name, c.phone, c.address, e.full_name
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN employees e ON i.employee_id = e.id
            WHERE i.id = ?
        ''', (invoice_id,))
        header = cursor.fetchone()

        if not header:
            QMessageBox.warning(self, 'Lỗi', f'Không tìm thấy hóa đơn #{invoice_id}')
            return

        inv_id, created_date, total_amount, cust_name, cust_phone, cust_addr, emp_name = header
        cust_name = cust_name
        created_date_fmt = _format_date(created_date)
        emp_name = emp_name or ''

        # Lấy chi tiết sản phẩm
        cursor.execute('''
            SELECT p.name, id.quantity, id.price, (id.quantity * id.price) as line_total
            FROM invoice_details id
            JOIN products p ON id.product_id = p.id
            WHERE id.invoice_id = ?
        ''', (invoice_id,))
        details = cursor.fetchall()

        lines = [
            f"HÓA ĐƠN #{inv_id}",
            f"Ngày tạo: {created_date_fmt}",
            f"Khách hàng: {cust_name}",
        ]
        if cust_phone:
            lines.append(f"SĐT: {cust_phone}")
        if cust_addr:
            lines.append(f"Địa chỉ: {cust_addr}")
        lines.append(f"Nhân viên: {emp_name}")
        lines.append("\n--- Chi tiết sản phẩm ---")

        for i, (name, qty, price, line_total) in enumerate(details, 1):
            lines.append(
                f"\n{i}. {name}\n"
                f"   Số lượng : {qty}\n"
                f"   Đơn giá  : {price:,.0f} VND\n"
                f"   Thành tiền: {line_total:,.0f} VND"
            )

        lines.append("\n-------------------------")
        total_display = total_amount or sum(d[3] for d in details)
        lines.append(f"TỔNG CỘNG: {total_display:,.0f} VND")

        detail_text = "\n".join(lines)
        QMessageBox.information(self, f'Hóa đơn #{inv_id}', detail_text)
    
    def view_repair_details(self, row):
        repair_id = int(self.table.item(row, 0).text())
        customer = self.table.item(row, 1).text()
        employee = self.table.item(row, 2).text()
        watch_desc = self.table.item(row, 3).text()
        issue_desc = self.table.item(row, 4).text()
        actual_cost = self.table.item(row, 5).text()
        created_date = self.table.item(row, 6).text()
        estimated_completion = self.table.item(row, 7).text()
        status = self.table.item(row, 8).text()
        
        info_text = f"""
        Thông tin đơn sửa chữa #{repair_id}:
        
        Khách hàng: {customer}
        Nhân viên: {employee}
        Đồng hồ: {watch_desc}
        Lỗi: {issue_desc}
        Chi phí: {actual_cost}
        Ngày tạo: {created_date}
        Dự kiến hoàn thành: {estimated_completion}
        Trạng thái: {status}
        """
        
        QMessageBox.information(self, 'Chi tiết sửa chữa', info_text)
    
    def get_repair_status_text(self, status):
        status_map = {
            'Chờ xử lý': 'Chờ xử lý',
            'Hoàn thành': 'Hoàn thành',
            'Đã hủy': 'Đã hủy'
        }
        return status_map.get(status, status)
    
    def delete_repair_row(self, row):
        repair_id = int(self.table.item(row, 0).text())
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa đơn sửa chữa #{repair_id}?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM repair_orders WHERE id = ?', (repair_id,))
            self.db.conn.commit()
            self.load_data()
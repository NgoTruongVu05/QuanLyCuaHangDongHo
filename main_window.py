from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTabWidget, QLabel, QMessageBox)
from tabs.create_invoice_tab import CreateInvoiceTab
from tabs.create_repair_tab import CreateRepairTab
from tabs.product_management_tab import ProductManagementTab
from tabs.customer_management_tab import CustomerManagementTab
from tabs.invoice_management_tab import InvoiceManagementTab
from tabs.repair_management_tab import RepairManagementTab
from tabs.statistics_tab import StatisticsTab
from tabs.employee_management_tab import EmployeeManagementTab
from tabs.salary_management_tab import SalaryManagementTab

class MainWindow(QMainWindow):
    def __init__(self, user_info, db):
        super().__init__()
        self.user_info = user_info
        self.db = db
        self.user_role = user_info[4]  # vaitro ở index 4 (đã bỏ username)
        self.init_ui()
    
    def init_ui(self):
        # Hiển thị thông tin người dùng - HIỂN THỊ ID
        user_id = self.user_info[0]  # id ở index 0
        role_text = "Quản lý" if self.user_role == 1 else "Nhân viên"
        self.setWindowTitle(f'Hệ thống quản lý cửa hàng đồng hồ - {user_id} ({role_text})')
        self.setGeometry(100, 100, 1200, 700)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header với thông tin user và nút đăng xuất
        header_layout = QHBoxLayout()
        
        # HIỂN THỊ ID THAY VÌ USERNAME
        user_info_text = f'{user_id} ({role_text})'
        self.user_info_label = QLabel(user_info_text)
        self.user_info_label.setStyleSheet('font-weight: bold; color: #2E86AB;')
        header_layout.addWidget(self.user_info_label)
        
        header_layout.addStretch()
        
        self.logout_btn = QPushButton('Đăng xuất')
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.setStyleSheet('''
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        ''')
        header_layout.addWidget(self.logout_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Tab bán hàng và sửa chữa (luôn hiển thị)
        self.create_invoice_tab = CreateInvoiceTab(self.db, self.user_info[0])  # id ở index 0
        self.create_repair_tab = CreateRepairTab(self.db, self.user_info[0])
        self.tabs.addTab(self.create_invoice_tab, "Bán hàng")
        self.tabs.addTab(self.create_repair_tab, "Sửa chữa")
        
        # Các tab quản lý
        self.product_tab = ProductManagementTab(self.db, self.user_role)
        self.customer_tab = CustomerManagementTab(self.db, self.user_role)
        self.invoice_tab = InvoiceManagementTab(self.db, self.user_role)
        self.repair_tab = RepairManagementTab(self.db, self.user_role)
        self.statistics_tab = StatisticsTab(self.db, self.user_role)
        
        # Thêm các tab cơ bản cho cả admin và nhân viên
        self.tabs.addTab(self.product_tab, "Quản lý sản phẩm")
        self.tabs.addTab(self.customer_tab, "Quản lý khách hàng")
        self.tabs.addTab(self.invoice_tab, "Quản lý hóa đơn")
        self.tabs.addTab(self.repair_tab, "Quản lý sửa chữa")
        self.tabs.addTab(self.statistics_tab, "Thống kê")
        
        # Chỉ thêm tab quản lý nhân viên và lương cho admin
        if self.user_role == 1:
            self.employee_tab = EmployeeManagementTab(self.db, self.user_role)
            self.salary_tab = SalaryManagementTab(self.db, self.user_role)
            self.tabs.addTab(self.employee_tab, "Quản lý nhân viên")
            self.tabs.addTab(self.salary_tab, "Quản lý lương")
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def logout(self):
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   'Bạn có chắc muốn đăng xuất?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def on_tab_changed(self, index):
        """Handle tab changed event"""
        current_tab = self.tabs.widget(index)
        
        # Reload data for each tab type
        if isinstance(current_tab, CreateInvoiceTab):
            current_tab.load_data()
        elif isinstance(current_tab, InvoiceManagementTab):
            current_tab.load_data()
        elif isinstance(current_tab, ProductManagementTab):
            current_tab.load_data()
        elif isinstance(current_tab, CustomerManagementTab):
            current_tab.load_data()
        elif isinstance(current_tab, EmployeeManagementTab):
            current_tab.load_data()
        elif isinstance(current_tab, StatisticsTab):
            current_tab.load_statistics()
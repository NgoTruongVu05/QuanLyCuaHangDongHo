from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTabWidget, QLabel, QMessageBox)
from tabs.create_invoice_tab import CreateInvoiceTab
from tabs.product_management_tab import ProductManagementTab
from tabs.customer_management_tab import CustomerManagementTab
from tabs.invoice_management_tab import InvoiceManagementTab
from tabs.statistics_tab import StatisticsTab
from tabs.employee_management_tab import EmployeeManagementTab
from dialogs.login_dialog import LoginDialog

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_info = None  # Chưa đăng nhập
        self.user_role = 0     # Mặc định là khách
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Hệ thống quản lý cửa hàng đồng hồ - Chưa đăng nhập')
        self.setGeometry(100, 100, 1200, 700)
        
        # Central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header với nút đăng nhập
        header_layout = QHBoxLayout()
        
        self.user_info_label = QLabel('Chưa đăng nhập')
        header_layout.addWidget(self.user_info_label)
        
        header_layout.addStretch()
        
        self.login_btn = QPushButton('Đăng nhập')
        self.login_btn.clicked.connect(self.show_login)
        header_layout.addWidget(self.login_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab Tạo hóa đơn (luôn hiển thị)
        self.create_invoice_tab = CreateInvoiceTab(self.db, None)  # user_id = None cho khách
        self.tabs.addTab(self.create_invoice_tab, "Tạo hóa đơn")
        
        # Các tab quản lý (ban đầu ẩn)
        self.product_tab = ProductManagementTab(self.db, 0)
        self.customer_tab = CustomerManagementTab(self.db, 0)
        self.invoice_tab = InvoiceManagementTab(self.db, 0)
        self.statistics_tab = StatisticsTab(self.db, 0)
        self.employee_tab = EmployeeManagementTab(self.db, 0)
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Ẩn các tab quản lý ban đầu
        self.hide_management_tabs()
    
    def hide_management_tabs(self):
        """Ẩn tất cả tab quản lý"""
        for i in range(self.tabs.count() - 1, 0, -1):  # Giữ lại tab đầu tiên (tạo hóa đơn)
            self.tabs.removeTab(i)
    
    def show_management_tabs(self):
        """Hiển thị tab quản lý theo vai trò"""
        # Thêm các tab cơ bản
        self.tabs.addTab(self.product_tab, "Quản lý sản phẩm")
        self.tabs.addTab(self.customer_tab, "Quản lý khách hàng")
        self.tabs.addTab(self.invoice_tab, "Quản lý hóa đơn")
        self.tabs.addTab(self.statistics_tab, "Thống kê")
        
        # Thêm tab quản lý nhân viên nếu là quản lý
        if self.user_role == 1:
            self.tabs.addTab(self.employee_tab, "Quản lý nhân viên")
    
    def show_login(self):
        """Hiển thị dialog đăng nhập"""
        login_dialog = LoginDialog(self.db)
        if login_dialog.exec():
            self.user_info = login_dialog.user_info
            self.user_role = self.user_info[4]  # vaitro
            
            # Cập nhật giao diện
            role_text = "Quản lý" if self.user_role == 1 else "Nhân viên"
            self.user_info_label.setText(f'{self.user_info[3]} ({role_text})')
            self.login_btn.setText('Đăng xuất')
            self.login_btn.clicked.disconnect()
            self.login_btn.clicked.connect(self.logout)
            
            # Hiển thị tab quản lý
            self.show_management_tabs()
            
            # Cập nhật user_id cho tab tạo hóa đơn
            self.create_invoice_tab.user_id = self.user_info[0]
            
            self.setWindowTitle(f'Hệ thống quản lý cửa hàng đồng hồ - {self.user_info[3]}')
            
            QMessageBox.information(self, 'Thành công', f'Đăng nhập thành công với vai trò {role_text}!')
    
    def logout(self):
        """Đăng xuất"""
        self.user_info = None
        self.user_role = 0
        
        # Cập nhật giao diện
        self.user_info_label.setText('Chưa đăng nhập')
        self.login_btn.setText('Đăng nhập')
        self.login_btn.clicked.disconnect()
        self.login_btn.clicked.connect(self.show_login)
        
        # Ẩn tab quản lý
        self.hide_management_tabs()
        
        # Reset user_id cho tab tạo hóa đơn
        self.create_invoice_tab.user_id = None
        
        self.setWindowTitle('Hệ thống quản lý cửa hàng đồng hồ - Chưa đăng nhập')
        
        QMessageBox.information(self, 'Thông báo', 'Đã đăng xuất!')
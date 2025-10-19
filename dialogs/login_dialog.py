from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QMessageBox)

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Đăng nhập hệ thống')
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Form đăng nhập
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Nhập tên đăng nhập')
        form_layout.addRow('Tên đăng nhập:', self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Nhập mật khẩu')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow('Mật khẩu:', self.password_input)
        
        layout.addLayout(form_layout)
        
        # Nút đăng nhập
        login_btn = QPushButton('Đăng nhập')
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin!')
            return
        
        user = self.db.verify_login(username, password)
        if user:
            self.user_info = user
            self.accept()
        else:
            QMessageBox.warning(self, 'Lỗi', 'Tên đăng nhập hoặc mật khẩu không đúng!')
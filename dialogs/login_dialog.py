from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QMessageBox,
                             QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Đăng nhập hệ thống')
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Tiêu đề
        title_label = QLabel('ĐĂNG NHẬP HỆ THỐNG')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        layout.addSpacing(20)
        
        # Form đăng nhập
        form_layout = QFormLayout()
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Nhập ID hoặc Username')
        self.login_input.setMinimumHeight(35)
        form_layout.addRow('Đăng nhập:', self.login_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Nhập mật khẩu')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        form_layout.addRow('Mật khẩu:', self.password_input)
        
        layout.addLayout(form_layout)
        
        layout.addSpacing(20)
        
        # Nút đăng nhập
        login_btn = QPushButton('ĐĂNG NHẬP')
        login_btn.setMinimumHeight(40)
        login_btn.setStyleSheet('''
            QPushButton {
                background-color: #2E86AB;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B6B93;
            }
        ''')
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
        
        # Set focus vào ô đăng nhập
        self.login_input.setFocus()
    
    def login(self):
        login_input = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        if not login_input or not password:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin!')
            return
        
        user = self.db.verify_login(login_input, password)
        if user:
            self.user_info = user
            self.accept()
        else:
            QMessageBox.warning(self, 'Lỗi', 'Thông tin đăng nhập không đúng!')
import sys
from PyQt6.QtWidgets import QApplication
from database import Database
from dialogs.login_dialog import LoginDialog
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Khởi tạo database
    db = Database()
    
    # Hiển thị dialog đăng nhập đầu tiên
    login_dialog = LoginDialog(db)
    if login_dialog.exec():
        user_info = login_dialog.user_info
        # Hiển thị main window sau khi đăng nhập thành công
        main_window = MainWindow(user_info, db)
        main_window.show()
        sys.exit(app.exec())
    else:
        # Thoát ứng dụng nếu không đăng nhập
        sys.exit(0)

if __name__ == '__main__':
    main()
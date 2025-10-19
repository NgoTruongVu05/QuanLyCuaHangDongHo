import sys
from PyQt6.QtWidgets import QApplication
from database import Database
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Khởi tạo database
    db = Database()
    
    # Hiển thị main window trực tiếp (trang tạo hóa đơn)
    main_window = MainWindow(db)
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
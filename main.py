import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont
from database import Database
from dialogs.login_dialog import LoginDialog
from main_window import MainWindow

def set_app_style(app):
    # Set application-wide font
    app.setFont(QFont('Segoe UI', 10))
    
    # Set modern style
    app.setStyle('Fusion')
    
    # Set color palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    app.setPalette(palette)
    
    # Set stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #353535;
        }
        QPushButton {
            background-color: #2a82da;
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #3891e8;
        }
        QPushButton:pressed {
            background-color: #1e5b99;
        }
        QTableWidget {
            gridline-color: #5c5c5c;
            background-color: #252525;
            border: 1px solid #5c5c5c;
            border-radius: 4px;
            padding: 2px;
        }
        QTableWidget::item {
            padding: 6px;
        }
        QHeaderView::section {
            background-color: #353535;
            padding: 6px;
            border: 1px solid #5c5c5c;
            font-weight: bold;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            padding: 6px;
            background-color: #252525;
            border: 1px solid #5c5c5c;
            border-radius: 4px;
            color: white;
        }
        QLabel {
            color: white;
        }
        QTabWidget::pane {
            border: 1px solid #5c5c5c;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #353535;
            color: white;
            padding: 8px 16px;
            border: 1px solid #5c5c5c;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #2a82da;
        }
        QTabBar::tab:hover {
            background-color: #3891e8;
        }
    """)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    set_app_style(app)
    
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
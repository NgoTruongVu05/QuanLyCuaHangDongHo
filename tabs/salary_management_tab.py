from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QComboBox, QSpinBox, QLabel, QFormLayout,
                             QGroupBox)
from PyQt6.QtCore import QDate
from dialogs.salary_dialog import SalaryDialog

class SalaryManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Filter section
        filter_group = QGroupBox('Lọc dữ liệu')
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel('Tháng:'))
        self.month_filter = QSpinBox()
        self.month_filter.setRange(1, 12)
        self.month_filter.setValue(QDate.currentDate().month())
        self.month_filter.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.month_filter)
        
        filter_layout.addWidget(QLabel('Năm:'))
        self.year_filter = QSpinBox()
        self.year_filter.setRange(2020, 2030)
        self.year_filter.setValue(QDate.currentDate().year())
        self.year_filter.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.year_filter)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_btn = QPushButton('Thêm bảng lương')
        add_btn.clicked.connect(self.add_salary)
        controls_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)  # Thêm cột hành động
        self.table.setHorizontalHeaderLabels([
            'ID', 'Nhân viên', 'Tháng', 'Năm', 'Lương cơ bản', 
            'Thưởng', 'Khấu trừ', 'Tổng lương', 'Trạng thái', 'Hành động'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên NV
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Tháng
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Năm
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Lương cơ bản
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Thưởng
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Khấu trừ
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Tổng lương
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Trạng thái
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        month = self.month_filter.value()
        year = self.year_filter.value()
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT s.id, e.full_name, s.month, s.year, s.base_salary, 
                   s.bonus, s.deductions, s.total_salary, s.status
            FROM salaries s
            JOIN employees e ON s.employee_id = e.id
            WHERE s.month = ? AND s.year = ?
            ORDER BY s.id DESC
        ''', (month, year))
        
        salaries = cursor.fetchall()
        
        self.table.setRowCount(len(salaries))
        for row, salary in enumerate(salaries):
            for col, value in enumerate(salary):
                if col in [4, 5, 6, 7]:  # Salary columns
                    item = QTableWidgetItem(f"{value:,.0f} VND")
                elif col == 8:  # Status column
                    status_text = "Đã thanh toán" if value == 'paid' else "Chờ thanh toán"
                    item = QTableWidgetItem(status_text)
                else:
                    item = QTableWidgetItem(str(value))
                
                self.table.setItem(row, col, item)
            
            # Nút hành động cho từng dòng
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
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
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_salary_row(r))
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
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_salary_row(r))
            action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 9, action_widget)
    
    def add_salary(self):
        dialog = SalaryDialog(self.db)
        if dialog.exec():
            self.load_data()
    
    def edit_salary_row(self, row):
        salary_id = int(self.table.item(row, 0).text())
        dialog = SalaryDialog(self.db, salary_id)
        if dialog.exec():
            self.load_data()
    
    def delete_salary_row(self, row):
        salary_id = int(self.table.item(row, 0).text())
        employee_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa bảng lương của "{employee_name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM salaries WHERE id = ?', (salary_id,))
            self.db.conn.commit()
            self.load_data()
from PyQt6.QtWidgets import (QDialog, QFormLayout, QComboBox, QPushButton, 
                             QDoubleSpinBox, QMessageBox, QSpinBox, QLabel,
                             QHBoxLayout, QWidget)
from PyQt6.QtCore import QDate

class SalaryDialog(QDialog):
    def __init__(self, db, salary_id=None):
        super().__init__()
        self.db = db
        self.salary_id = salary_id
        self.init_ui()
        if salary_id:
            self.load_salary_data()
        else:
            self.load_employees()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa lương' if not self.salary_id else 'Sửa lương')
        self.setFixedSize(400, 400)
        
        layout = QFormLayout()
        
        self.employee_combo = QComboBox()
        layout.addRow('Nhân viên:', self.employee_combo)
        
        # Tạo widget chứa cho tháng và năm
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        date_layout.addWidget(QLabel('Tháng:'))
        self.month_input = QSpinBox()
        self.month_input.setRange(1, 12)
        self.month_input.setValue(QDate.currentDate().month())
        date_layout.addWidget(self.month_input)
        
        date_layout.addWidget(QLabel('Năm:'))
        self.year_input = QSpinBox()
        self.year_input.setRange(2020, 2030)
        self.year_input.setValue(QDate.currentDate().year())
        date_layout.addWidget(self.year_input)
        
        date_layout.addStretch()
        layout.addRow('Thời gian:', date_widget)
        
        self.base_salary_input = QDoubleSpinBox()
        self.base_salary_input.setMaximum(999999999)
        self.base_salary_input.setPrefix('VND ')
        layout.addRow('Lương cơ bản:', self.base_salary_input)
        
        self.bonus_input = QDoubleSpinBox()
        self.bonus_input.setMaximum(999999999)
        self.bonus_input.setPrefix('VND ')
        layout.addRow('Thưởng:', self.bonus_input)
        
        self.deductions_input = QDoubleSpinBox()
        self.deductions_input.setMaximum(999999999)
        self.deductions_input.setPrefix('VND ')
        layout.addRow('Khấu trừ:', self.deductions_input)
        
        self.total_label = QLabel('0 VND')
        layout.addRow('Tổng lương:', self.total_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Chờ thanh toán', 'Đã thanh toán'])
        layout.addRow('Trạng thái:', self.status_combo)
        
        # Connect signals for auto-calculation
        self.base_salary_input.valueChanged.connect(self.calculate_total)
        self.bonus_input.valueChanged.connect(self.calculate_total)
        self.deductions_input.valueChanged.connect(self.calculate_total)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_salary)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
        self.calculate_total()  # Tính tổng ban đầu
    
    def load_employees(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, full_name FROM employees')
        employees = cursor.fetchall()
        
        self.employee_combo.clear()
        for employee in employees:
            self.employee_combo.addItem(employee[1], employee[0])
    
    def load_salary_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM salaries WHERE id = ?', (self.salary_id,))
        salary = cursor.fetchone()
        
        if salary:
            self.load_employees()
            # Tìm index của employee trong combo
            employee_index = -1
            for i in range(self.employee_combo.count()):
                if self.employee_combo.itemData(i) == salary[1]:
                    employee_index = i
                    break
            if employee_index >= 0:
                self.employee_combo.setCurrentIndex(employee_index)
            
            self.month_input.setValue(salary[2])
            self.year_input.setValue(salary[3])
            self.base_salary_input.setValue(salary[4])
            self.bonus_input.setValue(salary[5])
            self.deductions_input.setValue(salary[6])
            self.status_combo.setCurrentIndex(1 if salary[8] == 'paid' else 0)
            self.calculate_total()
    
    def calculate_total(self):
        total = self.base_salary_input.value() + self.bonus_input.value() - self.deductions_input.value()
        self.total_label.setText(f"{total:,.0f} VND")
    
    def save_salary(self):
        employee_id = self.employee_combo.currentData()
        month = self.month_input.value()
        year = self.year_input.value()
        base_salary = self.base_salary_input.value()
        bonus = self.bonus_input.value()
        deductions = self.deductions_input.value()
        total_salary = base_salary + bonus - deductions
        status = 'paid' if self.status_combo.currentIndex() == 1 else 'pending'
        
        if not employee_id:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn nhân viên!')
            return
        
        cursor = self.db.conn.cursor()
        
        # Check if salary record already exists for this employee and period
        if not self.salary_id:
            cursor.execute('''
                SELECT id FROM salaries WHERE employee_id = ? AND month = ? AND year = ?
            ''', (employee_id, month, year))
            if cursor.fetchone():
                QMessageBox.warning(self, 'Lỗi', 'Đã tồn tại bảng lương cho nhân viên này trong tháng/năm!')
                return
        
        if self.salary_id:
            cursor.execute('''
                UPDATE salaries SET employee_id=?, month=?, year=?, base_salary=?, bonus=?, 
                deductions=?, total_salary=?, status=?
                WHERE id=?
            ''', (employee_id, month, year, base_salary, bonus, deductions, total_salary, status, self.salary_id))
        else:
            cursor.execute('''
                INSERT INTO salaries (employee_id, month, year, base_salary, bonus, deductions, total_salary, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, month, year, base_salary, bonus, deductions, total_salary, status))
        
        self.db.conn.commit()
        self.accept()
from PyQt6.QtWidgets import (QDialog, QFormLayout, QTextEdit, QDateEdit,
                             QComboBox, QPushButton, QMessageBox, QHBoxLayout,
                             QDoubleSpinBox)
from PyQt6.QtCore import QDate

class EditRepairDialog(QDialog):
    def __init__(self, db, repair_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.repair_id = repair_id
        self.setWindowTitle(f'Sửa đơn sửa chữa #{repair_id}')
        self.setMinimumWidth(420)

        self.init_ui()  
        self.load_data()  

    def init_ui(self):
        self.layout = QFormLayout(self)

        # Dự kiến hoàn thành
        self.estimated_completion_input = QDateEdit()
        self.estimated_completion_input.setCalendarPopup(True)
        self.estimated_completion_input.setDisplayFormat('dd/MM/yyyy')
        self.layout.addRow('Dự kiến hoàn thành:', self.estimated_completion_input)

        # Chi phí
        self.actual_cost_input = QDoubleSpinBox()
        self.actual_cost_input.setMaximum(999999999)
        self.actual_cost_input.setPrefix('VND ')
        self.actual_cost_input.setDecimals(0)
        self.actual_cost_input.setSingleStep(1000)
        self.layout.addRow('Chi phí:', self.actual_cost_input)

        self.actual_cost_input.setStyleSheet("""
        QDoubleSpinBox:disabled {
        background-color: #333;
        color: #aaa;
        border: 1px solid #555;
    }
""")

        # Trạng thái
        self.status_combo = QComboBox()
        self.status_map = {
            'Chờ xử lý': 'Chờ xử lý',
            'Hoàn thành': 'Hoàn thành',
            'Đã hủy': 'Đã hủy'
        }
        for label in self.status_map.keys():
            self.status_combo.addItem(label)
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        self.layout.addRow('Trạng thái:', self.status_combo)

        # Nút
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addRow(btn_layout)

        # Style cho trạng thái bị khóa
        self.status_combo.setStyleSheet("""
            QComboBox:disabled {
                background-color: #333;
                color: #aaa;
                border: 1px solid #555;
            }
        """)


    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT issue_description, actual_cost, estimated_completion, status
            FROM repair_orders
            WHERE id = ?
        ''', (self.repair_id,))
        row = cursor.fetchone()
        if not row:
            QMessageBox.warning(self, 'Lỗi', 'Không tìm thấy đơn sửa chữa.')
            self.reject()
            return

        issue_desc, actual_cost, estimated_completion, status = row

        # Điền dữ liệu
        self.actual_cost_input.setValue(float(actual_cost or 0.0))

        # Ngày
        if estimated_completion:
            d = QDate.fromString(estimated_completion, 'yyyy-MM-dd')
            if d.isValid():
                self.estimated_completion_input.setDate(d)
            else:
                self.estimated_completion_input.setDate(QDate.currentDate())
        else:
            self.estimated_completion_input.setDate(QDate.currentDate())

        # Trạng thái
        rev = {v: k for k, v in self.status_map.items()}
        label = rev.get(status, 'Chờ xử lý')
        idx = self.status_combo.findText(label)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        # KHÓA TRẠNG THÁI + NGÀY NẾU ĐÃ HOÀN THÀNH HOẶC HỦY
        if status in ('Hoàn thành', 'Đã hủy'):
            self.status_combo.setEnabled(False)
            self.estimated_completion_input.setEnabled(False) 

            if status == 'Hoàn thành':
                self.actual_cost_input.setEnabled(True)
            else:  # Đã hủy
                self.actual_cost_input.setEnabled(False)
                self.actual_cost_input.setValue(0.0)
        else:
            self.status_combo.setEnabled(True)
            self.estimated_completion_input.setEnabled(True)  
            self.actual_cost_input.setEnabled(False)

        self.estimated_completion_input.setStyleSheet("""
            QDateEdit:disabled {
                background-color: #333;
                color: #aaa;
                border: 1px solid #555;
            }
        """)

    def on_status_changed(self, text):
        if not self.status_combo.isEnabled():
            return

        key = self.status_map.get(text, 'Chờ xử lý')
        if key == 'Hoàn thành':
            self.actual_cost_input.setEnabled(True)
        else:
            self.actual_cost_input.setEnabled(False)
            self.actual_cost_input.setValue(0.0)

    def save(self):
        estimated_completion = self.estimated_completion_input.date().toString('yyyy-MM-dd')
        status = self.status_map.get(self.status_combo.currentText(), 'Chờ xử lý')
        actual_cost = float(self.actual_cost_input.value()) if status == 'Hoàn thành' else 0.0

        cursor = self.db.conn.cursor()
        cursor.execute('''
    UPDATE repair_orders
    SET actual_cost = ?, estimated_completion = ?, status = ?
    WHERE id = ?
''', (actual_cost, estimated_completion, status, self.repair_id))
        self.db.conn.commit()
        QMessageBox.information(self, 'Thành công', 'Cập nhật đơn sửa chữa thành công.')
        self.accept()
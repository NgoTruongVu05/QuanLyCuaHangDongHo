from PyQt6.QtWidgets import (QDialog, QFormLayout, QTextEdit, QDateEdit,
                             QComboBox, QPushButton, QMessageBox, QHBoxLayout,
                             QDoubleSpinBox, QLabel)
from PyQt6.QtCore import QDate

class EditRepairDialog(QDialog):
    def __init__(self, db, repair_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.repair_id = repair_id
        self.created_date = None  
        self.setWindowTitle(f'Sửa đơn sửa chữa #{repair_id}')
        self.setMinimumWidth(420)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.layout = QFormLayout(self)

        # Hiển thị ngày tạo (chỉ đọc)
        self.created_date_label = QLabel("Chưa tải")
        self.created_date_label.setStyleSheet("color: #888; font-style: italic;")
        self.layout.addRow('Ngày tạo đơn:', self.created_date_label)

        # Dự kiến hoàn thành
        self.estimated_completion_input = QDateEdit()
        self.estimated_completion_input.setCalendarPopup(True)
        self.estimated_completion_input.setDisplayFormat('dd/MM/yyyy')
        self.estimated_completion_input.dateChanged.connect(self.validate_estimated_date)
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

        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addRow(btn_layout)

        self.status_combo.setStyleSheet("""
            QComboBox:disabled {
                background-color: #333;
                color: #aaa;
                border: 1px solid #555;
            }
        """)
        self.estimated_completion_input.setStyleSheet("""
            QDateEdit:disabled {
                background-color: #333;
                color: #aaa;
                border: 1px solid #555;
            }
        """)

    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT created_date, estimated_completion, actual_cost, status
            FROM repair_orders
            WHERE id = ?
        ''', (self.repair_id,))
        row = cursor.fetchone()
        if not row:
            QMessageBox.warning(self, 'Lỗi', 'Không tìm thấy đơn sửa chữa.')
            self.reject()
            return

        created_str, estimated_str, actual_cost, status = row

        # Lưu và hiển thị ngày tạo đơn
        self.created_date = QDate.fromString(created_str.split()[0], 'yyyy-MM-dd')
        if not self.created_date.isValid():
            self.created_date = QDate.currentDate()
        self.created_date_label.setText(self.created_date.toString('dd/MM/yyyy'))

        # Đặt ngày dự kiến (nếu có)
        if estimated_str:
            d = QDate.fromString(estimated_str.split()[0], 'yyyy-MM-dd')
            if d.isValid() and d >= self.created_date:
                self.estimated_completion_input.setDate(d)
            else:
                self.estimated_completion_input.setDate(self.created_date)
        else:
            self.estimated_completion_input.setDate(self.created_date)

        # không cho chọn ngày nhỏ hơn ngày tạo
        self.estimated_completion_input.setMinimumDate(self.created_date)

        # Chi phí
        self.actual_cost_input.setValue(float(actual_cost or 0.0))

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
            else:
                self.actual_cost_input.setEnabled(False)
                self.actual_cost_input.setValue(0.0)
        else:
            self.status_combo.setEnabled(True)
            self.estimated_completion_input.setEnabled(True)
            self.actual_cost_input.setEnabled(False)

        self.validate_estimated_date()

    def validate_estimated_date(self):
        """Không cho chọn ngày dự kiến < ngày tạo đơn"""
        if not self.created_date:
            return

        selected = self.estimated_completion_input.date()
        if selected < self.created_date:
            QMessageBox.warning(
                self,
                'Lỗi ngày',
                f'Dự kiến hoàn thành không được sớm hơn ngày tạo đơn:\n'
                f'→ <b>{self.created_date.toString("dd/MM/yyyy")}</b>'
            )
            self.estimated_completion_input.setDate(self.created_date)

        self.estimated_completion_input.setMinimumDate(self.created_date)

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
        selected = self.estimated_completion_input.date()
        if selected < self.created_date:
            QMessageBox.critical(self, 'Lỗi', 'Ngày dự kiến không hợp lệ!')
            return

        estimated_completion = selected.toString('yyyy-MM-dd')
        status = self.status_map.get(self.status_combo.currentText(), 'Chờ xử lý')
        actual_cost = float(self.actual_cost_input.value()) if status == 'Hoàn thành' else 0.0

        cursor = self.db.conn.cursor()
        try:
            cursor.execute('''
                UPDATE repair_orders
                SET actual_cost = ?, estimated_completion = ?, status = ?
                WHERE id = ?
            ''', (actual_cost, estimated_completion, status, self.repair_id))
            self.db.conn.commit()
            QMessageBox.information(self, 'Thành công', 'Cập nhật thành công.')
            self.accept()
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, 'Lỗi', f'Không thể lưu: {e}')
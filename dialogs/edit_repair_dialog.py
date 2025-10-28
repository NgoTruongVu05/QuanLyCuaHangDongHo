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

        self.watch_desc_input = QTextEdit()
        self.watch_desc_input.setMaximumHeight(80)
        self.layout.addRow('Mô tả đồng hồ:', self.watch_desc_input)

        self.issue_desc_input = QTextEdit()
        self.issue_desc_input.setMaximumHeight(80)
        self.layout.addRow('Mô tả lỗi:', self.issue_desc_input)

        self.estimated_completion_input = QDateEdit()
        self.estimated_completion_input.setCalendarPopup(True)
        self.layout.addRow('Dự kiến hoàn thành:', self.estimated_completion_input)

        # Chi phí thực tế - chỉ editable khi chọn "Hoàn thành"
        self.actual_cost_input = QDoubleSpinBox()
        self.actual_cost_input.setMaximum(999999999)
        self.actual_cost_input.setPrefix('VND ')
        self.actual_cost_input.setDecimals(0)
        self.actual_cost_input.setSingleStep(1000)
        self.layout.addRow('Chi phí:', self.actual_cost_input)

        # Chỉ cho phép 3 trạng thái: Chờ xử lý, Hoàn thành, Đã hủy
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

    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT watch_description, issue_description, actual_cost, estimated_completion, status
            FROM repair_orders
            WHERE id = ?
        ''', (self.repair_id,))
        row = cursor.fetchone()
        if not row:
            QMessageBox.warning(self, 'Lỗi', 'Không tìm thấy đơn sửa chữa.')
            self.reject()
            return

        watch_desc, issue_desc, actual_cost, estimated_completion, status = row
        self.watch_desc_input.setPlainText(watch_desc or '')
        self.issue_desc_input.setPlainText(issue_desc or '')
        self.actual_cost_input.setValue(float(actual_cost or 0.0))

        if estimated_completion:
            d = QDate.fromString(estimated_completion, 'yyyy-MM-dd')
            if d.isValid():
                self.estimated_completion_input.setDate(d)
            else:
                self.estimated_completion_input.setDate(QDate.currentDate())
        else:
            self.estimated_completion_input.setDate(QDate.currentDate())

        # Set status combo by reverse lookup
        rev = {v: k for k, v in self.status_map.items()}
        label = rev.get(status, 'Chờ xử lý')
        idx = self.status_combo.findText(label)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        # Enable/disable cost input according to status
        self.actual_cost_input.setEnabled(status == 'Hoàn thành')

    def on_status_changed(self, text):
        """Khi đổi trạng thái: nếu chọn Hoàn thành -> bật nhập chi phí,
           nếu chọn Chờ xử lý hoặc Đã hủy -> khoá và đặt chi phí = 0."""
        key = self.status_map.get(text, 'Chờ xử lý')
        if key == 'Hoàn thành':
            self.actual_cost_input.setEnabled(True)
        else:
            # khoá và reset giá trị
            self.actual_cost_input.setEnabled(False)
            self.actual_cost_input.setValue(0.0)

    def save(self):
        watch_desc = self.watch_desc_input.toPlainText().strip()
        issue_desc = self.issue_desc_input.toPlainText().strip()
        estimated_completion = self.estimated_completion_input.date().toString('yyyy-MM-dd')

        status = self.status_map.get(self.status_combo.currentText(), 'Chờ xử lý')
        # chỉ lấy chi phí khi trạng thái là completed
        actual_cost = float(self.actual_cost_input.value()) if status == 'Hoàn thành' else 0.0

        if not watch_desc or not issue_desc:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin.')
            return

        cursor = self.db.conn.cursor()
        cursor.execute('''
            UPDATE repair_orders
            SET watch_description = ?, issue_description = ?, actual_cost = ?, estimated_completion = ?, status = ?
            WHERE id = ?
        ''', (watch_desc, issue_desc, actual_cost, estimated_completion, status, self.repair_id))
        self.db.conn.commit()
        QMessageBox.information(self, 'Thành công', 'Cập nhật đơn sửa chữa thành công.')
        self.accept()
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QHeaderView, QDialog, QFormLayout, QLineEdit,
                            QFileDialog, QProgressDialog)
from PyQt6.QtCore import Qt
import csv

class BrandDialog(QDialog):
    def __init__(self, db, brand_id=None):
        super().__init__()
        self.db = db
        self.brand_id = brand_id
        self.init_ui()
        if brand_id:
            self.load_brand_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa thương hiệu')
        self.setFixedSize(400, 200)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        layout.addRow('Tên thương hiệu:', self.name_input)
        
        self.country_input = QLineEdit()
        layout.addRow('Quốc gia:', self.country_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_brand)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def load_brand_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name, country FROM brands WHERE id = ?', (self.brand_id,))
        brand = cursor.fetchone()
        
        if brand:
            self.name_input.setText(brand[0])
            self.country_input.setText(brand[1] if brand[1] else '')
    
    def save_brand(self):
        name = self.name_input.text().strip()
        country = self.country_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập tên thương hiệu!')
            return
        
        cursor = self.db.conn.cursor()
        
        if self.brand_id:
            cursor.execute('UPDATE brands SET name=?, country=? WHERE id=?', 
                         (name, country, self.brand_id))
        else:
            cursor.execute('INSERT INTO brands (name, country) VALUES (?, ?)', 
                         (name, country))
        
        self.db.conn.commit()
        self.accept()

class BrandManagementTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        if self.user_role == 1:  # Chỉ admin mới được thêm thương hiệu
            add_btn = QPushButton('Thêm thương hiệu')
            add_btn.setStyleSheet('''
                QPushButton {
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #8E44AD;
                }
            ''')
            add_btn.clicked.connect(self.add_brand)
            controls_layout.addWidget(add_btn)

            import_csv_btn = QPushButton('Nhập CSV')
            import_csv_btn.setStyleSheet('''
                QPushButton {
                    background-color: #9B59B6;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #8E44AD;
                }
            ''')
            import_csv_btn.clicked.connect(self.import_csv)
            controls_layout.addWidget(import_csv_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # ID, Tên, Quốc gia, Hành động
        self.table.setHorizontalHeaderLabels(['ID', 'Tên thương hiệu', 'Quốc gia', 'Hành động'])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Quốc gia
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Hành động
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def load_data(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM brands ORDER BY id')
        brands = cursor.fetchall()
        
        self.table.setRowCount(len(brands))
        for row, brand in enumerate(brands):
            # ID, Tên, Quốc gia
            for col in range(3):
                self.table.setItem(row, col, QTableWidgetItem(str(brand[col] or '')))
            
            # Nút hành động
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            if self.user_role == 1:  # Chỉ admin mới có nút sửa/xóa
                edit_btn = QPushButton('Sửa')
                edit_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 3px 8px;
                        font-size: 11px;
                        margin-right: 2px;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                ''')
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_brand_row(r))
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
                        margin: 0 3px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_brand_row(r))
                action_layout.addWidget(delete_btn)
            
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 3, action_widget)
            self.table.resizeRowsToContents()
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def add_brand(self):
        dialog = BrandDialog(self.db)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm thương hiệu mới!')
    
    def edit_brand_row(self, row):
        brand_id = int(self.table.item(row, 0).text())
        dialog = BrandDialog(self.db, brand_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật thương hiệu!')
    
    def delete_brand_row(self, row):
        brand_id = int(self.table.item(row, 0).text())
        brand_name = self.table.item(row, 1).text()
        
        # Kiểm tra xem thương hiệu có sản phẩm không
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products WHERE brand_id = ?', (brand_id,))
        product_count = cursor.fetchone()[0]
        
        if product_count > 0:
            QMessageBox.warning(self, 'Lỗi', 
                              f'Không thể xóa thương hiệu "{brand_name}" vì có {product_count} sản phẩm đang sử dụng!')
            return
        
        reply = QMessageBox.question(self, 'Xác nhận',
                                   f'Bạn có chắc muốn xóa thương hiệu "{brand_name}"?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            cursor.execute('DELETE FROM brands WHERE id = ?', (brand_id,))
            self.db.conn.commit()
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã xóa thương hiệu!')

    def import_csv(self):
        """
        Import brands from CSV file.
        Expected CSV headers: name, country
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file CSV", "", "CSV files (*.csv);;All files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            if not rows:
                QMessageBox.warning(self, 'Lỗi', 'File CSV trống hoặc không có dữ liệu.')
                return

            # Validate headers
            required_headers = ['name']
            if not all(header in reader.fieldnames for header in required_headers):
                QMessageBox.warning(self, 'Lỗi', f'File CSV thiếu các cột bắt buộc: {", ".join(required_headers)}')
                return

            # Validate all rows first before importing
            errors = []
            cursor = self.db.conn.cursor()
            for i, row in enumerate(rows):
                try:
                    # Parse data for validation
                    name = row.get('name', '').strip()
                    if not name:
                        errors.append(f"Dòng {i+2}: Tên thương hiệu không được để trống")
                        continue

                except Exception as e:
                    errors.append(f"Dòng {i+2}: {str(e)}")

            # If any errors found, block import
            if errors:
                error_msg = '\n'.join(errors[:10])  # Show first 10 errors
                if len(errors) > 10:
                    error_msg += f'\n... và {len(errors) - 10} lỗi khác'
                QMessageBox.warning(self, 'Lỗi nhập dữ liệu', f'Không thể nhập dữ liệu do có lỗi:\n{error_msg}')
                return

            # If validation passed, proceed with import
            # Show progress dialog
            progress = QProgressDialog("Đang nhập dữ liệu...", "Hủy", 0, len(rows), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            cursor = self.db.conn.cursor()
            imported_count = 0
            skipped_count = 0

            for i, row in enumerate(rows):
                if progress.wasCanceled():
                    break

                progress.setValue(i)

                try:
                    # Parse data
                    name = row.get('name', '').strip()
                    country = row.get('country', '').strip()

                    # Check if brand already exists
                    cursor.execute('SELECT id FROM brands WHERE name = ?', (name,))
                    if cursor.fetchone():
                        skipped_count += 1
                        continue

                    # Insert brand
                    cursor.execute('INSERT INTO brands (name, country) VALUES (?, ?)', (name, country))

                    imported_count += 1

                except Exception as e:
                    # This shouldn't happen since we validated, but just in case
                    QMessageBox.warning(self, 'Lỗi', f'Lỗi không mong muốn ở dòng {i+2}: {str(e)}')
                    return

            self.db.conn.commit()
            progress.setValue(len(rows))

            # Show success
            self.load_data()
            if skipped_count > 0:
                QMessageBox.information(self, 'Thành công',
                                      f'Đã nhập thành công {imported_count} thương hiệu. Đã bỏ qua {skipped_count} thương hiệu đã tồn tại.')
            else:
                QMessageBox.information(self, 'Thành công',
                                      f'Đã nhập thành công {imported_count} thương hiệu.')

        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể đọc file CSV: {str(e)}')

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QGridLayout, QComboBox, QSpinBox,
                             QPushButton, QToolTip, QFrame)
from PyQt6.QtCore import QDate
# backend qtagg tương thích tốt với PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as mtick
import numpy as np
import logging

class StatisticsTab(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        # default mode là "revenue"
        # Các mode: revenue, customer, top_types
        self.current_mode = "revenue"
        self.init_ui()
        self.switch_statistics(self.current_mode)
        self.load_statistics()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12,12,12,12)
        layout.setSpacing(12)

        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        filter_layout.addWidget(QLabel('Tháng:'))
        self.month_filter = QComboBox()
        self.month_filter.addItems(['Tất cả'] + [str(i) for i in range(1,13)])
        current_month = str(QDate.currentDate().month())
        self.month_filter.setCurrentText(current_month)
        self.month_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.month_filter)

        filter_layout.addWidget(QLabel('Năm:'))
        self.year_filter = QSpinBox()
        self.year_filter.setRange(2000, 2030)
        self.year_filter.setValue(QDate.currentDate().year())
        self.year_filter.valueChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.year_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Buttons: Doanh thu / Khách hàng / Loại đồng hồ (NO refresh button)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        self.revenue_btn = QPushButton('Doanh thu')
        self.revenue_btn.setFixedHeight(36)
        self.revenue_btn.clicked.connect(lambda: self.switch_statistics("revenue"))
        self.customer_btn = QPushButton('Khách hàng')
        self.customer_btn.setFixedHeight(36)
        self.customer_btn.clicked.connect(lambda: self.switch_statistics("customer"))
        self.top_types_btn = QPushButton('Sản phẩm bán chạy')
        self.top_types_btn.setFixedHeight(36)
        self.top_types_btn.clicked.connect(lambda: self.switch_statistics("top_types"))

        for b in (self.revenue_btn, self.customer_btn, self.top_types_btn):
            b.setCursor(b.cursor())
            button_layout.addWidget(b)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Grid thông tin tóm tắt — tách sales và repair thành 2 cột để rõ ràng hơn
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # Doanh thu bán hàng (left)
        self.sales_group = QGroupBox('Doanh thu - Bán hàng')
        sl = QVBoxLayout()
        self.total_revenue_label = QLabel('Tổng doanh thu bán hàng: 0 VND')
        self.total_revenue_label.setStyleSheet("color: white;")
        self.total_sales_label = QLabel('Tổng số hóa đơn bán hàng: 0')
        self.avg_sale_label = QLabel('Giá trị trung bình mỗi hóa đơn: 0 VND')
        for w in (self.total_revenue_label, self.total_sales_label, self.avg_sale_label):
            sl.addWidget(w)
        self.sales_group.setLayout(sl)
        grid_layout.addWidget(self.sales_group, 0, 0)

        # Doanh thu sửa chữa (right)
        self.repair_group = QGroupBox('Doanh thu - Sửa chữa')
        rl = QVBoxLayout()
        self.total_repair_revenue_label = QLabel('Tổng doanh thu sửa chữa: 0 VND')
        self.total_repair_revenue_label.setStyleSheet("color: white;")
        self.total_repairs_label = QLabel('Tổng số đơn sửa chữa: 0')
        self.completed_repairs_label = QLabel('Đơn đã hoàn thành: 0')
        for w in (self.total_repair_revenue_label, self.total_repairs_label, self.completed_repairs_label):
            rl.addWidget(w)
        self.repair_group.setLayout(rl)
        grid_layout.addWidget(self.repair_group, 0, 1)

        # Customer (trải rộng 2 cột)
        self.customer_group = QGroupBox('Thống kê khách hàng')
        cl = QVBoxLayout()
        self.total_customers_label = QLabel('Tổng số khách hàng: 0')
        self.repeat_customers_label = QLabel('Khách hàng thân thiết: 0')
        self.new_customers_month_label = QLabel('Khách hàng mới (tháng): 0')
        cl.addWidget(self.total_customers_label); cl.addWidget(self.repeat_customers_label); cl.addWidget(self.new_customers_month_label)
        self.customer_group.setLayout(cl); grid_layout.addWidget(self.customer_group, 1, 0, 1, 2)

        # Add subtle separators for visual clarity
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addLayout(grid_layout)
        layout.addWidget(sep)

        # Chart area
        self.chart_group = QGroupBox('Biểu đồ thống kê')
        chart_layout = QVBoxLayout()
        self.figure = Figure(figsize=(9,4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        self.chart_group.setLayout(chart_layout)

        layout.addWidget(self.chart_group)
        self.setLayout(layout)

        # Styles: cải tiến để thân thiện hơn với màu sắc tương phản và bo góc tròn hơn, với nền #353535
        self.active_style = '''
            QPushButton { background-color: #2C3E50; color: white; border: 2px solid #F39C12; border-radius: 12px; padding: 8px 14px; font-weight: 600; }
        '''
        self.inactive_style = '''
            QPushButton { background-color: #27AE60; color: white; border: 1px solid #777777; border-radius: 12px; padding: 8px 14px; }
            QPushButton:hover { background-color: #229954; }
        '''

        # Tooltips nhẹ
        QToolTip.setFont(self.font())
        self.revenue_btn.setToolTip('Xem doanh thu theo năm/tháng')
        self.customer_btn.setToolTip('Thống kê khách hàng mới / thân thiết')
        self.top_types_btn.setToolTip('Sản phẩm bán chạy nhất (Top)')

    def on_filter_changed(self, *_):
        self.load_statistics()

    def load_statistics(self):
        month = self.month_filter.currentText()
        year = self.year_filter.value()
        cursor = self.db.conn.cursor()
        try:
            # --- Doanh thu bán hàng ---
            if month == 'Tất cả':
                cursor.execute('SELECT IFNULL(SUM(total_amount),0), COUNT(*) FROM invoices WHERE strftime("%Y", created_date) = ?', (str(year),))
            else:
                cursor.execute('SELECT IFNULL(SUM(total_amount),0), COUNT(*) FROM invoices WHERE strftime("%Y", created_date) = ? AND strftime("%m", created_date) = ?', (str(year), month.zfill(2)))
            s_sum, s_count = cursor.fetchone() or (0,0)
            self.total_revenue_label.setText(f'Tổng doanh thu bán hàng: {s_sum:,.0f} VND')
            self.total_sales_label.setText(f'Tổng số hóa đơn bán hàng: {s_count}')
            self.avg_sale_label.setText(f'Giá trị trung bình mỗi hóa đơn: { (s_sum/(s_count or 1)) :,.0f} VND')

            # --- Doanh thu sửa chữa ---
            if month == 'Tất cả':
                cursor.execute("SELECT IFNULL(SUM(estimated_cost),0), COUNT(*), SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) FROM repair_orders WHERE strftime('%Y', created_date) = ?", (str(year),))
            else:
                cursor.execute("SELECT IFNULL(SUM(estimated_cost),0), COUNT(*), SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) FROM repair_orders WHERE strftime('%Y', created_date) = ? AND strftime('%m', created_date) = ?", (str(year), month.zfill(2)))
            r_sum, r_count, r_completed = cursor.fetchone() or (0,0,0)
            self.total_repair_revenue_label.setText(f'Tổng doanh thu sửa chữa: {r_sum:,.0f} VND')
            self.total_repairs_label.setText(f'Tổng số đơn sửa chữa: {r_count}')
            self.completed_repairs_label.setText(f'Đơn đã hoàn thành: {r_completed}')

            # --- Customer ---
            cursor.execute('SELECT COUNT(*) FROM customers')
            total_customers = cursor.fetchone()[0] or 0
            cursor.execute('''
                SELECT COUNT(*) FROM (
                    SELECT customer_id FROM invoices WHERE customer_id IS NOT NULL
                    GROUP BY customer_id HAVING COUNT(*) > 1
                )
            ''')
            repeat_customers = cursor.fetchone()[0] or 0

            if month == 'Tất cả':
                cursor.execute('''
                    SELECT COUNT(*) FROM (
                        SELECT customer_id, MIN(created_date) as first_date FROM invoices
                        WHERE customer_id IS NOT NULL
                        GROUP BY customer_id
                        HAVING strftime('%Y', first_date) = ?
                    )
                ''', (str(year),))
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM (
                        SELECT customer_id, MIN(created_date) as first_date FROM invoices
                        WHERE customer_id IS NOT NULL
                        GROUP BY customer_id
                        HAVING strftime('%Y', first_date) = ? AND strftime('%m', first_date) = ?
                    )
                ''', (str(year), month.zfill(2)))
            new_customers = cursor.fetchone()[0] or 0

            self.total_customers_label.setText(f'Tổng số khách hàng: {total_customers}')
            self.repeat_customers_label.setText(f'Khách hàng thân thiết: {repeat_customers}')
            self.new_customers_month_label.setText(f'Khách hàng mới (tháng): {new_customers}')

        except Exception as e:
            logging.error('Lỗi load_statistics: %s', e)
        finally:
            try:
                cursor.close()
            except: pass

        # cập nhật biểu đồ theo mode
        self.update_chart()

    def switch_statistics(self, mode):
        self.current_mode = mode
        if mode == "revenue":
            self.sales_group.show(); self.repair_group.show(); self.customer_group.hide()
        elif mode == "customer":
            self.sales_group.hide(); self.repair_group.hide(); self.customer_group.show()
        elif mode == "top_types":
            self.sales_group.hide(); self.repair_group.hide(); self.customer_group.hide()
        self.update_button_styles()
        self.update_chart()

    def update_button_styles(self):
        for name, btn in (("revenue", self.revenue_btn), ("customer", self.customer_btn), ("top_types", self.top_types_btn)):
            btn.setStyleSheet(self.active_style if self.current_mode == name else self.inactive_style)

    def update_chart(self):
        # vẽ lại biểu đồ theo self.current_mode + filter month/year
        self.figure.clear()
        self.figure.patch.set_facecolor('#353535')
        month = self.month_filter.currentText()
        year = self.year_filter.value()
        cursor = self.db.conn.cursor()

        try:
            if self.current_mode == "revenue":
                # Vẽ doanh thu bán hàng và doanh thu sửa chữa (biểu đồ đường)
                if month == 'Tất cả':
                    months = [f'{i:02d}' for i in range(1,13)]
                    xlbl = [f'T{i}' for i in range(1,13)]
                    sales_data = []
                    repair_data = []
                    for m in months:
                        cursor.execute('SELECT IFNULL(SUM(total_amount),0) FROM invoices WHERE strftime("%m", created_date)=? AND strftime("%Y", created_date)=?', (m, str(year)))
                        s_sum = cursor.fetchone()[0] or 0
                        cursor.execute("SELECT IFNULL(SUM(estimated_cost),0) FROM repair_orders WHERE strftime('%m', created_date)=? AND strftime('%Y', created_date)=?", (m, str(year)))
                        r_sum = cursor.fetchone()[0] or 0
                        sales_data.append(s_sum); repair_data.append(r_sum)
                    ax = self.figure.add_subplot(111); ax.set_facecolor('#353535')
                    x = np.arange(len(xlbl))
                    ax.plot(x, sales_data, marker='o', label='Doanh thu bán hàng', color='#3498DB', linewidth=2)
                    ax.plot(x, repair_data, marker='s', label='Doanh thu sửa chữa', color='#E74C3C', linewidth=2)
                    ax.set_xticks(x); ax.set_xticklabels(xlbl, color='white')
                    ax.set_ylabel('Doanh thu (VND)', color='white'); ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
                    ax.tick_params(axis='y', colors='white', labelcolor='white')
                    ax.grid(True, alpha=0.3, color='white')
                    ax.set_title(f'Doanh thu năm {year}', color='white', fontsize=12, fontweight='bold')
                    legend = ax.legend(frameon=True); legend.get_frame().set_facecolor('#2C3E50'); legend.get_frame().set_edgecolor('white')
                    for t in legend.get_texts(): t.set_color('white')
                else:
                    m = month.zfill(2)
                    cursor.execute('SELECT strftime("%d", created_date) as d, IFNULL(SUM(total_amount),0) FROM invoices WHERE strftime("%m", created_date)=? AND strftime("%Y", created_date)=? GROUP BY d ORDER BY d', (m, str(year)))
                    rows_s = cursor.fetchall()
                    days = [r[0] for r in rows_s] if rows_s else []
                    sums = [r[1] for r in rows_s] if rows_s else []
                    cursor.execute('SELECT strftime("%d", created_date) as d, IFNULL(SUM(estimated_cost),0) FROM repair_orders WHERE strftime("%m", created_date)=? AND strftime("%Y", created_date)=? GROUP BY d ORDER BY d', (m, str(year)))
                    rows_r = cursor.fetchall()
                    days_r = [r[0] for r in rows_r] if rows_r else []
                    sums_r = [r[1] for r in rows_r] if rows_r else []
                    # align by day: tạo một map
                    all_days = sorted(list(set(days + days_r)), key=lambda x: int(x))
                    s_map = {d:0 for d in all_days}; r_map = {d:0 for d in all_days}
                    for d,v in zip(days, sums): s_map[d]=v
                    for d,v in zip(days_r, sums_r): r_map[d]=v
                    ax = self.figure.add_subplot(111); ax.set_facecolor('#353535')
                    x = np.arange(len(all_days))
                    ax.plot(x, [s_map[d] for d in all_days], marker='o', label='Doanh thu bán hàng', color='#3498DB', linewidth=2)
                    ax.plot(x, [r_map[d] for d in all_days], marker='s', label='Doanh thu sửa chữa', color='#E74C3C', linewidth=2)
                    ax.set_xticks(x); ax.set_xticklabels(all_days, rotation=45, color='white')
                    ax.set_ylabel('Doanh thu (VND)', color='white'); ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
                    ax.tick_params(axis='y', colors='white', labelcolor='white')
                    ax.grid(True, alpha=0.3, color='white')
                    ax.set_title(f'Doanh thu tháng {int(month)}/{year}', color='white', fontsize=12, fontweight='bold')
                    legend = ax.legend(frameon=True); legend.get_frame().set_facecolor('#2C3E50'); legend.get_frame().set_edgecolor('white')
                    for t in legend.get_texts(): t.set_color('white')

            elif self.current_mode == "customer":
                if month == 'Tất cả':
                    months = [f'{i:02d}' for i in range(1,13)]
                    new_counts = []
                    repeat_counts = []
                    for m in months:
                        cursor.execute('''
                            SELECT COUNT(*) FROM (
                                SELECT customer_id, MIN(created_date) as first_date FROM invoices
                                WHERE customer_id IS NOT NULL
                                GROUP BY customer_id
                                HAVING strftime('%Y', first_date)=? AND strftime('%m', first_date)=?
                            )
                        ''', (str(year), m))
                        new_counts.append(cursor.fetchone()[0] or 0)
                        cursor.execute('SELECT COUNT(DISTINCT customer_id) FROM invoices WHERE strftime("%m", created_date)=? AND strftime("%Y", created_date)=? GROUP BY customer_id HAVING COUNT(*)>1', (m, str(year)))
                        rows = cursor.fetchall()
                        repeat_counts.append(len(rows))
                    ax = self.figure.add_subplot(111); ax.set_facecolor('#353535')
                    x = np.arange(len(months))
                    ax.plot(x, new_counts, marker='o', label='Khách mới', color='#3498DB', linewidth=2)
                    ax.plot(x, repeat_counts, marker='s', label='Khách thân thiết', color='#E74C3C', linewidth=2)
                    ax.set_xticks(x); ax.set_xticklabels([f'T{i}' for i in range(1,13)], color='white')
                    ax.set_ylabel('Số lượng khách hàng', color='white')
                    ax.set_title(f'Khách hàng năm {year}', color='white', fontsize=12)
                    ax.legend(frameon=True); ax.grid(True, alpha=0.3, color='white')
                    for text in ax.get_legend().get_texts(): text.set_color('white')
                    ax.tick_params(axis='y', colors='white', labelcolor='white')
                    legend = ax.legend(frameon=True); legend.get_frame().set_facecolor('#2C3E50'); legend.get_frame().set_edgecolor('white')
                    for t in legend.get_texts(): t.set_color('white')
                else:
                    m = month.zfill(2)
                    # Query daily new customers
                    cursor.execute('''
                        SELECT strftime('%d', first_date) as d, COUNT(*) FROM (
                            SELECT customer_id, MIN(created_date) as first_date FROM invoices
                            WHERE customer_id IS NOT NULL
                            GROUP BY customer_id
                            HAVING strftime('%Y', first_date)=? AND strftime('%m', first_date)=?
                        ) GROUP BY d ORDER BY d
                    ''', (str(year), m))
                    new_rows = cursor.fetchall()
                    new_days = [r[0] for r in new_rows] if new_rows else []
                    new_counts = [r[1] for r in new_rows] if new_rows else []

                    # Query daily repeat customers
                    cursor.execute('''
                        SELECT strftime('%d', created_date) as d, COUNT(DISTINCT customer_id) FROM invoices
                        WHERE strftime('%Y', created_date)=? AND strftime('%m', created_date)=?
                        AND customer_id IN (
                            SELECT customer_id FROM invoices GROUP BY customer_id HAVING COUNT(*)>1
                        )
                        GROUP BY d ORDER BY d
                    ''', (str(year), m))
                    rep_rows = cursor.fetchall()
                    rep_days = [r[0] for r in rep_rows] if rep_rows else []
                    rep_counts = [r[1] for r in rep_rows] if rep_rows else []

                    # Align by day
                    all_days = sorted(list(set(new_days + rep_days)), key=lambda x: int(x))
                    new_map = {d: 0 for d in all_days}
                    rep_map = {d: 0 for d in all_days}
                    for d, v in zip(new_days, new_counts): new_map[d] = v
                    for d, v in zip(rep_days, rep_counts): rep_map[d] = v

                    ax = self.figure.add_subplot(111); ax.set_facecolor('#353535')
                    x = np.arange(len(all_days))
                    ax.plot(x, [new_map[d] for d in all_days], marker='o', label='Khách mới', color='#3498DB', linewidth=2)
                    ax.plot(x, [rep_map[d] for d in all_days], marker='s', label='Khách thân thiết', color='#E74C3C', linewidth=2)
                    ax.set_xticks(x); ax.set_xticklabels(all_days, rotation=45, color='white')
                    ax.set_ylabel('Số lượng khách hàng', color='white')
                    ax.set_title(f'Khách hàng tháng {int(month)}/{year}', color='white'); ax.tick_params(axis='y', colors='white', labelcolor='white')
                    ax.grid(True, alpha=0.3, color='white')
                    legend = ax.legend(frameon=True); legend.get_frame().set_facecolor('#2C3E50'); legend.get_frame().set_edgecolor('white')
                    for t in legend.get_texts(): t.set_color('white')

            elif self.current_mode == "top_types":
                # Thống kê sản phẩm bán chạy nhất
                try:
                    if month != 'Tất cả':
                        cursor.execute('''
                            SELECT p.name AS product, SUM(id.quantity) AS sold_qty
                            FROM invoice_details id
                            JOIN products p ON p.id = id.product_id
                            JOIN invoices inv ON inv.id = id.invoice_id
                            WHERE strftime('%Y', inv.created_date)=? AND strftime('%m', inv.created_date)=?
                            GROUP BY p.name ORDER BY sold_qty DESC LIMIT 15
                        ''', (str(year), month.zfill(2)))
                    else:
                        cursor.execute('''
                            SELECT p.name AS product, SUM(id.quantity) AS sold_qty
                            FROM invoice_details id
                            JOIN products p ON p.id = id.product_id
                            JOIN invoices inv ON inv.id = id.invoice_id
                            WHERE strftime('%Y', inv.created_date)=?
                            GROUP BY p.name ORDER BY sold_qty DESC LIMIT 15
                        ''', (str(year),))
                    rows = cursor.fetchall()

                    if rows:
                        products = [r[0] for r in rows]
                        qtys = [r[1] for r in rows]
                        ax = self.figure.add_subplot(111); ax.set_facecolor('#353535')
                        y_pos = np.arange(len(products))
                        # Sử dụng màu sắc khác nhau cho từng cột để dễ nhận diện
                        colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#27AE60', '#2980B9', '#8E44AD', '#D35400', '#C0392B', '#7D3C98']
                        bar_colors = [colors[i % len(colors)] for i in range(len(products))]
                        ax.barh(y_pos, qtys, color=bar_colors)
                        ax.set_yticks(y_pos); ax.set_yticklabels(products, color='white')
                        ax.invert_yaxis()
                        ax.set_xlabel('Số lượng bán', color='white')
                        ax.set_title(f'Top sản phẩm bán nhiều nhất {"tháng " + str(int(month)) + "/" + str(year) if month != "Tất cả" else "năm " + str(year)}', color='white')
                        ax.tick_params(axis='x', colors='white')
                    else:
                        ax = self.figure.add_subplot(111); ax.set_facecolor('#353535')
                        ax.text(0.5, 0.5, 'Không có dữ liệu bán hàng trong khoảng thời gian này', ha='center', va='center', color='white')
                except Exception as e:
                    logging.error('Lỗi truy vấn top_types: %s', e)
                    ax = self.figure.add_subplot(111); ax.set_facecolor('#353535')
                    ax.text(0.5, 0.5, 'Không thể truy vấn top sản phẩm với schema hiện tại', ha='center', va='center', color='white')

        except Exception as e:
            logging.error('Lỗi update_chart: %s', e)
        finally:
            try: cursor.close()
            except: pass

        try:
            self.figure.tight_layout()
        except:
            pass
        self.canvas.draw()

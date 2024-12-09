from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                           QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                           QDialog, QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox,
                           QFrame, QCompleter, QHeaderView, QGroupBox, QRadioButton,
                           QCheckBox)
from PyQt6.QtCore import Qt, QTimer, QRect, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor
from database_manager import DatabaseManager
from datetime import datetime
import json
import qrcode
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.platypus import Table, TableStyle, Spacer
from reportlab.lib import colors

class SalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_order = {
            'items': [],
            'customer': None,
            'total': 0,
            'discount': 0
        }
        self.setup_ui()
        self.load_products_data()

    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # تقليل الهوامش
        main_layout.setSpacing(10)  # تقليل المسافة بين العناصر

        # Top Section - Search and Customer Info
        top_section = QHBoxLayout()
        top_section.setSpacing(10)  # تقليل المسافة بين العناصر
        
        # Product Search
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 40, 65, 0.95);
                border-radius: 10px;
                border: 1px solid #c5a572;
            }
        """)
        search_layout = QVBoxLayout(search_frame)
        
        # Product Search
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("بحث عن منتج...")
        self.product_search.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: rgba(10, 17, 40, 0.95);
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        
        # Products Quick List
        self.products_list = QTableWidget()
        self.products_list.setColumnCount(5)
        self.products_list.setHorizontalHeaderLabels([
            "الكود", "المنتج", "سعر البيع", "سعر الجملة", "المخزون"
        ])
        self.products_list.setStyleSheet("""
            QTableWidget {
                background-color: rgba(10, 17, 40, 0.95);
                color: #c5a572;
                border: none;
            }
            QHeaderView::section {
                background-color: #0a1128;
                color: #c5a572;
                padding: 5px;
                border: 1px solid #c5a572;
            }
        """)
        self.products_list.itemDoubleClicked.connect(self.add_product_to_order)
        search_layout.addWidget(self.products_list)
        
        # Customer Section
        customer_frame = QFrame()
        customer_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 40, 65, 0.95);
                border-radius: 10px;
                border: 1px solid #c5a572;
            }
        """)
        customer_layout = QVBoxLayout(customer_frame)
        
        # Customer Search/Select
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("بحث عن عميل...")
        self.customer_search.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: rgba(10, 17, 40, 0.95);
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        customer_layout.addWidget(self.customer_search)
        
        # Customer Info Display
        self.customer_info = QLabel("لم يتم اختيار عميل")
        self.customer_info.setStyleSheet("color: #c5a572; font-size: 14px;")
        customer_layout.addWidget(self.customer_info)
        
        # Add Customer Button
        add_customer_btn = QPushButton("إضافة عميل جديد")
        add_customer_btn.setStyleSheet(self.get_button_style())
        add_customer_btn.clicked.connect(self.add_new_customer)
        customer_layout.addWidget(add_customer_btn)
        
        top_section.addWidget(search_frame, 2)
        top_section.addWidget(customer_frame, 1)
        main_layout.addLayout(top_section)

        # Current Order Section
        order_frame = QFrame()
        order_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 40, 65, 0.95);
                border-radius: 10px;
                border: 1px solid #c5a572;
            }
        """)
        order_layout = QVBoxLayout(order_frame)
        
        # Order Table
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(7)
        self.order_table.setHorizontalHeaderLabels([
            "الكود", "المنتج", "الكمية", "السعر", "الإجمالي", "نوع السعر", "حذف"
        ])
        self.order_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(10, 17, 40, 0.95);
                color: #c5a572;
                border: none;
            }
            QHeaderView::section {
                background-color: #0a1128;
                color: #c5a572;
                padding: 5px;
                border: 1px solid #c5a572;
            }
        """)
        order_layout.addWidget(self.order_table)
        
        # Order Summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 40, 65, 0.95);
                border-radius: 10px;
                border: 1px solid #c5a572;
                padding: 5px;
                max-height: 100px;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setSpacing(10)
        summary_layout.setContentsMargins(5, 5, 5, 5)
        
        # Totals Section
        totals_layout = QHBoxLayout()
        totals_layout.setSpacing(10)
        
        # Discount Section
        discount_layout = QHBoxLayout()
        discount_label = QLabel("الخصم:")
        discount_label.setStyleSheet("color: #c5a572; font-size: 12px;")
        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("0.00")
        self.discount_input.setFixedWidth(80)
        self.discount_input.setFixedHeight(25)
        self.discount_input.setStyleSheet("""
            QLineEdit {
                padding: 2px 5px;
                background-color: rgba(10, 17, 40, 0.95);
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 3px;
                font-size: 12px;
            }
        """)
        self.discount_input.textChanged.connect(self.update_totals)
        discount_layout.addWidget(discount_label)
        discount_layout.addWidget(self.discount_input)
        totals_layout.addLayout(discount_layout)
        
        # VAT Section
        vat_layout = QHBoxLayout()
        vat_label = QLabel("ضريبة القيمة المضافة:")
        vat_label.setStyleSheet("color: #c5a572; font-size: 12px;")
        self.vat_checkbox = QCheckBox()
        self.vat_checkbox.setStyleSheet("QCheckBox { color: #c5a572; }")
        self.vat_rate = QDoubleSpinBox()
        self.vat_rate.setRange(0, 100)
        self.vat_rate.setValue(14)
        self.vat_rate.setSuffix(" %")
        self.vat_rate.setEnabled(False)
        self.vat_rate.setFixedWidth(80)
        self.vat_rate.setFixedHeight(25)
        self.vat_rate.setStyleSheet("""
            QDoubleSpinBox {
                padding: 2px 5px;
                background-color: rgba(10, 17, 40, 0.95);
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 3px;
                font-size: 12px;
            }
        """)
        
        vat_layout.addWidget(vat_label)
        vat_layout.addWidget(self.vat_checkbox)
        vat_layout.addWidget(self.vat_rate)
        totals_layout.addLayout(vat_layout)
        
        # Connect VAT checkbox
        self.vat_checkbox.stateChanged.connect(self.on_vat_changed)
        
        # Totals Labels
        totals_labels_layout = QHBoxLayout()
        self.total_label = QLabel("الإجمالي: 0.00")
        self.final_total_label = QLabel("المجموع النهائي: 0.00")
        
        for label in [self.total_label, self.final_total_label]:
            label.setStyleSheet("color: #c5a572; font-size: 14px; font-weight: bold; margin: 0 5px;")
            totals_labels_layout.addWidget(label)
        
        totals_layout.addLayout(totals_labels_layout)
        summary_layout.addLayout(totals_layout)
        order_layout.addWidget(summary_frame)
        
        # Order Actions
        actions_layout = QHBoxLayout()
        
        self.save_order_btn = QPushButton("حفظ الطلب")
        self.print_invoice_btn = QPushButton("طباعة الفاتورة")
        self.clear_order_btn = QPushButton("مسح الطلب")
        
        for btn in [self.save_order_btn, self.print_invoice_btn, self.clear_order_btn]:
            btn.setStyleSheet(self.get_button_style())
            actions_layout.addWidget(btn)
        
        self.save_order_btn.clicked.connect(self.save_order)
        self.print_invoice_btn.clicked.connect(lambda: self.print_invoice())
        self.clear_order_btn.clicked.connect(self.clear_order)
        
        order_layout.addLayout(actions_layout)
        main_layout.addWidget(order_frame)

        self.setLayout(main_layout)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #c5a572;
                color: #1c2841;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d4af37;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """

    def get_delete_button_style(self):
        """نمط زر الحذف"""
        return """
            QPushButton {
                background-color: #8B0000;  /* أحمر داكن */
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #A52A2A;  /* أحمر فاتح عند التحويم */
            }
            QPushButton:pressed {
                background-color: #800000;  /* أحمر داكن عند الضغط */
            }
        """

    def load_products_data(self):
        """تحميل بيانات المنتجات من قاعدة البيانات"""
        self.products_data = self.db_manager.get_products_with_details()
        self.update_products_list()

    def update_products_list(self, search_text=""):
        """تحديث قائمة المنتجات مع إمكانية البحث"""
        self.products_list.setRowCount(0)
        self.products_list.setColumnCount(5)
        self.products_list.setHorizontalHeaderLabels([
            "الكود", "المنتج", "سعر البيع", "سعر الجملة", "المخزون"
        ])
        
        for product in self.products_data:
            if search_text.lower() in product[1].lower():
                # تحديث المخزون المتاح من قاعدة البيانات
                current_stock = self.db_manager.get_warehouse_product_quantity(
                    product[11], product[0])
                
                if current_stock == 0:  # تخطي المنتجات التي نفذت من المخزون
                    continue
                    
                row = self.products_list.rowCount()
                self.products_list.insertRow(row)
                
                # إضافة بيانات المنتج
                self.products_list.setItem(row, 0, QTableWidgetItem(str(product[0])))  # الكود
                self.products_list.setItem(row, 1, QTableWidgetItem(product[1]))  # اسم المنتج
                self.products_list.setItem(row, 2, QTableWidgetItem(str(product[10])))  # سعر البيع
                self.products_list.setItem(row, 3, QTableWidgetItem(str(product[9])))  # سعر الجملة
                self.products_list.setItem(row, 4, QTableWidgetItem(str(current_stock)))  # المخزون الحالي
                
                # تلوين المخزون حسب الحد الأدنى
                if current_stock <= product[5]:
                    self.products_list.item(row, 4).setForeground(QColor("#ff4444"))

        self.products_list.resizeColumnsToContents()

    def search_products(self):
        """البحث في المنتجات"""
        search_text = self.product_search.text()
        self.update_products_list(search_text)

    def add_product_to_order(self, item):
        """إضافة منتج إلى الطلب الحالي"""
        row = item.row()
        product_id = int(self.products_list.item(row, 0).text())
        product_name = self.products_list.item(row, 1).text()
        retail_price = float(self.products_list.item(row, 2).text())
        wholesale_price = float(self.products_list.item(row, 3).text())
        
        # تحديث المخزون المتاح من قاعدة البيانات
        current_stock = self.db_manager.get_warehouse_product_quantity(
            self.products_data[row][11], product_id)
        
        # فتح نافذة تحديد الكمية والسعر
        price_dialog = PriceQuantityDialog(wholesale_price, retail_price, current_stock)
        if price_dialog.exec() == QDialog.DialogCode.Accepted:
            quantity = price_dialog.quantity_spin.value()
            selected_price = price_dialog.get_selected_price()
            price_type = price_dialog.get_price_type()
            
            # التحقق من المخزون مرة أخرى قبل الإضافة
            current_stock = self.db_manager.get_warehouse_product_quantity(
                self.products_data[row][11], product_id)
            if quantity > current_stock:
                QMessageBox.warning(self, "تنبيه", 
                                  f"الكمية المطلوبة غير متوفرة. المخزون المتاح: {current_stock}")
                return
            
            # إضافة المنتج إلى جدول الطلب
            row = self.order_table.rowCount()
            self.order_table.insertRow(row)
            
            self.order_table.setItem(row, 0, QTableWidgetItem(str(product_id)))
            self.order_table.setItem(row, 1, QTableWidgetItem(product_name))
            self.order_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
            self.order_table.setItem(row, 3, QTableWidgetItem(str(selected_price)))
            self.order_table.setItem(row, 4, QTableWidgetItem(str(selected_price * quantity)))
            self.order_table.setItem(row, 5, QTableWidgetItem(price_type))
            delete_button = QPushButton("حذف")
            delete_button.setStyleSheet(self.get_delete_button_style())
            delete_button.clicked.connect(lambda: self.remove_product_from_order(row))
            self.order_table.setCellWidget(row, 6, delete_button)
            
            # تحديث المجاميع والبيانات
            self.update_order_totals()
            self.refresh_data()

    def remove_product_from_order(self, row):
        """حذف منتج من الطلب"""
        self.order_table.removeRow(row)
        self.update_order_totals()

    def update_order_totals(self):
        """تحديث مجاميع الطلب"""
        total = 0
        for row in range(self.order_table.rowCount()):
            total += float(self.order_table.item(row, 4).text())
        
        self.current_order['total'] = total
        
        # حساب الخصم إذا كان هناك عميل
        if self.current_order['customer']:
            self.current_order['discount'] = self.current_order['customer']['discount']
        else:
            self.current_order['discount'] = 0
        
        final_total = total - self.current_order['discount']
        
        # تحديث الملصقات
        self.total_label.setText(f"الإجمالي: {total:.2f}")
        self.discount_label.setText(f"الخصم: {self.current_order['discount']:.2f}")
        self.final_total_label.setText(f"المجموع النهائي: {final_total:.2f}")

    def add_new_customer(self):
        """إضافة عميل جديد"""
        dialog = AddCustomerDialog(self.db_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customer(dialog.customer_id)

    def load_customer(self, customer_id):
        """تحميل بيانات العميل"""
        customer = self.db_manager.get_customer_details(customer_id)
        if customer:
            self.current_order['customer'] = {
                'id': customer[0],
                'name': customer[1],
                'address': customer[2],
                'phone': customer[3],
                'discount': float(customer[4]) if customer[4] else 0
            }
            self.customer_info.setText(
                f"العميل: {customer[1]}\n"
                f"الخصم: {customer[4]} جنيه"
            )
            self.update_order_totals()

    def save_order(self):
        """حفظ الطلب في قاعدة البيانات"""
        if not self.order_table.rowCount():
            QMessageBox.warning(self, "تنبيه", "لا يوجد منتجات في الطلب")
            return

        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            # إنشاء الطلب
            cursor.execute("""
                INSERT INTO orders (customer_id, order_date, total_price)
                VALUES (?, DATE('now'), ?)
            """, (
                self.current_order['customer']['id'] if self.current_order['customer'] else None,
                self.current_order['total']
            ))
            order_id = cursor.lastrowid

            total_profit = 0
            # إضافة تفاصيل الطلب وتحديث المخزون
            for row in range(self.order_table.rowCount()):
                product_id = int(self.order_table.item(row, 0).text())
                quantity = int(self.order_table.item(row, 2).text())
                price = float(self.order_table.item(row, 3).text())
                price_type = self.order_table.item(row, 5).text()

                # إضافة تفاصيل الطلب
                cursor.execute("""
                    INSERT INTO order_details (order_id, product_id, quantity, sale_price, price_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, product_id, quantity, price, price_type))

                # تحديث المخزون
                cursor.execute("""
                    UPDATE products 
                    SET current_stock = current_stock - ?
                    WHERE product_id = ?
                """, (quantity, product_id))

                # تحديث المخزون في المستودع
                warehouse_id = self.products_data[row][11]
                cursor.execute("""
                    UPDATE warehouse_products 
                    SET quantity = quantity - ?
                    WHERE warehouse_id = ? AND product_id = ?
                """, (quantity, warehouse_id, product_id))

                # حساب الربح
                cursor.execute("""
                    SELECT MIN(supply_price) 
                    FROM supplier_products 
                    WHERE product_id = ?
                """, (product_id,))
                supply_price = cursor.fetchone()[0] or 0
                item_profit = (price - supply_price) * quantity
                total_profit += item_profit

                # التحقق من مستوى المخزون وإنشاء تنبيه إذا لزم الأمر
                cursor.execute("""
                    SELECT current_stock, min_stock_level 
                    FROM products 
                    WHERE product_id = ?
                """, (product_id,))
                current_stock, min_stock = cursor.fetchone()

                if current_stock <= min_stock:
                    cursor.execute("""
                        SELECT alert_id FROM stock_alerts 
                        WHERE product_id = ?
                    """, (product_id,))
                    existing_alert = cursor.fetchone()
                    
                    if existing_alert:
                        cursor.execute("""
                            UPDATE stock_alerts 
                            SET current_stock = ?, 
                                alert_status = TRUE,
                                alert_threshold = ?
                            WHERE product_id = ?
                        """, (current_stock, min_stock, product_id))
                    else:
                        cursor.execute("""
                            INSERT INTO stock_alerts 
                            (product_id, current_stock, alert_threshold, alert_status)
                            VALUES (?, ?, ?, TRUE)
                        """, (product_id, current_stock, min_stock))

                    # إنشاء إشعار
                    cursor.execute("""
                        INSERT INTO notifications 
                        (notification_type, notification_content)
                        VALUES ('تنبيه المخزون', ?)
                    """, (f"المنتج {product_id} وصل للحد الأدنى للمخزون: {current_stock}",))

            # إنشاء فاتورة
            cursor.execute("""
                INSERT INTO invoices (order_id, total_amount, profit, invoice_date)
                VALUES (?, ?, ?, DATE('now'))
            """, (
                order_id,
                self.current_order['total'] - self.current_order['discount'],
                total_profit
            ))

            # تسجيل النشاط
            cursor.execute("""
                INSERT INTO activity_logs (user_id, action_type, action_details)
                VALUES (?, 'طلب جديد', ?)
            """, (1, f"تم إنشاء طلب جديد برقم {order_id}"))

            conn.commit()
            QMessageBox.information(self, "نجاح", "تم حفظ الطلب بنجاح")
            self.cancel_order()  # إعادة تعيين نموذج الطلب

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الطلب: {str(e)}")
        finally:
            conn.close()

    def cancel_order(self):
        """إلغاء الطلب الحالي"""
        self.order_table.setRowCount(0)
        self.current_order = {
            'customer': None,
            'items': [],
            'total': 0,
            'discount': 0
        }
        self.customer_info.setText("لم يتم اختيار عميل")
        self.update_order_totals()

    def print_invoice(self, order_id=None):
        """طباعة الفاتورة"""
        try:
            filename = f"invoice_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # تسجيل الخطوط العربية
            pdfmetrics.registerFont(TTFont('Arabic', 'fonts/arabic/NotoNaskhArabic-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('Arabic-Bold', 'fonts/arabic/NotoNaskhArabic-Bold.ttf'))
            
            # تحسين النص العربي
            def arabic_text(text):
                if not text:
                    return ""
                # تحسين معالجة الأرقام العربية
                arabic_numbers = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
                                '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'}
                text = str(text)
                for eng, ar in arabic_numbers.items():
                    text = text.replace(eng, ar)
                
                # معالجة النص العربي
                reshaped_text = arabic_reshaper.reshape(text)
                bidi_text = get_display(reshaped_text)
                return bidi_text
            
            # إنشاء ملف الفاتورة
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=20,
                leftMargin=20,
                topMargin=20,
                bottomMargin=20
            )
            
            elements = []
            
            # شعار الشركة
            logo = Image("assets/noor_alislam.png", width=100, height=100)
            logo_table = Table([[logo]], colWidths=[A4[0]-40])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(logo_table)
            elements.append(Spacer(1, 20))
            
            # ترويسة الفاتورة
            header_data = [
                [arabic_text('رقم الفاتورة: ' + str(order_id)), arabic_text('فاتورة ضريبية مبسطة')],
                [arabic_text(f'التاريخ: {datetime.now().strftime("%Y-%m-%d")}'), arabic_text('نور الإسلام')],
                [arabic_text(f'الوقت: {datetime.now().strftime("%H:%M:%S")}'), arabic_text('الرقم الضريبي: ١٢٣٤٥٦٧٨٩')]
            ]
            header_table = Table(header_data, colWidths=[(A4[0]-40)/2]*2)
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONT', (0, 0), (-1, -1), 'Arabic-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 20))
            
            # معلومات العميل
            if self.current_order['customer']:
                customer_data = [
                    [arabic_text('بيانات العميل')],
                    [arabic_text(f"الاسم: {self.current_order['customer']['name']}")],
                    [arabic_text(f"العنوان: {self.current_order['customer'].get('address', '')}")],
                    [arabic_text(f"رقم الهاتف: {self.current_order['customer'].get('phone', '')}")],
                ]
            else:
                customer_data = [[arabic_text('عميل نقدي')]]
            
            customer_table = Table(customer_data, colWidths=[A4[0]-40])
            customer_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONT', (0, 0), (0, 0), 'Arabic-Bold'),
                ('FONT', (0, 1), (-1, -1), 'Arabic'),
                ('FONTSIZE', (0, 0), (0, 0), 14),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.9, 0.9, 0.9)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ]))
            elements.append(customer_table)
            elements.append(Spacer(1, 20))
            
            # جدول المنتجات
            products_data = [[
                arabic_text('الإجمالي'),
                arabic_text('السعر'),
                arabic_text('الكمية'),
                arabic_text('الصنف'),
                arabic_text('م')
            ]]
            
            for row in range(self.order_table.rowCount()):
                products_data.append([
                    f"{float(self.order_table.item(row, 4).text()):.2f}",
                    f"{float(self.order_table.item(row, 3).text()):.2f}",
                    self.order_table.item(row, 2).text(),
                    arabic_text(self.order_table.item(row, 1).text()),
                    str(row + 1)
                ])
            
            # إضافة صف المجموع
            products_data.append([
                f"{self.current_order['total']:.2f}",
                "",
                "",
                arabic_text("الإجمالي"),
                ""
            ])
            
            # إضافة صف الخصم إذا وجد
            if self.current_order['discount'] > 0:
                products_data.append([
                    f"{self.current_order['discount']:.2f}",
                    "",
                    "",
                    arabic_text("الخصم"),
                    ""
                ])
            
            # إضافة صف المجموع الفرعي
            subtotal = self.current_order['total'] - self.current_order['discount']
            products_data.append([
                f"{subtotal:.2f}",
                "",
                "",
                arabic_text("الصافي"),
                ""
            ])
            
            # إضافة ضريبة القيمة المضافة إذا كانت مفعلة
            if self.vat_checkbox.isChecked():
                vat_rate = self.vat_rate.value() / 100
                vat_amount = subtotal * vat_rate
                products_data.append([
                    f"{vat_amount:.2f}",
                    "",
                    "",
                    arabic_text(f"ضريبة القيمة المضافة {self.vat_rate.value()}%"),
                    ""
                ])
                
                # المجموع النهائي مع الضريبة
                final_total = subtotal + vat_amount
                products_data.append([
                    f"{final_total:.2f}",
                    "",
                    "",
                    arabic_text("الإجمالي شامل الضريبة"),
                    ""
                ])
            
            col_widths = [70, 70, 60, A4[0]-260, 30]
            products_table = Table(products_data, colWidths=col_widths, repeatRows=1)
            products_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-2, -1), 'CENTER'),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                ('FONT', (0, 0), (-1, 0), 'Arabic-Bold'),
                ('FONT', (0, 1), (-1, -1), 'Arabic'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(products_table)
            elements.append(Spacer(1, 20))
            
            # إضافة QR code
            qr_table = self.get_qr_code()
            if qr_table:
                elements.append(qr_table)
            
            # إضافة التذييل
            footer_text = arabic_text("شكراً لتعاملكم معنا - نور الإسلام")
            footer = Paragraph(footer_text, ParagraphStyle(
                'footer',
                fontName='Arabic',
                fontSize=12,
                alignment=2,  # محاذاة لليمين
                textColor=colors.black
            ))
            elements.append(Spacer(1, 20))
            elements.append(footer)
            
            # إنشاء الفاتورة
            doc.build(elements)
            
            # فتح الفاتورة
            os.startfile(filename)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء طباعة الفاتورة: {str(e)}")

    def get_qr_code(self):
        """إنشاء QR code للفاتورة"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr_data = {
                'seller_name': 'نور الإسلام',
                'tax_number': '123456789',
                'invoice_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_amount': self.current_order['total'] - self.current_order['discount'],
                'tax_amount': (self.current_order['total'] - self.current_order['discount']) * 0.14
            }
            qr.add_data(json.dumps(qr_data, ensure_ascii=False))
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # حفظ QR code مؤقتاً
            temp_qr_path = "temp_qr.png"
            qr_img.save(temp_qr_path)
            
            # إنشاء جدول يحتوي على QR code
            qr_table = Table([[Image(temp_qr_path, width=100, height=100)]], 
                            colWidths=[100], rowHeights=[100])
            qr_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            return qr_table
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None

    def refresh_data(self):
        """تحديث جميع البيانات في الواجهة"""
        self.load_products_data()
        if self.current_order['customer']:
            self.load_customer(self.current_order['customer']['id'])
        self.update_order_totals()

    def on_vat_changed(self, state):
        """معالجة تغيير حالة ضريبة القيمة المضافة"""
        self.vat_rate.setEnabled(state == 2)  # 2 means checked
        self.update_totals()

    def update_totals(self):
        """تحديث المجاميع والضريبة"""
        total = 0
        for row in range(self.order_table.rowCount()):
            total += float(self.order_table.item(row, 4).text())
        
        # تطبيق الخصم
        discount = float(self.discount_input.text()) if self.discount_input.text() else 0
        subtotal = total - discount
        
        # حساب ضريبة القيمة المضافة
        vat_amount = 0
        if self.vat_checkbox.isChecked():
            vat_rate = self.vat_rate.value() / 100
            vat_amount = subtotal * vat_rate
        
        # تحديث المجاميع
        final_total = subtotal + vat_amount
        
        self.total_label.setText(f"{total:.2f}")
        self.final_total_label.setText(f"{final_total:.2f}")

    def clear_order(self):
        """مسح الطلب الحالي"""
        try:
            # تأكيد المسح
            reply = QMessageBox.question(
                self, 
                "تأكيد المسح",
                "هل أنت متأكد من مسح الطلب الحالي؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # مسح جدول الطلب
                self.order_table.setRowCount(0)
                
                # إعادة تعيين المجاميع
                self.discount_input.clear()
                self.vat_checkbox.setChecked(False)
                self.vat_rate.setValue(14)
                
                # تحديث المجاميع
                self.update_totals()
                
                # إعادة تعيين بيانات الطلب
                self.current_order = {
                    'customer': None,
                    'items': [],
                    'total': 0,
                    'discount': 0,
                    'vat': 0,
                    'final_total': 0
                }
                
                QMessageBox.information(self, "تم", "تم مسح الطلب بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء مسح الطلب: {str(e)}")

    def update_order_totals(self):
        """تحديث مجاميع الطلب"""
        try:
            total = 0
            for row in range(self.order_table.rowCount()):
                total += float(self.order_table.item(row, 4).text())
            
            # تحديث إجمالي الطلب
            self.current_order['total'] = total
            
            # تحديث الخصم
            discount = float(self.discount_input.text()) if self.discount_input.text() else 0
            self.current_order['discount'] = discount
            
            # حساب الصافي
            subtotal = total - discount
            
            # حساب ضريبة القيمة المضافة
            vat_amount = 0
            if self.vat_checkbox.isChecked():
                vat_rate = self.vat_rate.value() / 100
                vat_amount = subtotal * vat_rate
            self.current_order['vat'] = vat_amount
            
            # حساب الإجمالي النهائي
            final_total = subtotal + vat_amount
            self.current_order['final_total'] = final_total
            
            # تحديث الواجهة
            self.total_label.setText(f"{total:.2f}")
            self.final_total_label.setText(f"{final_total:.2f}")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث المجاميع: {str(e)}")

    def add_new_customer(self):
        """إضافة عميل جديد"""
        try:
            # هنا يمكن إضافة نافذة لإضافة عميل جديد
            QMessageBox.information(self, "قريباً", "سيتم إضافة هذه الميزة قريباً")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def show_keyboard(self):
        """إظهار لوحة المفاتيح على الشاشة"""
        try:
            import subprocess
            # تشغيل لوحة المفاتيح الافتراضية لويندوز
            subprocess.Popen('osk.exe')
        except Exception as e:
            QMessageBox.warning(self, "خطأ", "لم نتمكن من فتح لوحة المفاتيح")


class PriceQuantityDialog(QDialog):
    """نافذة تحدد الكمية والسعر"""
    def __init__(self, wholesale_price, retail_price, max_quantity, parent=None):
        super().__init__(parent)
        self.wholesale_price = wholesale_price
        self.retail_price = retail_price
        self.setWindowTitle("تحديد الكمية والسعر")
        self.setFixedSize(400, 250)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # Quantity Spinner
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("الكمية:")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, max_quantity)
        self.quantity_spin.setValue(1)
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_spin)
        layout.addLayout(quantity_layout)
        
        # Price Selection
        price_group = QGroupBox("نوع السعر")
        price_layout = QVBoxLayout()
        
        self.retail_radio = QRadioButton(f"سعر البيع: {retail_price}")
        self.wholesale_radio = QRadioButton(f"سعر الجملة: {wholesale_price}")
        self.custom_radio = QRadioButton("سعر مخصص")
        
        self.retail_radio.setChecked(True)
        
        price_layout.addWidget(self.retail_radio)
        price_layout.addWidget(self.wholesale_radio)
        price_layout.addWidget(self.custom_radio)
        
        self.custom_price = QDoubleSpinBox()
        self.custom_price.setRange(wholesale_price, retail_price * 1.5)
        self.custom_price.setValue(retail_price)
        self.custom_price.setEnabled(False)
        price_layout.addWidget(self.custom_price)
        
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)
        
        # Connect signals
        self.custom_radio.toggled.connect(self.custom_price.setEnabled)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("موافق")
        cancel_btn = QPushButton("إلغاء")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setStyleSheet(self.get_style())

    def get_selected_price(self):
        if self.retail_radio.isChecked():
            return self.retail_price
        elif self.wholesale_radio.isChecked():
            return self.wholesale_price
        else:
            return self.custom_price.value()

    def get_price_type(self):
        if self.retail_radio.isChecked():
            return 'retail'
        elif self.wholesale_radio.isChecked():
            return 'wholesale'
        else:
            return 'custom'

    def get_style(self):
        return """
            QDialog {
                background-color: #1c2841;
            }
            QLabel, QRadioButton, QGroupBox {
                color: #c5a572;
                font-size: 14px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #0a1128;
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #c5a572;
                color: #0a1128;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d4af37;
            }
        """


class AddCustomerDialog(QDialog):
    """نافذة إضافة عميل جديد"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer_id = None
        self.setWindowTitle("إضافة عميل جديد")
        self.setFixedSize(400, 300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Customer Name
        name_layout = QHBoxLayout()
        name_label = QLabel("اسم العميل:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Address
        address_layout = QHBoxLayout()
        address_label = QLabel("العنوان:")
        self.address_input = QLineEdit()
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.address_input)
        layout.addLayout(address_layout)
        
        # Phone
        phone_layout = QHBoxLayout()
        phone_label = QLabel("رقم الهاتف:")
        self.phone_input = QLineEdit()
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # Discount Amount (changed from percentage to amount)
        discount_layout = QHBoxLayout()
        discount_label = QLabel("قيمة الخصم:")
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 1000000)
        self.discount_input.setSuffix(" جنيه")
        discount_layout.addWidget(discount_label)
        discount_layout.addWidget(self.discount_input)
        layout.addLayout(discount_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        cancel_btn = QPushButton("إلغاء")
        
        save_btn.clicked.connect(self.save_customer)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #1c2841;
            }
            QLabel {
                color: #c5a572;
                font-size: 14px;
            }
            QLineEdit, QDoubleSpinBox {
                background-color: #0a1128;
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #c5a572;
                color: #0a1128;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d4af37;
            }
        """)

    def save_customer(self):
        """حفظ بيانات العميل"""
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم العميل")
            return
        
        try:
            self.customer_id = self.db_manager.add_customer(
                name,
                self.address_input.text(),
                self.phone_input.text(),
                self.discount_input.value()
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ بيانات العميل: {str(e)}")


class CustomerManagementDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("إدارة العملاء")
        self.setFixedSize(800, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()
        self.load_customers()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Customers Table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels([
            "الكود", "اسم العميل", "العنوان", "رقم الهاتف", "الخصم"
        ])
        self.customers_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(10, 17, 40, 0.95);
                color: #c5a572;
                border: none;
            }
            QHeaderView::section {
                background-color: #0a1128;
                color: #c5a572;
                padding: 5px;
                border: 1px solid #c5a572;
            }
        """)
        layout.addWidget(self.customers_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("إضافة عميل")
        edit_btn = QPushButton("تعديل العميل")
        delete_btn = QPushButton("حذف العميل")
        select_btn = QPushButton("اختيار العميل")
        
        for btn in [add_btn, edit_btn, delete_btn, select_btn]:
            btn.setStyleSheet(self.get_button_style())
            buttons_layout.addWidget(btn)
        
        add_btn.clicked.connect(self.add_customer)
        edit_btn.clicked.connect(self.edit_customer)
        delete_btn.clicked.connect(self.delete_customer)
        select_btn.clicked.connect(self.select_customer)
        
        layout.addLayout(buttons_layout)

    def load_customers(self):
        customers = self.db_manager.get_customers()
        self.customers_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            for col, value in enumerate(customer):
                item = QTableWidgetItem(str(value))
                self.customers_table.setItem(row, col, item)
        self.customers_table.resizeColumnsToContents()

    def add_customer(self):
        dialog = AddEditCustomerDialog(self.db_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()

    def edit_customer(self):
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار عميل للتعديل")
            return
        
        customer_id = int(self.customers_table.item(current_row, 0).text())
        customer = self.db_manager.get_customer_details(customer_id)
        
        dialog = AddEditCustomerDialog(self.db_manager, customer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()

    def delete_customer(self):
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار عميل للحذف")
            return
        
        customer_id = int(self.customers_table.item(current_row, 0).text())
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا العميل؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_customer(customer_id):
                self.load_customers()
                QMessageBox.information(self, "نجاح", "تم حذف العميل بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "لا يمكن حذف العميل لوجود طلبا مرتبطة به")

    def select_customer(self):
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار عميل")
            return
        
        self.selected_customer_id = int(self.customers_table.item(current_row, 0).text())
        self.accept()

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #c5a572;
                color: #0a1128;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d4af37;
            }
        """


class AddEditCustomerDialog(QDialog):
    """نافذة إضافة/تعديل عميل"""
    def __init__(self, db_manager, customer_data=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer_data = customer_data
        self.setWindowTitle("إضافة عميل جديد" if not customer_data else "تعديل بيانات العميل")
        self.setFixedSize(400, 300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Customer Name
        name_layout = QHBoxLayout()
        name_label = QLabel("اسم العميل:")
        self.name_input = QLineEdit()
        if self.customer_data:
            self.name_input.setText(self.customer_data[1])
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Address
        address_layout = QHBoxLayout()
        address_label = QLabel("العنوان:")
        self.address_input = QLineEdit()
        if self.customer_data:
            self.address_input.setText(self.customer_data[2])
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.address_input)
        layout.addLayout(address_layout)
        
        # Phone
        phone_layout = QHBoxLayout()
        phone_label = QLabel("رقم الهاتف:")
        self.phone_input = QLineEdit()
        if self.customer_data:
            self.phone_input.setText(self.customer_data[3])
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # Discount
        discount_layout = QHBoxLayout()
        discount_label = QLabel("قيمة الخصم:")
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 1000000)
        self.discount_input.setSuffix(" جنيه")
        if self.customer_data:
            self.discount_input.setValue(float(self.customer_data[4] or 0))
        discount_layout.addWidget(discount_label)
        discount_layout.addWidget(self.discount_input)
        layout.addLayout(discount_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        cancel_btn = QPushButton("إلغاء")
        
        save_btn.clicked.connect(self.save_customer)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1c2841;
            }
            QLabel {
                color: #c5a572;
                font-size: 14px;
            }
            QLineEdit, QDoubleSpinBox {
                background-color: #0a1128;
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #c5a572;
                color: #0a1128;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d4af37;
            }
        """)

    def save_customer(self):
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم العميل")
            return
        
        try:
            if self.customer_data:
                success = self.db_manager.update_customer(
                    self.customer_data[0],
                    name,
                    self.address_input.text(),
                    self.phone_input.text(),
                    self.discount_input.value()
                )
            else:
                self.customer_id = self.db_manager.add_customer(
                    name,
                    self.address_input.text(),
                    self.phone_input.text(),
                    self.discount_input.value()
                )
                success = bool(self.customer_id)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حفظ بيانات العميل")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ بيانات العميل: {str(e)}")


class CustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إدارة العملاء")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # حول إدخال بيانات العميل
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم العميل")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("رقم الهاتف")
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("العنوان")
        
        # أزرار الإجراءات
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_customer)
        delete_btn = QPushButton("حذف")
        delete_btn.clicked.connect(self.delete_customer)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        
        layout.addWidget(self.name_input)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.address_input)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def save_customer(self):
        """حفظ بيانات العميل"""
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم العميل")
            return
        
        try:
            # TODO: save customer data to database
            pass
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ بيانات العميل: {str(e)}")

    def delete_customer(self):
        """حذف بيانات العميل"""
        # TODO: delete customer data from database
        pass

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                               QDialog, QMessageBox, QComboBox, QDoubleSpinBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from database_manager import DatabaseManager
import datetime

class AddEditSupplierDialog(QDialog):
    def __init__(self, parent=None, supplier_data=None):
        super().__init__(parent)
        self.supplier_data = supplier_data
        self.setWindowTitle("إضافة مورد جديد" if not supplier_data else "تعديل بيانات المورد")
        self.setFixedSize(400, 200)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Supplier Name
        name_layout = QHBoxLayout()
        name_label = QLabel("اسم المورد:")
        self.name_input = QLineEdit()
        if self.supplier_data:
            self.name_input.setText(self.supplier_data[1])
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Contact Details
        contact_layout = QHBoxLayout()
        contact_label = QLabel("بيانات الاتصال:")
        self.contact_input = QLineEdit()
        if self.supplier_data:
            self.contact_input.setText(self.supplier_data[2])
        contact_layout.addWidget(contact_label)
        contact_layout.addWidget(self.contact_input)
        layout.addLayout(contact_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'contact': self.contact_input.text()
        }

class AddSupplierProductDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("إضافة منتج للمورد")
        self.setFixedSize(400, 250)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Product Selection
        product_layout = QHBoxLayout()
        product_label = QLabel("المنتج:")
        self.product_combo = QComboBox()
        self.load_products()
        product_layout.addWidget(product_label)
        product_layout.addWidget(self.product_combo)
        layout.addLayout(product_layout)

        # Supply Price
        price_layout = QHBoxLayout()
        price_label = QLabel("سعر التوريد:")
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setDecimals(2)
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        layout.addLayout(price_layout)

        # Supply Date
        date_layout = QHBoxLayout()
        date_label = QLabel("تاريخ التوريد:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    def load_products(self):
        products = self.db_manager.get_products()
        for product_id, product_name in products:
            self.product_combo.addItem(product_name, product_id)

    def get_data(self):
        return {
            'product_id': self.product_combo.currentData(),
            'supply_price': self.price_input.value(),
            'supply_date': self.date_input.date().toString("yyyy-MM-dd")
        }

class SuppliersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.load_suppliers()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("إدارة الموردين")
        title_label.setStyleSheet("""
            QLabel {
                color: #c5a572;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("إضافة مورد جديد")
        self.add_btn.clicked.connect(self.add_supplier)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("تعديل المورد")
        self.edit_btn.clicked.connect(self.edit_supplier)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("حذف المورد")
        self.delete_btn.clicked.connect(self.delete_supplier)
        buttons_layout.addWidget(self.delete_btn)
        
        self.add_product_btn = QPushButton("إضافة منتج للمورد")
        self.add_product_btn.clicked.connect(self.add_supplier_product)
        buttons_layout.addWidget(self.add_product_btn)
        
        layout.addLayout(buttons_layout)

        # Suppliers Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "رقم المورد", "اسم المورد", "بيانات الاتصال", 
            "المنتجات", "عدد المنتجات"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(28, 40, 65, 0.95);
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #0a1128;
                color: #c5a572;
                padding: 5px;
                border: 1px solid #c5a572;
            }
        """)
        layout.addWidget(self.table)

        # Style buttons
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.add_product_btn]:
            btn.setStyleSheet("""
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

    def load_suppliers(self):
        suppliers = self.db_manager.get_suppliers()
        self.table.setRowCount(len(suppliers))
        for row, supplier in enumerate(suppliers):
            for col, value in enumerate(supplier):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)
        
        self.table.resizeColumnsToContents()

    def add_supplier(self):
        dialog = AddEditSupplierDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.add_supplier(data['name'], data['contact']):
                self.load_suppliers()
                QMessageBox.information(self, "نجاح", "تم إضافة المورد بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة المورد")

    def edit_supplier(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مورد للتعديل")
            return

        supplier_id = int(self.table.item(current_row, 0).text())
        supplier_data = [
            supplier_id,
            self.table.item(current_row, 1).text(),
            self.table.item(current_row, 2).text()
        ]

        dialog = AddEditSupplierDialog(self, supplier_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.update_supplier(supplier_id, data['name'], data['contact']):
                self.load_suppliers()
                QMessageBox.information(self, "نجاح", "تم تحديث بيانات المورد بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تحديث بيانات المورد")

    def delete_supplier(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مورد للحذف")
            return

        supplier_id = int(self.table.item(current_row, 0).text())
        reply = QMessageBox.question(self, "تأكيد الحذف",
                                   "هل أنت متأكد من حذف هذا المورد؟",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_supplier(supplier_id):
                self.load_suppliers()
                QMessageBox.information(self, "نجاح", "تم حذف المورد بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حذف المورد")

    def add_supplier_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مورد لإضافة منتج له")
            return

        supplier_id = int(self.table.item(current_row, 0).text())
        dialog = AddSupplierProductDialog(self, self.db_manager)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.add_supplier_product(
                supplier_id, data['product_id'],
                data['supply_price'], data['supply_date']
            ):
                self.load_suppliers()
                QMessageBox.information(self, "نجاح", "تم إضافة المنتج للمورد بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة المنتج للمورد")

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                               QDialog, QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox,
                               QTextEdit, QSplitter, QGroupBox, QAbstractItemView)
from PyQt6.QtCore import Qt
from database_manager import DatabaseManager

class AddEditProductDialog(QDialog):
    def __init__(self, parent=None, db_manager=None, product_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.product_data = product_data
        self.setWindowTitle("إضافة منتج جديد" if not product_data else "تعديل بيانات المنتج")
        self.setFixedSize(600, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Product Name
        name_layout = QHBoxLayout()
        name_label = QLabel("اسم المنتج:")
        self.name_input = QLineEdit()
        if self.product_data:
            self.name_input.setText(self.product_data[1])
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("وصف المنتج:")
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        if self.product_data:
            self.desc_input.setText(self.product_data[2])
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        # Unit Type
        unit_layout = QHBoxLayout()
        unit_label = QLabel("وحدة القياس:")
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["قطعة", "متر", "كيلو"])
        if self.product_data:
            self.unit_combo.setCurrentText(self.product_data[3])
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(self.unit_combo)
        layout.addLayout(unit_layout)

        # Min Stock Level
        min_stock_layout = QHBoxLayout()
        min_stock_label = QLabel("الحد الأدنى للمخزون:")
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 1000000)
        if self.product_data:
            self.min_stock_input.setValue(self.product_data[4])
        min_stock_layout.addWidget(min_stock_label)
        min_stock_layout.addWidget(self.min_stock_input)
        layout.addLayout(min_stock_layout)

        # Warehouse
        warehouse_layout = QHBoxLayout()
        warehouse_label = QLabel("المخزن:")
        self.warehouse_combo = QComboBox()
        self.load_warehouses()
        if self.product_data and self.product_data[6]:
            index = self.warehouse_combo.findText(self.product_data[6])
            if index >= 0:
                self.warehouse_combo.setCurrentIndex(index)
        warehouse_layout.addWidget(warehouse_label)
        warehouse_layout.addWidget(self.warehouse_combo)
        layout.addLayout(warehouse_layout)

        # Current Stock
        stock_layout = QHBoxLayout()
        stock_label = QLabel("المخزون الحالي:")
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 1000000)
        if self.product_data:
            self.stock_input.setValue(self.product_data[5])
        stock_layout.addWidget(stock_label)
        stock_layout.addWidget(self.stock_input)
        layout.addLayout(stock_layout)

        # Suppliers
        suppliers_layout = QVBoxLayout()
        suppliers_label = QLabel("الموردين:")
        self.suppliers_list = QTableWidget()
        self.suppliers_list.setColumnCount(2)
        self.suppliers_list.setHorizontalHeaderLabels(["المورد", "سعر التوريد"])
        self.suppliers_list.setMaximumHeight(150)
        self.load_suppliers()
        suppliers_layout.addWidget(suppliers_label)
        suppliers_layout.addWidget(self.suppliers_list)

        # Add Supplier Button
        add_supplier_btn = QPushButton("إضافة مورد")
        add_supplier_btn.clicked.connect(self.add_supplier_row)
        suppliers_layout.addWidget(add_supplier_btn)
        layout.addLayout(suppliers_layout)

        # Prices
        prices_layout = QVBoxLayout()
        
        # Supply Price
        supply_price_layout = QHBoxLayout()
        supply_price_label = QLabel("سعر التوريد:")
        self.supply_price_input = QDoubleSpinBox()
        self.supply_price_input.setRange(0, 1000000)
        self.supply_price_input.setDecimals(2)
        if self.product_data and self.product_data[7]:
            self.supply_price_input.setValue(float(self.product_data[7]))
        supply_price_layout.addWidget(supply_price_label)
        supply_price_layout.addWidget(self.supply_price_input)
        prices_layout.addLayout(supply_price_layout)

        # Wholesale Price
        wholesale_price_layout = QHBoxLayout()
        wholesale_price_label = QLabel("سعر الجملة:")
        self.wholesale_price_input = QDoubleSpinBox()
        self.wholesale_price_input.setRange(0, 1000000)
        self.wholesale_price_input.setDecimals(2)
        if self.product_data and self.product_data[9]:
            self.wholesale_price_input.setValue(float(self.product_data[9]))
        wholesale_price_layout.addWidget(wholesale_price_label)
        wholesale_price_layout.addWidget(self.wholesale_price_input)
        prices_layout.addLayout(wholesale_price_layout)

        # Retail Price
        retail_price_layout = QHBoxLayout()
        retail_price_label = QLabel("سعر البيع:")
        self.retail_price_input = QDoubleSpinBox()
        self.retail_price_input.setRange(0, 1000000)
        self.retail_price_input.setDecimals(2)
        if self.product_data and self.product_data[10]:
            self.retail_price_input.setValue(float(self.product_data[10]))
        retail_price_layout.addWidget(retail_price_label)
        retail_price_layout.addWidget(self.retail_price_input)
        prices_layout.addLayout(retail_price_layout)

        layout.addLayout(prices_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("إلغاء")
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
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget {
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
            QHeaderView::section {
                background-color: #0a1128;
                color: #c5a572;
                padding: 5px;
                border: 1px solid #c5a572;
            }
        """)

    def load_warehouses(self):
        warehouses = self.db_manager.get_warehouses()
        for warehouse_id, warehouse_name in warehouses:
            self.warehouse_combo.addItem(warehouse_name, warehouse_id)

    def load_suppliers(self):
        suppliers = self.db_manager.get_suppliers()
        self.suppliers = {supplier[1]: supplier[0] for supplier in suppliers}
        
        if self.product_data:
            # Load existing suppliers for this product
            product_id = self.product_data[0]
            supplier_products = self.db_manager.get_supplier_products(product_id)
            
            self.suppliers_list.setRowCount(len(supplier_products))
            for row, sp in enumerate(supplier_products):
                supplier_combo = QComboBox()
                supplier_combo.addItems(self.suppliers.keys())
                supplier_combo.setCurrentText(sp[1])
                
                price_input = QDoubleSpinBox()
                price_input.setRange(0, 1000000)
                price_input.setDecimals(2)
                price_input.setValue(float(sp[2]))
                
                self.suppliers_list.setCellWidget(row, 0, supplier_combo)
                self.suppliers_list.setCellWidget(row, 1, price_input)
        else:
            self.add_supplier_row()

    def add_supplier_row(self):
        current_row = self.suppliers_list.rowCount()
        self.suppliers_list.setRowCount(current_row + 1)
        
        supplier_combo = QComboBox()
        supplier_combo.addItems(self.suppliers.keys())
        
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 1000000)
        price_input.setDecimals(2)
        
        self.suppliers_list.setCellWidget(current_row, 0, supplier_combo)
        self.suppliers_list.setCellWidget(current_row, 1, price_input)

    def get_data(self):
        suppliers_data = []
        for row in range(self.suppliers_list.rowCount()):
            supplier_combo = self.suppliers_list.cellWidget(row, 0)
            price_input = self.suppliers_list.cellWidget(row, 1)
            if supplier_combo and price_input and supplier_combo.currentText():
                supplier_id = self.suppliers[supplier_combo.currentText()]
                suppliers_data.append({
                    'supplier_id': supplier_id,
                    'supply_price': price_input.value()
                })

        return {
            'name': self.name_input.text(),
            'description': self.desc_input.toPlainText(),
            'unit_type': self.unit_combo.currentText(),
            'min_stock': self.min_stock_input.value(),
            'current_stock': self.stock_input.value(),
            'warehouse_id': self.warehouse_combo.currentData(),
            'suppliers': suppliers_data,
            'wholesale_price': self.wholesale_price_input.value(),
            'retail_price': self.retail_price_input.value()
        }

class UpdateStockDialog(QDialog):
    def __init__(self, parent=None, db_manager=None, product_id=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.product_id = product_id
        self.setWindowTitle("تحديث المخزون")
        self.setFixedSize(800, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Product Info
        product_info = self.db_manager.get_product_details(self.product_id)
        if product_info:
            info_label = QLabel(f"المنتج: {product_info[1]} | المخزون الحالي: {product_info[5]}")
            info_label.setStyleSheet("color: #c5a572; font-size: 16px; font-weight: bold;")
            layout.addWidget(info_label)

        # Stock Distribution Table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(4)
        self.stock_table.setHorizontalHeaderLabels([
            "المخزن", "المخزون الحالي", "الكمية الجديدة", "الفرق"
        ])
        
        # Style the table
        self.stock_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(28, 40, 65, 0.95);
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
                gridline-color: #c5a572;
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
        
        layout.addWidget(self.stock_table)

        # Total Stock Info
        totals_layout = QHBoxLayout()
        self.total_current = QLabel("إجمالي المخزون الحالي: 0")
        self.total_new = QLabel("إجمالي المخزون الجديد: 0")
        self.total_diff = QLabel("إجمالي الفرق: 0")
        for label in [self.total_current, self.total_new, self.total_diff]:
            label.setStyleSheet("color: #c5a572; font-size: 14px;")
            totals_layout.addWidget(label)
        layout.addLayout(totals_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ التغييرات")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        for btn in [save_btn, cancel_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #c5a572;
                    color: #0a1128;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-size: 14px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #d4af37;
                }
            """)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.load_warehouses()
        
    def load_warehouses(self):
        warehouses = self.db_manager.get_warehouses()
        self.stock_table.setRowCount(len(warehouses))
        
        total_current = 0
        for row, warehouse in enumerate(warehouses):
            warehouse_id, warehouse_name = warehouse
            
            # Warehouse name (read-only)
            name_item = QTableWidgetItem(warehouse_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.stock_table.setItem(row, 0, name_item)
            
            # Current quantity
            current_qty = self.db_manager.get_warehouse_product_quantity(warehouse_id, self.product_id)
            current_item = QTableWidgetItem(str(current_qty))
            current_item.setFlags(current_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.stock_table.setItem(row, 1, current_item)
            total_current += current_qty
            
            # New quantity input
            qty_spinbox = QSpinBox()
            qty_spinbox.setRange(0, 1000000)
            qty_spinbox.setValue(current_qty)
            qty_spinbox.valueChanged.connect(self.update_totals)
            self.stock_table.setCellWidget(row, 2, qty_spinbox)
            
            # Difference (calculated)
            diff_item = QTableWidgetItem('0')
            diff_item.setFlags(diff_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.stock_table.setItem(row, 3, diff_item)
        
        self.stock_table.resizeColumnsToContents()
        self.total_current.setText(f"إجمالي المخزون الحالي: {total_current}")
        self.update_totals()

    def update_totals(self):
        total_current = 0
        total_new = 0
        
        for row in range(self.stock_table.rowCount()):
            current_qty = int(self.stock_table.item(row, 1).text())
            new_qty = self.stock_table.cellWidget(row, 2).value()
            diff = new_qty - current_qty
            
            total_current += current_qty
            total_new += new_qty
            
            # Update difference column
            self.stock_table.item(row, 3).setText(str(diff))
        
        self.total_current.setText(f"إجمالي المخزون الحالي: {total_current}")
        self.total_new.setText(f"إجمالي المخزون الجديد: {total_new}")
        self.total_diff.setText(f"إجمالي الفرق: {total_new - total_current}")

    def get_data(self):
        """
        تجميع بيانات تحديث المخزون من الجدول
        """
        updates = []
        
        for row in range(self.stock_table.rowCount()):
            warehouse_name = self.stock_table.item(row, 0).text()
            new_qty = self.stock_table.cellWidget(row, 2).value()
            
            # Get warehouse_id from name
            warehouses = self.db_manager.get_warehouses()
            warehouse_id = next(w[0] for w in warehouses if w[1] == warehouse_name)
            
            updates.append({
                'warehouse_id': warehouse_id,
                'quantity': new_qty
            })
        
        return updates

    def save_changes(self):
        """
        حفظ التغييرات في قاعدة البيانات
        """
        updates = self.get_data()
        total_new_stock = sum(update['quantity'] for update in updates)
        
        # Update database
        success = True
        try:
            # Start transaction
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            
            # Update product's total stock
            cursor.execute("""
                UPDATE products 
                SET current_stock = ? 
                WHERE product_id = ?
            """, (total_new_stock, self.product_id))
            
            # Update warehouse quantities
            for update in updates:
                cursor.execute("""
                    INSERT OR REPLACE INTO warehouse_products 
                    (warehouse_id, product_id, quantity) 
                    VALUES (?, ?, ?)
                """, (update['warehouse_id'], self.product_id, update['quantity']))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            success = False
            print(f"Error updating stock: {e}")
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حفظ التغييرات")

class ProductsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("إدارة المنتجات")
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
        self.add_btn = QPushButton("إضافة منتج جديد")
        self.add_btn.clicked.connect(self.add_product)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("تعديل المنتج")
        self.edit_btn.clicked.connect(self.edit_product)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("حذف المنتج")
        self.delete_btn.clicked.connect(self.delete_product)
        buttons_layout.addWidget(self.delete_btn)
        
        self.update_stock_btn = QPushButton("تحديث المخزون")
        self.update_stock_btn.clicked.connect(self.update_stock)
        buttons_layout.addWidget(self.update_stock_btn)
        
        layout.addLayout(buttons_layout)

        # Products Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "رقم المنتج", "اسم المنتج", "الوصف", "وحدة القياس",
            "الحد الأدنى", "المخزون الحالي", "المخزن",
            "سعر التوريد", "الموردين", "سعر الجملة", "سعر البيع"
        ])
        
        # Enable column moving
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.horizontalHeader().setDragEnabled(True)
        self.table.horizontalHeader().setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
        # Set selection behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(28, 40, 65, 0.95);
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
                gridline-color: #c5a572;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: rgba(197, 165, 114, 0.2);
            }
            QHeaderView::section {
                background-color: #0a1128;
                color: #c5a572;
                padding: 5px;
                border: 1px solid #c5a572;
            }
            QHeaderView::section:hover {
                background-color: rgba(197, 165, 114, 0.1);
            }
        """)
        
        # Save column positions when moved
        self.table.horizontalHeader().sectionMoved.connect(self.on_column_moved)
        
        layout.addWidget(self.table)

        # Style buttons
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.update_stock_btn]:
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

    def load_products(self):
        products = self.db_manager.get_products_with_details()
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, value in enumerate(product):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                # Make ID column read-only
                if col == 0:  # ID column
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        
        self.table.resizeColumnsToContents()

    def add_product(self):
        dialog = AddEditProductDialog(self, self.db_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.add_product(
                data['name'], data['description'], data['unit_type'],
                data['min_stock'], data['current_stock'], data['warehouse_id'],
                data['suppliers'], data['wholesale_price'], data['retail_price']
            ):
                self.load_products()
                QMessageBox.information(self, "نجاح", "تم إضافة المنتج بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة المنتج")

    def edit_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار منتج للتعديل")
            return

        product_id = int(self.table.item(current_row, 0).text())
        product_data = [
            product_id,
            self.table.item(current_row, 1).text(),
            self.table.item(current_row, 2).text(),
            self.table.item(current_row, 3).text(),
            int(self.table.item(current_row, 4).text()),
            int(self.table.item(current_row, 5).text()),
            self.table.item(current_row, 6).text(),
            self.table.item(current_row, 7).text(),
            self.table.item(current_row, 8).text(),
            self.table.item(current_row, 9).text(),
            self.table.item(current_row, 10).text()
        ]

        dialog = AddEditProductDialog(self, self.db_manager, product_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.update_product(
                product_id, data['name'], data['description'],
                data['unit_type'], data['min_stock'], data['current_stock'],
                data['warehouse_id'], data['suppliers'], data['wholesale_price'], data['retail_price']
            ):
                self.load_products()
                QMessageBox.information(self, "نجاح", "تم تحديث بيانات المنتج بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تحديث بيانات المنتج")

    def delete_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار منتج للحذف")
            return

        product_id = int(self.table.item(current_row, 0).text())
        reply = QMessageBox.question(self, "تأكيد الحذف",
                                   "هل أنت متأكد من حذف هذا المنتج؟",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_product(product_id):
                self.load_products()
                QMessageBox.information(self, "نجاح", "تم حذف المنتج بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حذف المنتج")

    def update_stock(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار منتج لتحديث المخزون")
            return

        product_id = int(self.table.item(current_row, 0).text())
        dialog = UpdateStockDialog(self, self.db_manager, product_id)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updates = dialog.get_data()  # الآن نحصل على قائمة من التحديثات
            success = True
            
            try:
                # Start transaction
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                total_stock = 0
                # تحديث كل مخزن
                for update in updates:
                    warehouse_id = update['warehouse_id']
                    quantity = update['quantity']
                    total_stock += quantity
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO warehouse_products 
                        (warehouse_id, product_id, quantity) 
                        VALUES (?, ?, ?)
                    """, (warehouse_id, product_id, quantity))
                
                # تحديث إجمالي المخزون في جدول المنتجات
                cursor.execute("""
                    UPDATE products 
                    SET current_stock = ? 
                    WHERE product_id = ?
                """, (total_stock, product_id))
                
                conn.commit()
                self.load_products()
                QMessageBox.information(self, "نجاح", "تم تحديث المخزون بنجاح")
                
            except Exception as e:
                conn.rollback()
                success = False
                print(f"Error updating stock: {e}")
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تحديث المخزون")

    def on_column_moved(self, logical_index, old_visual_index, new_visual_index):
        # You can save the column order here if needed
        pass

class AddEditWarehouseDialog(QDialog):
    def __init__(self, parent=None, db_manager=None, warehouse_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.warehouse_data = warehouse_data
        self.setWindowTitle("إضافة مخزن جديد" if not warehouse_data else "تعديل بيانات المخزن")
        self.setFixedSize(400, 300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Warehouse Name
        name_layout = QHBoxLayout()
        name_label = QLabel("اسم المخزن:")
        self.name_input = QLineEdit()
        if self.warehouse_data:
            self.name_input.setText(self.warehouse_data[1])
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Location
        location_layout = QHBoxLayout()
        location_label = QLabel("الموقع:")
        self.location_input = QLineEdit()
        if self.warehouse_data:
            self.location_input.setText(self.warehouse_data[2])
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_input)
        layout.addLayout(location_layout)

        # Contact Details
        contact_layout = QVBoxLayout()
        contact_label = QLabel("معلومات الاتصال:")
        self.contact_input = QTextEdit()
        if self.warehouse_data:
            self.contact_input.setText(self.warehouse_data[3])
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

        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #1c2841;
            }
            QLabel {
                color: #c5a572;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
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

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'location': self.location_input.text(),
            'contact_details': self.contact_input.toPlainText()
        }

class WarehouseManagementDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("إدارة المخازن")
        self.setFixedSize(800, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()
        self.load_warehouses()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left side - Warehouses List
        left_panel = QVBoxLayout()
        
        # Warehouse List
        self.warehouse_list = QTableWidget()
        self.warehouse_list.setColumnCount(2)
        self.warehouse_list.setHorizontalHeaderLabels(["رقم المخزن", "اسم المخزن"])
        self.warehouse_list.selectionModel().selectionChanged.connect(self.on_warehouse_selected)
        left_panel.addWidget(self.warehouse_list)
        
        # Warehouse Buttons
        warehouse_buttons = QHBoxLayout()
        self.add_warehouse_btn = QPushButton("إضافة مخزن")
        self.add_warehouse_btn.clicked.connect(self.add_warehouse)
        self.edit_warehouse_btn = QPushButton("تعديل المخزن")
        self.edit_warehouse_btn.clicked.connect(self.edit_warehouse)
        self.delete_warehouse_btn = QPushButton("حذف المخزن")
        self.delete_warehouse_btn.clicked.connect(self.delete_warehouse)
        
        warehouse_buttons.addWidget(self.add_warehouse_btn)
        warehouse_buttons.addWidget(self.edit_warehouse_btn)
        warehouse_buttons.addWidget(self.delete_warehouse_btn)
        left_panel.addLayout(warehouse_buttons)
        
        # Right side - Warehouse Details and Products
        right_panel = QVBoxLayout()
        
        # Warehouse Info
        info_group = QVBoxLayout()
        self.location_label = QLabel("الموقع: ")
        self.contact_label = QLabel("معلومات الاتصال: ")
        info_group.addWidget(self.location_label)
        info_group.addWidget(self.contact_label)
        right_panel.addLayout(info_group)
        
        # Products in Warehouse
        products_label = QLabel("المنتجات في المخزن:")
        right_panel.addWidget(products_label)
        
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["رقم المنتج", "اسم المنتج", "الكمية"])
        right_panel.addWidget(self.products_table)
        
        # Add to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        layout.addWidget(splitter)

        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #1c2841;
            }
            QLabel {
                color: #c5a572;
                font-size: 14px;
            }
            QTableWidget {
                background-color: #0a1128;
                color: #c5a572;
                border: 1px solid #c5a572;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #0a1128;
                color: #c5a572;
                padding: 5px;
                border: 1px solid #c5a572;
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

    def load_warehouses(self):
        warehouses = self.db_manager.get_warehouses()
        self.warehouse_list.setRowCount(len(warehouses))
        for row, warehouse in enumerate(warehouses):
            self.warehouse_list.setItem(row, 0, QTableWidgetItem(str(warehouse[0])))
            self.warehouse_list.setItem(row, 1, QTableWidgetItem(warehouse[1]))
        self.warehouse_list.resizeColumnsToContents()

    def on_warehouse_selected(self):
        current_row = self.warehouse_list.currentRow()
        if current_row < 0:
            return

        warehouse_id = int(self.warehouse_list.item(current_row, 0).text())
        warehouse = self.db_manager.get_warehouse_details(warehouse_id)
        if warehouse:
            self.location_label.setText(f"الموقع: {warehouse[2]}")
            self.contact_label.setText(f"معلومات الاتصال: {warehouse[3]}")
            
            # Load products
            products = self.db_manager.get_warehouse_products(warehouse_id)
            self.products_table.setRowCount(len(products))
            for row, product in enumerate(products):
                self.products_table.setItem(row, 0, QTableWidgetItem(str(product[0])))
                self.products_table.setItem(row, 1, QTableWidgetItem(product[1]))
                self.products_table.setItem(row, 2, QTableWidgetItem(str(product[2])))
            self.products_table.resizeColumnsToContents()

    def add_warehouse(self):
        dialog = AddEditWarehouseDialog(self, self.db_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.add_warehouse(data['name'], data['location'], data['contact_details']):
                self.load_warehouses()
                QMessageBox.information(self, "نجاح", "تم إضافة المخزن بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة المخزن")

    def edit_warehouse(self):
        current_row = self.warehouse_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مخزن للتعديل")
            return

        warehouse_id = int(self.warehouse_list.item(current_row, 0).text())
        warehouse = self.db_manager.get_warehouse_details(warehouse_id)
        
        dialog = AddEditWarehouseDialog(self, self.db_manager, warehouse)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if self.db_manager.update_warehouse(
                warehouse_id, data['name'], data['location'], data['contact_details']
            ):
                self.load_warehouses()
                QMessageBox.information(self, "نجاح", "تم تحديث بيانات المخزن بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تحديث بيانات المخزن")

    def delete_warehouse(self):
        current_row = self.warehouse_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مخزن للحذف")
            return

        warehouse_id = int(self.warehouse_list.item(current_row, 0).text())
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا المخزن؟\nلا يمكن حذف المخزن إذا كان يحتوي على منتجات.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_warehouse(warehouse_id):
                self.load_warehouses()
                QMessageBox.information(self, "نجاح", "تم حذف المخزن بنجاح")
            else:
                QMessageBox.warning(
                    self, "خطأ",
                    "لا يمكن حذف المخزن لأنه يحتوي على منتجات.\nقم بنقل المنتجات إلى مخزن آخر أولاً."
                )

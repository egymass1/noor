import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QStackedWidget, QLineEdit, 
                           QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QProgressBar,
                           QDialog, QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor, QFont
from suppliers_ui import SuppliersWidget
from products_ui import ProductsWidget
from sales_ui import SalesWindow as NewSaleWidget
import sqlite3

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - نور الإسلام")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set fixed size to match login window
        screen_size = QApplication.primaryScreen().size()
        target_width = int(screen_size.width() * 0.35)  # 35% of screen width
        target_height = int(target_width * 1.2)  # Slightly taller than wide
        self.setFixedSize(target_width, target_height)
        
        self.setup_ui()
        self.center_on_screen()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Create main container with gradient background
        main_container = QFrame(self)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 17, 40, 0.95),
                    stop:1 rgba(28, 40, 65, 0.95));
                border-radius: 20px;
                border: 2px solid #c5a572;
            }
        """)
        
        # Add glass effect shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(197, 165, 114, 90))  # Gold shadow
        main_container.setGraphicsEffect(shadow)
        
        # Create layout for main container with proper spacing
        container_layout = QVBoxLayout(main_container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(30, 40, 30, 40)
        
        # Add logo at the top
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/noor_alislam.png")
        logo_size = int(self.width() * 0.35)  # 35% of window width
        scaled_pixmap = logo_pixmap.scaled(
            logo_size, logo_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(logo_label)
        
        # Add title with elegant styling
        title_label = QLabel("نور الإسلام")
        title_label.setStyleSheet("""
            QLabel {
                color: #c5a572;
                font-size: 36px;
                font-weight: bold;
                font-family: Arial;
                margin: 10px 0;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Add spacer
        container_layout.addSpacing(20)
        
        # Add progress bar with golden gradient
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)  # Thinner progress bar
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: rgba(10, 17, 40, 0.6);
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c5a572,
                    stop:1 #d4af37);
                border-radius: 4px;
            }
        """)
        self.progress_bar.setTextVisible(False)
        container_layout.addWidget(self.progress_bar)
        
        # Add loading text
        self.loading_label = QLabel("جاري تحميل النظام...")
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #c5a572;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.loading_label)
        
        # Add stretches for better vertical alignment
        container_layout.addStretch()
        
        # Add subtitle at the bottom
        subtitle_label = QLabel("عالم من الجمال")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #c5a572;
                font-size: 16px;
                font-style: italic;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(subtitle_label)
        
        # Add main container to main layout
        layout.addWidget(main_container)
        
        # Setup progress animation
        self.progress_counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

    def update_progress(self):
        self.progress_counter += 1
        self.progress_bar.setValue(self.progress_counter)
        
        if self.progress_counter >= 100:
            self.timer.stop()
            self.loading_label.setText("اكتمل التحميل")
            QTimer.singleShot(500, self.show_login_window)

    def show_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('تسجيل الدخول - نور الإسلام')
        self.setFixedSize(400, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1128;  /* Very Dark Navy */
            }
        """)
        
        # Create background label with logo
        background_label = QLabel(self)
        background_pixmap = QPixmap("assets/noor_alislam.png")
        background_label.setFixedSize(self.size())
        background_label.setPixmap(background_pixmap.scaled(
            self.width(),
            self.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        background_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)
        background_label.lower()
        
        # Create main frame with transparent background
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 40, 65, 0.85);  /* More transparent Navy Blue */
                border-radius: 15px;
                border: 2px solid #c5a572;  /* Elegant Gold */
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 90))
        main_frame.setGraphicsEffect(shadow)
        
        # Create layout for main frame
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(25)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        
        # Add title text
        title_label = QLabel("نور الإسلام")
        title_label.setStyleSheet("""
            QLabel {
                color: #c5a572;  /* Elegant Gold */
                font-size: 36px;
                font-weight: bold;
                font-family: Arial;
                margin-bottom: 30px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Add username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                background-color: rgba(35, 49, 72, 0.95);  /* Semi-transparent Navy */
                border: 1.5px solid #c5a572;  /* Elegant Gold */
                border-radius: 8px;
                font-size: 16px;
                color: #ffffff;
                margin: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #d4af37;  /* Brighter Gold */
                background-color: rgba(44, 62, 80, 0.95);
            }
            QLineEdit::placeholder {
                color: #aaaaaa;
            }
        """)
        self.username_input.returnPressed.connect(self.login)
        frame_layout.addWidget(self.username_input)
        
        # Add password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                background-color: rgba(35, 49, 72, 0.95);  /* Semi-transparent Navy */
                border: 1.5px solid #c5a572;  /* Elegant Gold */
                border-radius: 8px;
                font-size: 16px;
                color: #ffffff;
                margin: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #d4af37;  /* Brighter Gold */
                background-color: rgba(44, 62, 80, 0.95);
            }
            QLineEdit::placeholder {
                color: #aaaaaa;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        frame_layout.addWidget(self.password_input)
        
        # Add login button
        login_button = QPushButton("تسجيل الدخول")
        login_button.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #c5a572;  /* Elegant Gold */
                color: #1c2841;  /* Rich Navy Blue */
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                min-height: 45px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #d4af37;  /* Brighter Gold */
            }
            QPushButton:pressed {
                background-color: #b8860b;  /* Darker Gold */
            }
        """)
        login_button.clicked.connect(self.login)
        frame_layout.addWidget(login_button)

        # Add keyboard button at the bottom right
        keyboard_button = QPushButton()
        keyboard_button.setFixedSize(50, 50)  # Increased button size
        
        # Create and set keyboard icon
        keyboard_icon = QIcon("assets/keyboard.png")
        keyboard_button.setIcon(keyboard_icon)
        keyboard_button.setIconSize(QSize(32, 32))  # Increased icon size
        
        keyboard_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 49, 72, 0.95);
                border: 1.5px solid #c5a572;
                border-radius: 25px;  /* Adjusted for larger size */
                margin: 10px;
            }
            QPushButton:hover {
                background-color: rgba(44, 62, 80, 0.95);
                border-color: #d4af37;
            }
        """)
        keyboard_button.clicked.connect(self.show_keyboard)
        
        # Create a container for the keyboard button with transparent background
        button_container = QWidget()
        button_container.setFixedHeight(70)  # Increased container height
        button_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(keyboard_button)
        button_layout.setContentsMargins(0, 0, 15, 15)  # Adjusted margins
        
        # Add to main layout with margins
        layout.addWidget(main_frame)
        layout.addWidget(button_container)
        layout.setContentsMargins(30, 30, 30, 30)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update background logo size when window is resized
        for child in self.children():
            if isinstance(child, QLabel) and not child.text():
                child.setFixedSize(self.size())
                child.setPixmap(QPixmap("assets/noor_alislam.png").scaled(
                    self.width(),
                    self.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم المستخدم وكلمة المرور")
            return
        
        try:
            conn = sqlite3.connect('noor_alislam.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            
            if user:
                self.dashboard = Dashboard()
                self.dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في قاعدة البيانات: {str(e)}")

    def show_keyboard(self):
        try:
            import os
            keyboard_path = os.path.join(os.environ['WINDIR'], 'System32', 'osk.exe')
            if os.path.exists(keyboard_path):
                os.startfile(keyboard_path)
            else:
                print(f"Keyboard not found at: {keyboard_path}")
        except Exception as e:
            print(f"Error launching keyboard: {str(e)}")

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("عن EGYmass")
        self.setFixedSize(400, 300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1128,
                    stop:1 #1c2841);
            }
            QLabel {
                color: #c5a572;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/egymass_logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Company Info
        info_text = """
        <div style='text-align: center; color: #c5a572;'>
            <h2>EGYmass</h2>
            <p>شركة برمجيات متخصصة في تطوير حلول الأعمال المتكاملة</p>
            <p>رقم الهاتف: 201103317161+</p>
            <p><a href='http://egymass.com' style='color: #d4af37;'>egymass.com</a></p>
        </div>
        """
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        # Close button
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #c5a572;
                color: #1c2841;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d4af37;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نور الإسلام - لوحة التحكم")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Set RTL layout
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1128,
                    stop:1 #1c2841);
            }
        """)
        
        # Set window size to 80% of screen size
        screen = QApplication.primaryScreen().size()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        
        # Center window
        self.center_window()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 5)  # تقليل الهوامش خاصة من الأسفل
        main_layout.setSpacing(5)  # تقليل المسافة بين العناصر
        
        # Create top bar
        top_bar = QFrame()
        top_bar.setFixedHeight(50)  # تحديد ارتفاع ثابت للشريط العلوي
        top_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 40, 65, 0.95);
                border-radius: 10px;
                border: 1px solid #c5a572;
            }
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setSpacing(15)
        top_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add logo to top bar
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/noor_alislam.png")
        logo_label.setPixmap(logo_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(logo_label)
        
        # Add menu buttons
        menu_buttons = [
            ("عملية جديدة", "🛍️", 3),
            ("المنتجات", "📦", 2),
            ("العملاء", "👥", 0),
            ("الموردين", "🏭", 1),
            ("التقارير والإحصائيات", "📊", 0),
            ("الإعدادات", "⚙️", 0)
        ]
        
        self.button_group = []
        for i, (text, icon, page_index) in enumerate(menu_buttons):
            btn = QPushButton(f"{text} {icon}")
            btn.setFixedHeight(35)
            btn.setCheckable(True)
            self.button_group.append(btn)
            
            # Set button style
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #c5a572;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    text-align: center;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(197, 165, 114, 0.1);
                }
                QPushButton:checked {
                    background-color: #c5a572;
                    color: #0a1128;
                }
            """)
            
            if text == "عملية جديدة":
                btn.setStyleSheet(btn.styleSheet() + """
                    QPushButton {
                        font-weight: bold;
                    }
                """)
            
            # Connect button click to page change
            btn.clicked.connect(lambda checked, btn=btn, index=page_index: self.change_page(btn, index))
            
            top_layout.addWidget(btn)
        
        # Add spacer
        top_layout.addStretch()
        
        # Add user info and logout button
        user_frame = QFrame()
        user_layout = QHBoxLayout(user_frame)
        user_layout.setSpacing(15)
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("color: #c5a572; font-size: 20px;")
        user_layout.addWidget(user_icon)
        
        username_label = QLabel("المستخدم")
        username_label.setStyleSheet("color: #c5a572; font-size: 16px;")
        user_layout.addWidget(username_label)
        
        logout_btn = QPushButton("تسجيل خروج")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #c5a572;
                color: #1c2841;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d4af37;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        user_layout.addWidget(logout_btn)
        
        top_layout.addWidget(user_frame)
        main_layout.addWidget(top_bar)
        
        # Create stacked widget for main content
        self.stacked_widget = QStackedWidget()

        # Create and add pages
        self.welcome_page = QWidget()
        self.suppliers_page = SuppliersWidget()
        self.products_page = ProductsWidget()
        self.sales_page = NewSaleWidget()
        
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_label = QLabel("مرحباً بك في نظام نور الإسلام")
        welcome_label.setStyleSheet("""
            QLabel {
                color: #c5a572;
                font-size: 24px;
                font-weight: bold;
                margin: 20px;
            }
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_label)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.welcome_page)  # index 0
        self.stacked_widget.addWidget(self.suppliers_page)  # index 1
        self.stacked_widget.addWidget(self.products_page)  # index 2
        self.stacked_widget.addWidget(self.sales_page)  # index 3

        # Create main content area with full width
        content_area = QFrame()
        content_area.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 40, 65, 0.95);
                border-radius: 10px;
                border: 1px solid #c5a572;
            }
        """)
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(5, 5, 5, 5)  # تقليل الهوامش الداخلية
        content_layout.setSpacing(0)  # إزالة المسافات بين العناصر الداخلية
        content_layout.addWidget(self.stacked_widget)
        
        # Set size policy to make content area expand
        content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(content_area, 1)  # إضافة stretch factor لجعل المنطقة تأخذ المساحة المتبقية
        
        # Add EGYmass logo at bottom left
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(45)  # تقليل ارتفاع الشريط السفلي
        bottom_bar.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(5, 0, 5, 5)  # تقليل الهوامش
        
        # Add keyboard button at bottom right
        keyboard_btn = QPushButton()
        keyboard_btn.setIcon(QIcon("assets/keyboard.png"))
        keyboard_btn.setIconSize(QSize(20, 20))  # تصغير حجم الأيقونة
        keyboard_btn.setFixedSize(35, 35)  # تصغير حجم الزر
        keyboard_btn.setToolTip("لوحة المفاتيح")
        keyboard_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(28, 40, 65, 0.95);
                border: 1px solid #c5a572;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c5a572;
            }
        """)
        keyboard_btn.clicked.connect(self.show_keyboard)
        bottom_layout.addWidget(keyboard_btn)
        
        egymass_logo = QPushButton()
        egymass_logo.setFixedSize(90, 35)  # تصغير حجم الشعار
        egymass_logo.setCursor(Qt.CursorShape.PointingHandCursor)
        egymass_logo.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
        """)
        logo_pixmap = QPixmap("assets/egymass_logo.png")
        egymass_logo.setIcon(QIcon(logo_pixmap))
        egymass_logo.setIconSize(QSize(90, 35))
        egymass_logo.clicked.connect(self.show_about_dialog)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(egymass_logo)
        main_layout.addWidget(bottom_bar)

        # Add refresh button
        refresh_btn = QPushButton()
        refresh_btn.setIcon(QIcon("assets/refresh.png"))
        refresh_btn.setToolTip("تحديث البيانات")
        refresh_btn.clicked.connect(self.refresh_all_data)
        top_layout.addWidget(refresh_btn)

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def logout(self):
        login_window = LoginWindow()
        login_window.show()
        self.close()

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def change_page(self, clicked_button, index):
        self.stacked_widget.setCurrentIndex(index)
        # Update button states
        for btn in self.button_group:
            if btn != clicked_button:
                btn.setChecked(False)
        clicked_button.setChecked(True)

    def refresh_all_data(self):
        """تحديث جميع البيانات في كل الواجهات"""
        try:
            # تحديث واجهة المبيعات
            if hasattr(self, 'sales_page'):
                self.sales_page.refresh_data()
            
            # تحديث واجهة المنتجات
            if hasattr(self, 'products_page'):
                self.products_page.load_products()
            
            # تحديث واجهة الموردين
            if hasattr(self, 'suppliers_page'):
                self.suppliers_page.load_suppliers()
            
            # عرض رسالة نجاح
            QMessageBox.information(self, "نجاح", "تم تحديث البيانات بنجاح")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث البيانات: {str(e)}")

    def show_keyboard(self):
        """إظهار لوحة المفاتيح على الشاشة"""
        try:
            import subprocess
            subprocess.Popen('osk.exe')
        except Exception as e:
            QMessageBox.warning(self, "خطأ", "لم نتمكن من فتح لوحة المفاتيح")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نور الإسلام - نظام إدارة المبيعات")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        header = QLabel("نور الإسلام")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create main menu buttons
        self.create_menu_buttons(layout)
        
    def create_menu_buttons(self, layout):
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create main menu buttons
        menu_items = [
            "إدارة المنتجات",
            "إدارة الموردين",
            "إدارة المخازن",
            "إدارة العملاء",
            "إدارة الطلبات",
            "التقارير",
            "إعدادات النظام"
        ]
        
        for item in menu_items:
            button = QPushButton(item)
            button.setStyleSheet("""
                QPushButton {
                    padding: 15px;
                    font-size: 16px;
                    background-color: #1c2841;  /* Rich Navy Blue */
                    color: #c5a572;  /* Elegant Gold */
                    border: 1.5px solid #c5a572;
                    border-radius: 8px;
                    margin: 5px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #233148;  /* Slightly Lighter Navy */
                    border-color: #d4af37;  /* Brighter Gold */
                    color: #d4af37;
                }
                QPushButton:pressed {
                    background-color: #0f1c2d;  /* Darker Navy */
                }
            """)
            buttons_layout.addWidget(button)
        
        layout.addLayout(buttons_layout)

def main():
    # Initialize database
    # initialize_database()
    
    # Create and run application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Create login window
    # login = LoginWindow()
    
    # Timer to simulate loading and switch to login window
    # def switch_to_login():
    #     splash.close()
    #     login.show()
    
    # QTimer.singleShot(3000, switch_to_login)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

from PySide6.QtWidgets import*
from PySide6.QtGui import * 
from PySide6.QtCore import *
from PySide6.QtCharts import*
from openpyxl import*
from PySide6.QtUiTools import QUiLoader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import*
from reportlab.lib.styles import*
from reportlab.lib.enums import*
from reportlab.lib import colors
from reportlab.lib.units import*
from textwrap import wrap
import mysql.connector
import os
from mysql.connector import Error
import imaplib
import email
import bcrypt
import sys
import re
import smtplib
import qrcode
import io
import random
import pandas as pd
import time
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from datetime import datetime 
from email.mime.multipart import MIMEMultipart
from ICONS import Icons
from notification_manager import NotificationManager
from clock import AnalogClock
from excel_handler import save_table_to_excel


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Login_Register(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.login_ui = loader.load(resource_path("ui/login.ui"), self)
        self.register_ui = loader.load(resource_path("ui/register.ui"), self)
        self.reset_password_ui = loader.load(resource_path("ui/reset_password.ui"), self)

        self.generated_otp = None
        self.otp_valid = False
        self.remaining_time = 60
        self.countdown_timer = QTimer()

        self.notification_manager = NotificationManager()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.login_ui)    
        self.stacked_widget.addWidget(self.register_ui) 
        self.stacked_widget.addWidget(self.reset_password_ui)

        self.setCentralWidget(self.stacked_widget)

        self.login_stacked = self.login_ui.findChild(QStackedWidget, "stackedWidget")
        self.loginbtn = self.login_ui.findChild(QPushButton, "login")
        self.qrcode_login_btn = self.login_ui.findChild(QPushButton, "qrcode_login")
        self.Qr_login = self.login_ui.findChild(QLineEdit, "Qr_login")
        self.userid_field = self.login_ui.findChild(QLineEdit, "User_ID")
        self.pass_field = self.login_ui.findChild(QLineEdit, "Password")
        self.forgot_password_btn = self.login_ui.findChild(QPushButton, "ForgotPassword")  
        self.guardian_login_btn = self.login_ui.findChild(QPushButton, "guardian_login")  
        self.studentid_field = self.login_ui.findChild(QLineEdit, "studentID")
        self.birthdate_edit = self.login_ui.findChild(QDateEdit, "birthdate")
        self.password_field = self.login_ui.findChild(QLineEdit, "l_password")

        self.loginbtn.clicked.connect(self.handle_login)

        def trigger_login_if_valid():
            current_index = self.login_stacked.currentIndex()
            if current_index in [0, 1]:
                self.loginbtn.click()

        enter_shortcut_login = QShortcut(QKeySequence("Return"), self.login_ui)
        enter_shortcut_login.activated.connect(trigger_login_if_valid)

        numpad_enter_shortcut_login = QShortcut(QKeySequence("Enter"), self.login_ui)
        numpad_enter_shortcut_login.activated.connect(trigger_login_if_valid)

        self.firstname = self.register_ui.findChild(QLineEdit, "firstname")
        self.middlename = self.register_ui.findChild(QLineEdit, "middlename")
        self.lastname = self.register_ui.findChild(QLineEdit, "lastname")
        self.birthdate = self.register_ui.findChild(QDateEdit, "birthdate")
        self.choosesex_btn = self.register_ui.findChild(QComboBox, "choosesex")
        self.suffix_btn = self.register_ui.findChild(QComboBox, "suffix")
        self.chooserole_btn = self.register_ui.findChild(QComboBox, "chooserole")
        self.dept = self.register_ui.findChild(QLabel, "department")
        self.choosedept_btn = self.register_ui.findChild(QComboBox, "choosedept")
        self.emailadd = self.register_ui.findChild(QLineEdit, "emailaddress")
        self.r_password = self.register_ui.findChild(QLineEdit, "r_password")
        self.r_confirmpassword = self.register_ui.findChild(QLineEdit, "r_confirmpassword")
        self.submit_btn = self.register_ui.findChild(QPushButton, "submit_btn")

        enter_shortcut_register = QShortcut(QKeySequence("Return"), self.register_ui)
        enter_shortcut_register.activated.connect(self.submit_btn.click)
        numpad_enter_shortcut_register = QShortcut(QKeySequence("Enter"), self.register_ui)
        numpad_enter_shortcut_register.activated.connect(self.submit_btn.click)

        self.enforce_uppercase()
        self.chooserole_btn.currentIndexChanged.connect(self.update_department_visibility)
        self.validate_email()
        self.validate_registration()

        self.enter_email = self.reset_password_ui.findChild(QLineEdit, "Enter_email")
        self.cancel_btn = self.reset_password_ui.findChild(QPushButton, "cancel")
        self.send_otp_btn = self.reset_password_ui.findChild(QPushButton, "send_OTP")

        self.add_eye_icon(self.pass_field)
        self.add_eye_icon(self.password_field)
        self.add_eye_icon(self.r_password)
        self.add_eye_icon(self.r_confirmpassword)

        self.setup_birthdate_format()
        self.set_background()
        self.setup_connections()
        self.setup_qr_listener()

        self.userid_field.installEventFilter(self)
        self.pass_field.installEventFilter(self)

    
    def enforce_uppercase(self):
        self.firstname.textChanged.connect(lambda: self.firstname.setText(self.firstname.text().upper()))
        self.middlename.textChanged.connect(lambda: self.middlename.setText(self.middlename.text().upper()))
        self.lastname.textChanged.connect(lambda: self.lastname.setText(self.lastname.text().upper()))
        self.userid_field.textChanged.connect(lambda: self.userid_field.setText(self.userid_field.text().upper()))
        self.studentid_field.textChanged.connect(lambda: self.studentid_field.setText(self.studentid_field.text().upper()))

    def validate_email(self):
        valid_domains = (r"@gsfe.tupcavite.edu\.ph$")

        def check_email():
            email = self.emailadd.text().strip()

            if email and not any(re.search(domain, email) for domain in valid_domains):
                QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address (e.g., example@gsfe.tupcavite.edu.ph).")

        self.emailadd.editingFinished.connect(check_email)

    def update_department_visibility(self):
        selected_role = self.chooserole_btn.currentText()

        if selected_role == "Student":
            self.dept.hide()
            self.choosedept_btn.hide()
        elif selected_role == "Faculty":
            self.dept.show()
            self.choosedept_btn.show()

    def validate_registration(self):
        def check_fields():
            empty_fields = []  
            invalid_email = False
            password_mismatch = False

            fields = {
                "First Name": self.firstname,
                "Last Name": self.lastname,
                "Birthdate": self.birthdate,
                "Sex": self.choosesex_btn,
                "Role": self.chooserole_btn,
                "Email Address": self.emailadd,
                "Password": self.r_password,
                "Confirm Password": self.r_confirmpassword
            }

            if self.chooserole_btn.currentText() == "Faculty":
                fields["Department"] = self.choosedept_btn

            for label, field in fields.items():
                if isinstance(field, QLineEdit) and field.text().strip() == "":
                    empty_fields.append(label)
                elif isinstance(field, QComboBox) and field.currentIndex() == 0:  
                    empty_fields.append(label)
                elif isinstance(field, QDateEdit) and not field.date().isValid():
                    empty_fields.append(label)

            valid_domains = ["@gsfe.tupcavite.edu.ph"]
            email = self.emailadd.text().strip()
            if not any(email.endswith(domain) for domain in valid_domains):
                invalid_email = True

            password = self.r_password.text().strip()
            confirm_password = self.r_confirmpassword.text().strip()

            if password != confirm_password:
                password_mismatch = True

            # Check if email already exists in the database
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="TUPCcoet@23!",
                    database="axis"
                )

                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SELECT COUNT(*) FROM user_account WHERE emailaddress = %s", (email,))
                    email_count = cursor.fetchone()[0]

                    if email_count > 0:
                        QMessageBox.warning(self, "Email Error", "The email address is already in use. Please enter another email.")
                        return  # Exit the function if email is already in use

            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred while checking the email: {e}")
            
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

            # Handle the validation errors
            if empty_fields:
                QMessageBox.warning(self, "Incomplete Form", f"Please fill in the following fields:\n\n- " + "\n- ".join(empty_fields))
            elif invalid_email:
                QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address (e.g., example@gsfe.tupcavite.edu.ph).")
            elif len(password) < 8 or not re.search(r"\d", password):
                QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters long and contain at least one number.")
            elif password_mismatch:
                QMessageBox.warning(self, "Password Mismatch", "Passwords do not match. Please try again.")
            else:
                if self.show_privacy_dialog():
                    self.save_to_database()

        self.submit_btn.clicked.connect(check_fields)

    
    def show_privacy_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Data Privacy Agreement")
        msg.setText(
            "By continuing, you agree to the collection and use of your personal information "
            "in accordance with the Data Privacy Act of 2012. Your data will be stored securely "
            "and used solely for academic and system-related purposes."
        )
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        checkbox = QCheckBox("I agree to the Data Privacy Act")
        msg.setCheckBox(checkbox)

        result = msg.exec()

        if result == QMessageBox.Ok and checkbox.isChecked():
            return True
        elif result == QMessageBox.Ok and not checkbox.isChecked():
            QMessageBox.warning(self, "Agreement Required", "You must agree to the Data Privacy Act to proceed.")
            return False
        return False


    def save_to_database(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor()

                insert_query = """
                    INSERT INTO user_account (
                        user_id,
                        first_name,
                        middle_name,
                        last_name,
                        suffix,
                        birthdate,
                        sex,
                        role,
                        department,
                        emailaddress,
                        password,
                        qr_token,
                        status,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                role = self.chooserole_btn.currentText()
                department = self.choosedept_btn.currentText() if role == "Faculty" else None

                suffix = self.suffix_btn.currentText().strip()
                suffix = suffix if suffix and suffix != "Select Suffix" else None

                middle_name = self.middlename.text().strip()
                middle_name = middle_name if middle_name else None

                user_id = None
                qr_token = None
                status = 'pending'
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                first_name = self.firstname.text().strip()
                last_name = self.lastname.text().strip()
                email = self.emailadd.text().strip()

                plain_password = self.r_password.text().strip()
                hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                user_data = (
                    user_id,
                    first_name,
                    middle_name,
                    last_name,
                    suffix,
                    self.birthdate.date().toString("yyyy-MM-dd"),
                    self.choosesex_btn.currentText(),
                    role,
                    department,
                    email,
                    hashed_password,
                    qr_token,
                    status,
                    created_at
                )

                cursor.execute(insert_query, user_data)
                connection.commit()

                notif_manager = NotificationManager()
                notif_manager.send_notification(
                    sender_id=None,
                    recipient_role="Admin",
                    recipient_id=None,
                    message=f"📋 New user registration submitted for approval:\n"
                            f"Name: {first_name} {last_name}\n"
                            f"Role: {role}\n"
                            f"Please review and approve/reject."
                )

                QMessageBox.information(
                    self,
                    "Registration Successful",
                    "Successfully Registered!\n\nPlease wait for approval. Once your account is approved, you will receive your User ID and QR Code via your registered email."
                )
                self.show_login()

        except Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def setup_connections(self):
        login_btn = self.login_ui.findChild(QPushButton, "register_btn")  
        register_btn = self.register_ui.findChild(QPushButton, "login")
        back_to_login = self.login_ui.findChild(QPushButton, "back_to_login")

        if login_btn:
            login_btn.clicked.connect(self.show_register)

        if register_btn:
            register_btn.clicked.connect(self.show_login)

        if self.guardian_login_btn and self.login_stacked:
            self.guardian_login_btn.clicked.connect(self.toggle_login_mode)

        if self.qrcode_login_btn and self.login_stacked:
            self.qrcode_login_btn.clicked.connect(self.toggle_login_mode)

        if back_to_login and self.login_stacked:
            back_to_login.clicked.connect(self.show_student_login)
        
        if self.forgot_password_btn:
            self.forgot_password_btn.clicked.connect(self.show_reset_password_dialog)
        
    
    def set_background(self):
        bg_image_path = "UI/Resources/green_bg.png"  
        style = f"""
        QMainWindow {{
            background-image: url("{bg_image_path}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }}
        """
        self.login_ui.setStyleSheet(style)
        self.register_ui.setStyleSheet(style)

    def add_eye_icon(self, password_field):
        if password_field:
            show_password_action = QAction(self)
            show_password_action.setIcon(QIcon(r"UI/Resources/hidden.png"))
            
            password_field.addAction(show_password_action, QLineEdit.TrailingPosition)
            password_field.setEchoMode(QLineEdit.Password)
            
            show_password_action.triggered.connect(
                lambda checked=False, field=password_field, action=show_password_action: 
                self.toggle_password_visibility(field, action))

    def toggle_password_visibility(self, password_field, show_password_action):
        if password_field.echoMode() == QLineEdit.Password:
            password_field.setEchoMode(QLineEdit.Normal)
            show_password_action.setIcon(QIcon(r"UI/Resources/show.png"))
        else:
            password_field.setEchoMode(QLineEdit.Password)
            show_password_action.setIcon(QIcon(r"UI/Resources/hidden.png"))


    
    def show_blurred_overlay(self):
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        self.overlay.setGeometry(self.rect())
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.show()

    def hide_blurred_overlay(self):
        if hasattr(self, "overlay"):
            self.overlay.deleteLater()
            del self.overlay
            
    def get_db_connection(self):
        return mysql.connector.connect(
            host="localhost",  
            user="root",  
            password="TUPCcoet@23!",  
            database="axis"  
        )

    def send_otp_email(self, user_email, otp):
        try:
            sender_email = "axistupcems@gmail.com"
            password = "ajiu rivz ttgw lzka"

            message = MIMEMultipart("alternative")
            message["From"] = sender_email
            message["To"] = user_email
            message["Subject"] = "Password Reset Request"

            html_body = f"""\
            <html>
                <body>
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Please use the following One-Time Password (OTP) to proceed with the password reset process:</p>
                    <p style="font-size: 24px; color: red; font-weight: bold;">{otp}</p>
                    <p>This OTP is valid for <strong>1 minute only</strong>.</p>
                    <p>If you did not request this change, please ignore this email or contact support immediately.</p>
                    <p>Thank you,<br>Axis Support Team</p>
                </body>
            </html>
            """
            message.attach(MIMEText(html_body, "html"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, user_email, message.as_string())
            server.quit()

            print("OTP email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")


    def generate_otp(self):
        return str(random.randint(100000, 999999))  

    def send_otp_for_password_reset(self):
        user_id = self.enter_id.text().strip()
        email = self.enter_email.text().strip()

        if not user_id or not email:
            QMessageBox.warning(self.reset_dialog, "Error", "User ID and Email cannot be empty.")
            return

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM user_account WHERE user_id = %s AND emailaddress = %s", (user_id, email))
            user = cursor.fetchone()

            if user is None:
                QMessageBox.warning(self.reset_dialog, "Error", "User ID or Email does not match any account.")
                return

            # Only show the loading dialog now that user is verified
            loading_dialog = QProgressDialog("Sending OTP email...", None, 0, 0, self.reset_dialog)
            loading_dialog.setWindowTitle("Please Wait")
            loading_dialog.setWindowModality(Qt.ApplicationModal)
            loading_dialog.setCancelButton(None)
            loading_dialog.setMinimumDuration(0)
            loading_dialog.show()
            QApplication.processEvents()

            otp = self.generate_otp()
            self.generated_otp = otp
            self.send_otp_email(email, otp)
            self.start_otp_timer()

            self.reset_stacked_widget.setCurrentIndex(1)

            loading_dialog.cancel()
            QMessageBox.information(self.reset_dialog, "OTP Sent", "An OTP has been sent to your email.")

            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            QMessageBox.warning(self.reset_dialog, "Error", "An error occurred while checking your account.")

    def show_reset_password_dialog(self):
        loader = QUiLoader()
        reset_password_ui = loader.load(resource_path("UI/reset_password.ui"), self)

        self.reset_dialog = QDialog(self)
        self.reset_dialog.setWindowTitle("Reset Password")
        self.reset_dialog.setModal(True)
        self.reset_dialog.setLayout(QVBoxLayout())
        self.reset_dialog.layout().addWidget(reset_password_ui)

        self.reset_stacked_widget = reset_password_ui.findChild(QStackedWidget, "reset_stackedWidget")

        self.show_blurred_overlay()

        self.enter_email = reset_password_ui.findChild(QLineEdit, "Enter_email")
        self.enter_id = reset_password_ui.findChild(QLineEdit, "enter_ID")
        self.enter_id.textChanged.connect(lambda text: self.enter_id.setText(text.upper()))
        self.enter_OTP = reset_password_ui.findChild(QLineEdit, "enter_OTP")
        self.otp_timer = reset_password_ui.findChild(QLabel, "otp_timer")  
        self.enter_new = reset_password_ui.findChild(QLineEdit, "enter_new")
        self.confirm_new = reset_password_ui.findChild(QLineEdit, "confirm_new")
        self.verify_btn = reset_password_ui.findChild(QPushButton, "verify")
        
        # This is the line you asked to confirm included
        self.resetpass_btn = reset_password_ui.findChild(QPushButton, "reset_pass") 
        
        self.resend_otp_btn = reset_password_ui.findChild(QPushButton, "resend_otp")
        self.cancel_btn2 = reset_password_ui.findChild(QPushButton, "cancel_2") 
        self.cancel_btn = reset_password_ui.findChild(QPushButton, "cancel") 
        self.send_otp_btn = reset_password_ui.findChild(QPushButton, "send_OTP")
        self.old_pass = reset_password_ui.findChild(QLabel, "old_pass")
        self.enter_old = reset_password_ui.findChild(QLineEdit, "enter_old")

        self.reset_dialog.finished.connect(self.hide_blurred_overlay)
        self.add_eye_icon(self.enter_new)
        self.add_eye_icon(self.confirm_new)

        if self.old_pass:
            self.old_pass.hide()

        if self.enter_old:
            self.enter_old.hide()

        if self.send_otp_btn:
            self.send_otp_btn.clicked.connect(self.send_otp_for_password_reset)

        # New combined shortcut handling for both buttons based on stacked widget index
        if self.send_otp_btn and self.verify_btn and self.resetpass_btn and self.reset_stacked_widget:
            def enter_pressed_trigger():
                idx = self.reset_stacked_widget.currentIndex()
                if idx == 0:
                    self.send_otp_btn.click()
                elif idx == 1:
                    self.verify_btn.click()
                elif idx == 2:
                    self.resetpass_btn.click()

            enter_shortcut_return = QShortcut(QKeySequence("Return"), reset_password_ui)
            enter_shortcut_return.activated.connect(enter_pressed_trigger)

            enter_shortcut_enter = QShortcut(QKeySequence("Enter"), reset_password_ui)
            enter_shortcut_enter.activated.connect(enter_pressed_trigger)

        if self.verify_btn:
            self.verify_btn.clicked.connect(self.verify_otp)
            self.verify_btn.clicked.connect(self.check_otp_input)

        if self.resend_otp_btn:
            self.resend_otp_btn.clicked.connect(self.resend_otp)

        if self.cancel_btn:
            self.cancel_btn.clicked.connect(self.close_reset_password_dialog)

        if self.cancel_btn2:
            self.cancel_btn2.clicked.connect(self.close_reset_password_dialog)

        if self.resetpass_btn:
            self.resetpass_btn.clicked.connect(self.verify_pass)

        self.reset_dialog.exec()

    def check_otp_input(self):
        if not self.enter_OTP.text().strip():
            QMessageBox.critical(self, "Error", "Please enter the OTP.")
        else:
            # Proceed with OTP verification
            print("OTP entered:", self.enter_OTP.text())

    def show_otp_page(self):
        user_id = self.enter_id.text().strip()
        email = self.enter_email.text().strip()

        if not user_id or not email:
            QMessageBox.warning(self.reset_dialog, "Error", "User ID and Email cannot be empty.")
            return  

        self.reset_stacked_widget.setCurrentIndex(1)

    def show_changepass_page(self):
        if self.reset_stacked_widget:
            self.reset_stacked_widget.setCurrentIndex(2)  

    def verify_otp(self):
        entered_otp = self.enter_OTP.text().strip()

        if not self.otp_valid:
            QMessageBox.warning(self.reset_dialog, "OTP Expired", "The OTP has expired. Please request a new one.")
            return

        if not re.fullmatch(r"\d{6}", entered_otp):
            QMessageBox.warning(self.reset_dialog, "Invalid OTP", "OTP must be a 6-digit number.")
            return

        if entered_otp == getattr(self, "generated_otp", None):
            QMessageBox.information(self.reset_dialog, "Success", "OTP Verified!")
            self.countdown_timer.stop()
            self.show_changepass_page()
        else:
            QMessageBox.warning(self.reset_dialog, "Error", "Incorrect OTP. Please try again.")

    def resend_otp(self):
        email = self.enter_email.text().strip()

        if not email:
            QMessageBox.warning(self.reset_dialog, "Error", "Email address cannot be empty.")
            return

        otp = self.generate_otp()
        self.generated_otp = otp
        self.send_otp_email(email, otp)
        self.start_otp_timer()

        QMessageBox.information(self.reset_dialog, "OTP Resent", "A new OTP has been sent to your email.")

    def verify_pass(self):
        enterednew_pass = self.enter_new.text().strip()
        enteredconfirm_pass = self.confirm_new.text().strip()

        if not enterednew_pass or not enteredconfirm_pass:  
            QMessageBox.warning(self.reset_dialog, "Error", "Both password fields must be filled. Please enter a valid password.")
            return

        if enterednew_pass != enteredconfirm_pass:
            QMessageBox.warning(self.reset_dialog, "Error", "Passwords do not match. Please enter the same password in both fields.")
            return
        
        if not self.is_strong_password(enterednew_pass):
            QMessageBox.warning(self.reset_dialog, "Error", "Password must be at least 8 characters long, contain both upper and lowercase letters, and atleast one number.")
            return

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            hashed_password = self.hash_password(enterednew_pass)

            cursor.execute("UPDATE user_account SET password = %s WHERE user_id = %s", (hashed_password, self.enter_id.text().strip()))
            connection.commit()

            QMessageBox.information(self.reset_dialog, "Success", "Password Changed Successfully!")

            self.reset_dialog.close()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            QMessageBox.warning(self.reset_dialog, "Error", "An error occurred while updating your password.")

    def is_strong_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):  
            return False
        if not re.search(r"[a-z]", password): 
            return False
        if not re.search(r"[0-9]", password):  
            return False
        return True


    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password
    
    def start_otp_timer(self):
            self.remaining_time = 60
            self.otp_valid = True
            self.otp_timer.setText(f"OTP valid for: {self.remaining_time} seconds")

            self.resend_otp_btn.setVisible(False)  # 🔴 Hide the resend button during countdown

            if hasattr(self, "countdown_timer") and self.countdown_timer.isActive():
                self.countdown_timer.stop()

            self.countdown_timer = QTimer()
            self.countdown_timer.timeout.connect(self.update_otp_timer)
            self.countdown_timer.start(1000)

    def update_otp_timer(self):
            self.remaining_time -= 1
            if self.remaining_time <= 0:
                self.countdown_timer.stop()
                self.otp_valid = False
                self.otp_timer.setText("OTP expired.")
                self.resend_otp_btn.setVisible(True)

                if self.reset_dialog.isVisible():  # ✅ Only show the message box if dialog is still open
                    QMessageBox.information(self.reset_dialog, "OTP Expired", "The OTP has expired. Please request a new one.")
            else:
                self.otp_timer.setText(f"OTP valid for: {self.remaining_time} seconds")


    def close_reset_password_dialog(self):
        if hasattr(self, 'reset_dialog') and self.reset_dialog:
            self.reset_dialog.close()

    def show_register(self):
        self.clear_inputs()
        self.stacked_widget.setCurrentIndex(1)

    def show_login(self):
        self.clear_inputs()
        self.stacked_widget.setCurrentIndex(0)
    
    def setup_birthdate_format(self):
        if self.birthdate_edit:
            self.birthdate_edit.setDisplayFormat("MM/dd/yyyy") 
            self.birthdate_edit.setDate(QDate(2000, 1, 1))

    def toggle_login_mode(self):
        dont_have_acc_label = self.login_ui.findChild(QLabel, "dont_have_acc")
        register_btn = self.login_ui.findChild(QPushButton, "register_btn")
        Qr_login = self.login_ui.findChild(QLineEdit, "Qr_login")

        current_index = self.login_stacked.currentIndex()
        sender = self.sender()

        if sender == self.qrcode_login_btn:
            if current_index in [0, 1]:  # From user or guardian login
                self.clear_inputs()
                self.login_stacked.setCurrentIndex(2)  # Switch to QR login
                self.qrcode_login_btn.setText("Log in as Faculty/Student")
                self.guardian_login_btn.setText("Log in as Parent/Guardian")
                if Qr_login:
                    Qr_login.setFocus()
                if self.forgot_password_btn:
                    self.forgot_password_btn.setVisible(False)
                if dont_have_acc_label:
                    dont_have_acc_label.setVisible(False)
                    register_btn.setVisible(False)
                if self.loginbtn:
                    self.loginbtn.setVisible(False)  # Hide login button for QR
            else:  # Back to default
                self.clear_inputs()
                self.login_stacked.setCurrentIndex(0)
                self.qrcode_login_btn.setText("Log in using QR")
                self.guardian_login_btn.setText("Log in as Parent/Guardian")
                if self.forgot_password_btn:
                    self.forgot_password_btn.setVisible(True)
                if dont_have_acc_label:
                    dont_have_acc_label.setVisible(True)
                    register_btn.setVisible(True)
                if self.loginbtn:
                    self.loginbtn.setVisible(True)  # Show for normal login

        elif sender == self.guardian_login_btn:
            if current_index in [0, 2]:  # From user or QR login
                self.clear_inputs()
                self.login_stacked.setCurrentIndex(1)  # Switch to guardian login
                self.guardian_login_btn.setText("Log in as Faculty/Student")
                self.qrcode_login_btn.setText("Log in using QR")
                if self.forgot_password_btn:
                    self.forgot_password_btn.setVisible(False)
                if dont_have_acc_label:
                    dont_have_acc_label.setVisible(False)
                    register_btn.setVisible(False)
                if self.loginbtn:
                    self.loginbtn.setVisible(True)
            else:  # Back to default
                self.clear_inputs()
                self.login_stacked.setCurrentIndex(0)
                self.guardian_login_btn.setText("Log in as Parent/Guardian")
                self.qrcode_login_btn.setText("Log in using QR")
                if self.forgot_password_btn:
                    self.forgot_password_btn.setVisible(True)
                if dont_have_acc_label:
                    dont_have_acc_label.setVisible(True)
                    register_btn.setVisible(True)
                if self.loginbtn:
                    self.loginbtn.setVisible(True)



    def clear_inputs(self):
        for widget in [self.login_ui, self.register_ui]:
            if widget:
                for field in widget.findChildren(QLineEdit):
                    field.clear()

                birthdate_field = widget.findChild(QDateEdit)
                if birthdate_field:
                    birthdate_field.setDate(QDate())  # Clears the date (null)
                    birthdate_field.setDisplayFormat("MM/dd/yyyy")
                    birthdate_field.setSpecialValueText("MM/dd/yyyy")
                    birthdate_field.setDateRange(QDate(1900, 1, 1), QDate.currentDate())
                    birthdate_field.setDate(birthdate_field.minimumDate())  # So it shows the placeholder

                for combo_box in widget.findChildren(QComboBox):
                    combo_box.setCurrentIndex(0)

    def handle_login(self):
        user_id = self.userid_field.text().strip()
        password = self.pass_field.text().strip()
        student_id = self.studentid_field.text().strip()
        birthdate = self.birthdate_edit.date().toString("yyyy-MM-dd")

        # If no login credentials are entered
        if not user_id and not student_id:
            QMessageBox.critical(self.login_ui, "Login Error", "Please enter login credentials.")
            return

        # Admin login
        if user_id == "TUPC-A-2025" and password == "axisadmin_2025":
            self.open_admin_ui()
            return

        # Faculty/Student login
        if user_id:
            if not password:
                QMessageBox.critical(self.login_ui, "Login Error", "Please enter your password.")
                return

            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="TUPCcoet@23!",
                    database="axis"
                )
                cursor = connection.cursor()

                query = "SELECT password FROM user_account WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()

                if result:
                    stored_hashed_password = result[0]
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                        if user_id.startswith("TUPC-F"):
                            self.open_faculty_ui(user_id)
                        elif user_id.startswith("TUPC-S"):
                            self.open_student_ui(user_id)
                        else:
                            QMessageBox.warning(self.login_ui, "Login Failed", "Unrecognized user type.")
                    else:
                        QMessageBox.warning(self.login_ui, "Login Failed", "Incorrect password.")
                else:
                    QMessageBox.warning(self.login_ui, "Login Failed", "User ID not found.")

            except mysql.connector.Error as e:
                QMessageBox.critical(self.login_ui, "Database Error", f"An error occurred: {e}")

            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        # Guardian login
        elif student_id:
            if not student_id and not birthdate:
                QMessageBox.critical(self.login_ui, "Login Error", "Please enter Student ID and Birthdate.")
                return
            if not student_id:
                QMessageBox.critical(self.login_ui, "Login Error", "Please enter Student ID.")
                return
            if not birthdate:
                QMessageBox.critical(self.login_ui, "Login Error", "Please enter Birthdate.")
                return
            if not student_id.startswith("TUPC-S"):
                QMessageBox.warning(self.login_ui, "Login Failed", "Invalid Student ID format.")
                return

            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="TUPCcoet@23!",
                    database="axis"
                )
                cursor = connection.cursor()

                query = "SELECT * FROM user_account WHERE user_id = %s AND birthdate = %s"
                cursor.execute(query, (student_id, birthdate))
                user = cursor.fetchone()

                if user:
                    self.open_guardian_ui(student_id)
                else:
                    QMessageBox.warning(self.login_ui, "Login Failed", "No matching student found with the provided ID and birthdate.")

            except mysql.connector.Error as e:
                QMessageBox.critical(self.login_ui, "Database Error", f"An error occurred: {e}")

            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        
    def setup_qr_listener(self):
        self.scanned_text_buffer = ""
        self.scan_timer = QTimer()
        self.scan_timer.setInterval(300)  # 300 ms delay after last keystroke
        self.scan_timer.setSingleShot(True)
        self.scan_timer.timeout.connect(self.process_qr_token)

        self.Qr_login.textEdited.connect(self.buffer_qr_input)

    def buffer_qr_input(self, text):
        self.scanned_text_buffer = text
        self.scan_timer.start()  # restart timer after every keystroke

    def process_qr_token(self):
        qr_token = self.scanned_text_buffer.strip()
        self.Qr_login.setText(qr_token)  # Optional: show full scanned value
        self.handle_qr_login()

    def setup_qr_listener(self):
        self.scanned_text_buffer = ""
        self.scan_timer = QTimer()
        self.scan_timer.setInterval(300)  # 300 ms delay after last keystroke
        self.scan_timer.setSingleShot(True)
        self.scan_timer.timeout.connect(self.process_qr_token)

        self.Qr_login.textEdited.connect(self.buffer_qr_input)

    def buffer_qr_input(self, text):
        self.scanned_text_buffer = text
        self.scan_timer.start()  # restart timer after every keystroke

    def process_qr_token(self):
        qr_token = self.scanned_text_buffer.strip()
        self.Qr_login.setText(qr_token)  # Optional: show full scanned value
        self.handle_qr_login()
        
    def handle_qr_login(self):
        qr_token = self.Qr_login.text().strip()
        if not qr_token:
            return

        print(f"Scanned QR Token: {qr_token}")  # Debug

        # --- Hardcoded QR token for Admin ---
        if qr_token == "EMS-ADMIN@AXIS-2025":
            print("Matched hardcoded admin token.")
            self.open_admin_ui()
            return

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor()

            query = "SELECT user_id, birthdate FROM user_account WHERE qr_token = %s AND status = 'approved'"
            cursor.execute(query, (qr_token,))
            result = cursor.fetchone()

            print(f"Database Result: {result}")  # Debug

            if result:
                user_id, birthdate = result

                if user_id.startswith("TUPC-F"):
                    self.open_faculty_ui(user_id)
                elif user_id.startswith("TUPC-S"):
                    self.open_student_ui(user_id)

            else:
                self.show_warning_clear("Invalid QR", "QR token is invalid or not linked to an approved account.")
                self.Qr_login.setFocus()

        except mysql.connector.Error as e:
            QMessageBox.critical(self.login_ui, "Database Error", f"An error occurred: {e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def show_warning_clear(self, title, message):
        msg = QMessageBox(self.login_ui)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(lambda _: self.Qr_login.clear())  # Clear QR field
        msg.exec()

    def open_faculty_ui(self, user_id):
        self.current_window = Faculty(user_id)  
        self.current_window.show()   
        self.hide()

    def open_admin_ui(self):
        self.current_window = Admin()
        self.current_window.show()
        self.hide()

    def open_student_ui(self, user_id):
        self.current_window = Student(user_id)
        self.current_window.show()
        self.hide() 

    def open_guardian_ui(self, student_id):
        if not student_id.startswith("TUPC-S"):
            raise ValueError("Invalid student_id provided to Guardian class")
        self.current_window = Guardian(student_id)
        self.current_window.show()
        self.hide()


class Admin(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.admin_ui = loader.load(resource_path("UI/Admin.ui"), self)  
        self.user_information = loader.load(resource_path("UI/user_information.ui"), self)
        self.notification = loader.load(resource_path("UI/notification.ui"), self)
        Icons(self.admin_ui)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.admin_ui)
        self.setCentralWidget(self.stacked_widget)  
        self.showMaximized()

        self.notification = NotificationManager(self)
        self.notification.dialog.finished.connect(self.hide_blurred_overlay)

        

        self.admin_stacked = self.admin_ui.findChild(QStackedWidget, "admin_stackedWidget")
        self.admin_dashboard = self.admin_ui.findChild(QTableWidget, "Admin_Dashboard")
        self.approvals_table = self.admin_ui.findChild(QTableWidget, "approvals_table")
        self.approved_table = self.admin_ui.findChild(QTableWidget, "approved_table")
        self.um_sort = self.admin_ui.findChild(QComboBox, "um_sort")
        self.timedb = self.admin_ui.findChild(QLabel, "time_dashboard")
        self.day = self.admin_ui.findChild(QLabel, "day")
        self.date = self.admin_ui.findChild(QLabel, "date")
        self.greetings = self.admin_ui.findChild(QLabel, "greetings")
        self.analog_clock = self.admin_ui.findChild(QFrame, "Analogclock")
        self.calendar_widget = self.admin_ui.findChild(QCalendarWidget, "calendar")

        self.pendingbtn = self.admin_ui.findChild(QPushButton, "pending_btn")
        self.studentbtn = self.admin_ui.findChild(QPushButton, "student_btn")
        self.facultybtn = self.admin_ui.findChild(QPushButton, "faculty_btn")
        self.dashboardbtn = self.admin_ui.findChild(QPushButton, "dashboard_btn")
        self.dashboardbtn.setChecked(True)
        self.pendingaccsbtn = self.admin_ui.findChild(QPushButton, "pendingaccs_btn")
        self.usermanagementbtn = self.admin_ui.findChild(QPushButton, "usermanagement_btn")
        self.notifbtn = self.admin_ui.findChild(QPushButton, "notif_btn")
        self.logoutbtn = self.admin_ui.findChild(QPushButton, "logout_btn")
        self.pending_data = self.admin_ui.findChild(QFrame, "pending_data")
        
        self.pendingbtn.clicked.connect(self.show_pendingaccs_page)
        self.studentbtn.clicked.connect(self.show_student_management_page)
        self.facultybtn.clicked.connect(self.show_faculty_management_page)
        self.dashboardbtn.clicked.connect(self.show_dashboard_page)
        self.pendingaccsbtn.clicked.connect(self.show_pendingaccs_page)
        self.usermanagementbtn.clicked.connect(lambda: (self.um_sort.setCurrentIndex(0), self.show_usermanagement_page()))
        self.logoutbtn.clicked.connect(self.logout)

        self.pendingaccsbtn.clicked.connect(self.load_approvals_data)
        self.usermanagementbtn.clicked.connect(self.load_user_management_data)
        self.notifbtn.clicked.connect(self.show_notification_dialog)

        layout = QVBoxLayout(self.analog_clock)
        layout.setContentsMargins(0, 0, 0, 0)
        self.clock_widget = AnalogClock()
        layout.addWidget(self.clock_widget)

        today_format = QTextCharFormat()
        today_format.setForeground(QColor("#ff3b30"))     # Match your theme
        today_format.setFontWeight(QFont.Bold)
        self.calendar_widget.setDateTextFormat(QDate.currentDate(), today_format)

        self.no_pending_label = QLabel("No pending account approvals.", self)
        self.no_pending_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_pending_label.setStyleSheet("font-size: 14px; color: gray;")
        self.no_pending_label.hide()
        self.approvals_table.parentWidget().layout().addWidget(self.no_pending_label)
                

        self.setup_approvals_table()  
        self.setup_approved_table()  
        self.admin_dashboard_table()  
        self.setup_approval_search_sort()  
        self.setup_user_management_search_sort()
        self.show_pending_pie_chart()
        self.update_time()
        self.start_time_update()

    def adjust_column_widths_to_header(self, table):
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def show_student_management_page(self):
        if self.admin_stacked:
            self.um_sort.setCurrentText("Student")  
            self.load_user_management_data()
            self.show_usermanagement_page()
            self.filter_user_management_table()  

    def show_faculty_management_page(self):
        if self.admin_stacked:
            self.um_sort.setCurrentText("Faculty")  
            self.load_user_management_data()
            self.show_usermanagement_page()
            self.filter_user_management_table()

    def update_time(self):
        # Time display (hh:mm:ss AM/PM)
        current_time = QTime.currentTime().toString("hh:mm:ss AP")
        self.timedb.setText(current_time)

        # Day like "Monday"
        now = datetime.now()
        day_string = now.strftime("%A")
        self.day.setText(day_string)

        # Date like "20 May"
        date_string = f"{now.day} {now.strftime('%B')}"
        self.date.setText(date_string)

        # Aesthetic and soft greetings
        hour = now.hour

        if 5 <= hour < 8:
            greeting = "Rise and shine ✨"
        elif 8 <= hour < 11:
            greeting = "Bright morning ☀️"
        elif 11 <= hour < 12:
            greeting = "Late morning glow 🌤️"
        elif 12 <= hour < 13:
            greeting = "Midday calm 🌞"
        elif 13 <= hour < 16:
            greeting = "Soft afternoon breeze 🌿"
        elif 16 <= hour < 17:
            greeting = "Golden hour ☀️"
        elif 17 <= hour < 19:
            greeting = "Hello, evening 🌇"
        elif 19 <= hour < 21:
            greeting = "Serene twilight 🌆"
        else:
            greeting = "Peaceful night 🌙"

        self.greetings.setText(greeting)

    def start_time_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  

    def show_notification_dialog(self):
        self.show_blurred_overlay()
        self.notification.load_notifications("Admin")
        self.notification.show_dialog()

    def admin_dashboard_table(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM user_account WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_account WHERE role = 'STUDENT' AND status = 'approved'")
            student_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_account WHERE role = 'FACULTY' AND status = 'approved'")
            faculty_count = cursor.fetchone()[0]
            
            self.pending_label = self.admin_ui.findChild(QLabel, "pending")
            self.student_label = self.admin_ui.findChild(QLabel, "student")
            self.faculty_label = self.admin_ui.findChild(QLabel, "faculty")
            
            if self.pending_label:
                self.pending_label.setText(str(pending_count))
            if self.student_label:
                self.student_label.setText(str(student_count))
            if self.faculty_label:
                self.faculty_label.setText(str(faculty_count))
                
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error updating dashboard: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def setup_approval_search_sort(self):
        self.pc_search = self.admin_ui.findChild(QLineEdit, "pc_search")
        self.pm_sort = self.admin_ui.findChild(QComboBox, "pm_sort")

        if self.pc_search:
            self.pc_search.textChanged.connect(self.filter_approvals_table)
        if self.pm_sort:
            self.pm_sort.currentIndexChanged.connect(self.filter_approvals_table)

    def filter_approvals_table(self):
        search_text = self.pc_search.text().lower() if self.pc_search else ""
        sort_option = self.pm_sort.currentText() if self.pm_sort else "All Users"
        
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor()

            query = """
                SELECT 
                    CONCAT(
                        last_name, ', ', first_name,
                        IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''),
                        IF(suffix IS NOT NULL AND suffix != '', CONCAT(' ', suffix), '')
                    ) AS full_name,
                    emailaddress,
                    role,
                    created_at
                FROM user_account
                WHERE status = 'pending'
            """
            
            params = []
            if search_text:
                query += """ AND (
                    CONCAT(
                        last_name, ', ', first_name,
                        IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''),
                        IF(suffix IS NOT NULL AND suffix != '', CONCAT(' ', suffix), '')
                    ) LIKE %s
                    OR emailaddress LIKE %s
                )"""
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            
            if sort_option == "Names (A-Z)":
                query += " ORDER BY last_name ASC, first_name ASC"
            elif sort_option == "Names (Z-A)":
                query += " ORDER BY last_name DESC, first_name DESC"
            elif sort_option == "Faculty":
                query += " AND role = 'FACULTY' ORDER BY created_at ASC"
            elif sort_option == "Student":
                query += " AND role = 'STUDENT' ORDER BY created_at ASC"
            elif sort_option == "All Users":
                query += " ORDER BY created_at ASC"
            
            cursor.execute(query, params)
            data = cursor.fetchall()
            
            # Handle empty state similar to load_approvals_data
            if not data:
                # Configure table for empty state message
                self.approvals_table.setRowCount(1)
                self.approvals_table.setColumnCount(4)
                
                # Create merged cell with "No pending account approvals available." message
                item = QTableWidgetItem("No pending account approvals available.")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                item.setForeground(Qt.GlobalColor.gray)
                item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-clickable
                
                # Set the item in the first cell
                self.approvals_table.setItem(0, 0, item)
                
                # Clear other cells and make them non-interactive
                for col in range(1, 4):
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    self.approvals_table.setItem(0, col, empty_item)
                
                # Merge cells to span the entire row
                self.approvals_table.setSpan(0, 0, 1, 4)
                
                # Disable the table to prevent any interactions
                self.approvals_table.setEnabled(False)
                
            else:
                # Re-enable table for normal operation
                self.approvals_table.setEnabled(True)
                
                # Clear any existing spans
                self.approvals_table.clearSpans()
                
                self.approvals_table.setRowCount(len(data))
                
                for row_idx, row_data in enumerate(data):
                    for col_idx, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                        
                        if col_idx == 0:
                            item.setForeground(Qt.GlobalColor.blue)  # Keep blue color for names
                            font = item.font()
                            font.setUnderline(False)               
                            item.setFont(font)
                            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                        else:
                            item.setForeground(Qt.GlobalColor.black)
                            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                        
                        self.approvals_table.setItem(row_idx, col_idx, item)
            
            self.adjust_column_widths_to_header(self.approvals_table)
            self.last_hovered_row = -1
            self.last_hovered_col = -1
            
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error filtering data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def show_pending_pie_chart(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor()

            # Fetch pending faculty and student counts
            cursor.execute("SELECT COUNT(*) FROM user_account WHERE status = 'pending' AND role = 'FACULTY'")
            pending_faculty = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM user_account WHERE status = 'pending' AND role = 'STUDENT'")
            pending_student = cursor.fetchone()[0]

            # Create the pie chart (no hole for full pie)
            series = QPieSeries()
            series.append("Faculty", pending_faculty)
            series.append("Student", pending_student)

            # Custom color in the palette (#055035)
            color = QColor("#055035")  # Dark green

            # Apply the same color to all slices
            for i, slice in enumerate(series.slices()):
                slice.setBrush(color)  # Apply the dark green color to all slices
                slice.setLabel(f"{slice.label()} - {int(slice.value())}")
                slice.setLabelVisible(True)
                slice.setLabelColor(Qt.white)
                slice.setPen(QPen(Qt.white, 1.5))

                # Enable hover effect (enlarge slightly on hover)
                slice.hovered.connect(lambda hovered, s=slice: s.setExploded(hovered))

            # Create the chart
            chart = QChart()
            chart.setTheme(QChart.ChartThemeBlueCerulean)
            chart.addSeries(series)
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.legend().setAlignment(Qt.AlignBottom)

            # Make the chart fully transparent
            chart.setBackgroundVisible(False)
            chart.setBackgroundBrush(Qt.transparent)
            chart.setContentsMargins(0, 0, 0, 0)
            chart.setMargins(QMargins(0, 0, 0, 0))

            # Create the chart view
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setStyleSheet("background: transparent; border: none;")

            # Find and prepare the frame
            self.pending_data = self.admin_ui.findChild(QFrame, "pending_data")
            self.pending_data.setStyleSheet("background: transparent; border: none;")

            if self.pending_data.layout() is None:
                self.pending_data.setLayout(QVBoxLayout())

            layout = self.pending_data.layout()
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(chart_view)

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading chart data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def setup_user_management_search_sort(self):
        self.um_search = self.admin_ui.findChild(QLineEdit, "um_search")
        self.um_sort = self.admin_ui.findChild(QComboBox, "um_sort")
        
        if self.um_search:
            self.um_search.textChanged.connect(self.filter_user_management_table)
        if self.um_sort:
            self.um_sort.currentIndexChanged.connect(self.filter_user_management_table)

    def filter_user_management_table(self):
        search_text = self.um_search.text().lower() if self.um_search else ""
        sort_option = self.um_sort.currentText() if self.um_sort else "All Users"
        
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    user_id,
                    CONCAT(
                        last_name, ', ', first_name,
                        IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''),
                        IF(suffix IS NOT NULL AND suffix != '', CONCAT(' ', suffix), '')
                    ) AS full_name,
                    emailaddress,
                    role,
                    department,
                    created_at,
                    date_approved,
                    status
                FROM user_account
                WHERE status = 'approved'
            """
            
            params = []
            if search_text:
                query += """ AND (
                    user_id LIKE %s
                    OR CONCAT(
                        last_name, ', ', first_name,
                        IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''),
                        IF(suffix IS NOT NULL AND suffix != '', CONCAT(' ', suffix), '')
                    ) LIKE %s
                    OR emailaddress LIKE %s
                    OR department LIKE %s
                )"""
                search_pattern = f"%{search_text}%"
                params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
            
            if sort_option == "Faculty":
                query += " AND role = 'FACULTY' ORDER BY user_id ASC"
            elif sort_option == "Student":
                query += " AND role = 'STUDENT' ORDER BY user_id ASC"

            # Sorting options
            if sort_option == "Names (A-Z)":
                query += " ORDER BY last_name ASC, first_name ASC"
            elif sort_option == "Names (Z-A)":
                query += " ORDER BY last_name DESC, first_name DESC"
            elif sort_option == "All Users":
                query += " ORDER BY date_approved ASC"
            
            cursor.execute(query, params)
            data = cursor.fetchall()
            
            # Handle empty state
            if not data:
                # Configure table for empty state message
                self.approved_table.setRowCount(1)
                self.approved_table.setColumnCount(7)  # Match your table structure
                
                # Create merged cell with "No approved users found." message
                item = QTableWidgetItem("No approved users found.")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                item.setForeground(Qt.GlobalColor.gray)
                item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-clickable
                
                # Set the item in the first cell
                self.approved_table.setItem(0, 0, item)
                
                # Clear other cells and make them non-interactive
                for col in range(1, 7):
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    self.approved_table.setItem(0, col, empty_item)
                
                # Merge cells to span the entire row
                self.approved_table.setSpan(0, 0, 1, 7)
                
                # Disable the table to prevent any interactions
                self.approved_table.setEnabled(False)
                
            else:
                # Re-enable table for normal operation
                self.approved_table.setEnabled(True)
                
                # Clear any existing spans
                self.approved_table.clearSpans()
                
                self.approved_table.setRowCount(len(data))
                
                for row_idx, row_data in enumerate(data):
                    for col_idx, col_name in enumerate(["user_id", "full_name", "emailaddress", "role", "department", "created_at", "date_approved"]):
                        value = row_data[col_name]
                        item = QTableWidgetItem(str(value) if value is not None else "")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                        item.setForeground(Qt.GlobalColor.black)
                        
                        if col_idx == 0:
                            item.setData(Qt.ItemDataRole.UserRole, row_data["user_id"])
                            font = item.font()
                            font.setUnderline(True)
                            item.setFont(font)
                            item.setForeground(QColor("blue"))
                        
                        self.approved_table.setItem(row_idx, col_idx, item)
            
            self.adjust_column_widths_to_header(self.approved_table)
            
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error filtering data: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def setup_approvals_table(self):
        self.approvals_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.approvals_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.approvals_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.approvals_table.setMouseTracking(True)

        self.approvals_table.cellEntered.connect(self.handle_table_hover)
        self.approvals_table.cellClicked.connect(self.handle_table_click)

        self.last_hovered_row = -1
        self.last_hovered_col = -1                                                          

    def handle_table_hover(self, row, column):
        if self.last_hovered_row >= 0 and self.last_hovered_col == 0:
            prev_item = self.approvals_table.item(self.last_hovered_row, 0)
            if prev_item:
                font = prev_item.font()
                font.setUnderline(False)
                prev_item.setFont(font)

        if column == 0:
            item = self.approvals_table.item(row, column)
            if item:
                font = item.font()
                font.setUnderline(True)
                item.setFont(font)
                item.setForeground(Qt.GlobalColor.blue) 
                self.approvals_table.setCursor(Qt.CursorShape.PointingHandCursor)

            self.last_hovered_row = row
            self.last_hovered_col = column
        else:
            self.approvals_table.setCursor(Qt.CursorShape.ArrowCursor)
            self.last_hovered_row = -1
            self.last_hovered_col = -1


    def setup_approved_table(self):
        self.approved_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.approved_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.approved_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.approved_table.setMouseTracking(True)

        self.approved_table.cellEntered.connect(self.handle_table_hover2)
        self.approved_table.cellClicked.connect(self.handle_table_click)

        self.last_hovered_row = -1
        self.last_hovered_col = -1


    def handle_table_hover2(self, row, column):
        if self.last_hovered_row >= 0 and self.last_hovered_col == 0:
            prev_item = self.approved_table.item(self.last_hovered_row, 0)
            if prev_item:
                font = prev_item.font()
                font.setUnderline(False)
                prev_item.setFont(font)

        if column == 0:
            item = self.approved_table.item(row, column)
            if item:
                font = item.font()
                font.setUnderline(True)
                item.setFont(font)
                item.setForeground(Qt.GlobalColor.blue) 
                self.approved_table.setCursor(Qt.CursorShape.PointingHandCursor)

            self.last_hovered_row = row
            self.last_hovered_col = column
        else:
            self.approved_table.setCursor(Qt.CursorShape.ArrowCursor)
            self.last_hovered_row = -1
            self.last_hovered_col = -1

    def load_approvals_data(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor()

            query = """
                SELECT 
                    CONCAT(
                        last_name, ', ', first_name,
                        IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''),
                        IF(suffix IS NOT NULL AND suffix != '', CONCAT(' ', suffix), '')
                    ) AS full_name,
                    emailaddress,
                    role,
                    created_at
                FROM user_account
                WHERE status = 'pending'
            """
            cursor.execute(query)
            data = cursor.fetchall()

            # Always show the table but handle empty state differently
            self.approvals_table.show()
            self.no_pending_label.hide()

            if not data:
                # Configure table for empty state message
                self.approvals_table.setRowCount(1)
                self.approvals_table.setColumnCount(4)
                self.approvals_table.setHorizontalHeaderLabels(["FULL NAME", "EMAIL", "ROLE", "REGISTRATION DATE"])
                
                # Create merged cell with "No pending account approvals available." message
                item = QTableWidgetItem("No pending account approvals available.")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                item.setForeground(Qt.GlobalColor.gray)
                item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-clickable
                
                # Set the item in the first cell
                self.approvals_table.setItem(0, 0, item)
                
                # Clear other cells and make them non-interactive
                for col in range(1, 4):
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    self.approvals_table.setItem(0, col, empty_item)
                
                # Merge cells to span the entire row
                self.approvals_table.setSpan(0, 0, 1, 4)
                
                # Disable the table to prevent any interactions
                self.approvals_table.setEnabled(False)
                
            else:
                # Re-enable table for normal operation
                self.approvals_table.setEnabled(True)
                
                # Clear any existing spans
                self.approvals_table.clearSpans()
                
                self.approvals_table.setRowCount(len(data))
                self.approvals_table.setColumnCount(4)
                self.approvals_table.setHorizontalHeaderLabels(["FULL NAME", "EMAIL", "ROLE", "REGISTRATION DATE"])

                for row_idx, row_data in enumerate(data):
                    for col_idx, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                        if col_idx == 0:
                            item.setForeground(Qt.GlobalColor.blue)  
                            font = item.font()
                            font.setUnderline(False)               
                            item.setFont(font)
                            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                        else:
                            item.setForeground(Qt.GlobalColor.black)
                            item.setFlags(Qt.ItemFlag.ItemIsEnabled)

                        self.approvals_table.setItem(row_idx, col_idx, item)

            self.adjust_column_widths_to_header(self.approvals_table)
            self.last_hovered_row = -1
            self.last_hovered_col = -1

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def handle_table_click(self, row, column):
        if column == 0:
            full_name = self.approvals_table.item(row, column).text()
            self.show_registration_details(full_name)

    def show_registration_details(self, full_name):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT id, first_name, middle_name, last_name, suffix, emailaddress,
                    role, birthdate, sex, department
                FROM user_account
                WHERE status = 'pending'
                AND CONCAT(last_name, ', ', first_name,
                            IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''),
                            IF(suffix IS NOT NULL AND suffix != '', CONCAT(' ', suffix), '')
                ) = %s
            """
            cursor.execute(query, (full_name,))
            user_data = cursor.fetchone()

            if user_data:
                self.show_user_information_dialog(user_data)
            else:
                QMessageBox.warning(self, "User Not Found", "User information not found in the database.")

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error retrieving user details: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def show_blurred_overlay(self):
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        self.overlay.setGeometry(self.rect())
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.show()

    def hide_blurred_overlay(self):
        if hasattr(self, "overlay"):
            self.overlay.deleteLater()
            del self.overlay

    def show_user_information_dialog(self, user_data, from_approval=True):
        self.show_blurred_overlay()

        loader = QUiLoader()
        user_info_ui = loader.load(resource_path("UI/user_information.ui"), self)
        Icons(user_info_ui)

        self.user_info_dialog = QDialog(self)
        
        status = user_data.get("status", "pending")
        if status == "approved":
            self.user_info_dialog.setWindowTitle("User Information")
            title_label = user_info_ui.findChild(QLabel, "label_19")
            if title_label:
                title_label.setText("User Information")
        else:
            self.user_info_dialog.setWindowTitle("Registration Details")
            title_label = user_info_ui.findChild(QLabel, "label_19")
            if title_label:
                title_label.setText("Registration Details")
        
        self.user_info_dialog.setModal(True)
        self.user_info_dialog.setLayout(QVBoxLayout())
        self.user_info_dialog.layout().addWidget(user_info_ui)

        self.lbl_last_name = user_info_ui.findChild(QLabel, "last_name")
        self.lbl_first_name = user_info_ui.findChild(QLabel, "first_name")
        self.lbl_middle_name = user_info_ui.findChild(QLabel, "middle_name")
        self.lbl_sex = user_info_ui.findChild(QLabel, "sex")
        self.lbl_birthdate = user_info_ui.findChild(QLabel, "birthdate")
        self.lbl_role = user_info_ui.findChild(QLabel, "role")
        self.lbl_department = user_info_ui.findChild(QLabel, "department")
        self.lbl_email = user_info_ui.findChild(QLabel, "email")

        self.close_btn = user_info_ui.findChild(QPushButton, "close_btn")
        self.approve_btn = user_info_ui.findChild(QPushButton, "approve")
        self.reject_btn = user_info_ui.findChild(QPushButton, "reject")

        if status == "approved":
            if self.approve_btn:
                self.approve_btn.hide()
            if self.reject_btn:
                self.reject_btn.hide()
        else:
            if self.approve_btn:
                self.approve_btn.show()
            if self.reject_btn:
                self.reject_btn.show()

        if self.close_btn:
            self.close_btn.clicked.connect(self.user_info_dialog.close)
        if self.approve_btn:
            self.approve_btn.clicked.connect(lambda: self.approve_account(user_data.get("emailaddress", "")))
        if self.reject_btn:
            self.reject_btn.clicked.connect(lambda: self.reject_account(user_data.get("emailaddress", "")))

        birthdate = user_data.get("birthdate", "")
        if birthdate and not isinstance(birthdate, str):
            birthdate = birthdate.strftime("%Y-%m-%d")

        self.lbl_last_name.setText(str(user_data.get("last_name", "")))
        first_name = user_data.get("first_name", "")
        suffix = user_data.get("suffix") or ""
        full_first_name = f"{first_name} {suffix}".strip()
        self.lbl_first_name.setText(full_first_name)
        self.lbl_middle_name.setText(str(user_data.get("middle_name", "")))
        self.lbl_sex.setText(str(user_data.get("sex", "")))
        self.lbl_birthdate.setText(str(birthdate))
        self.lbl_role.setText(str(user_data.get("role", "")))
        self.lbl_department.setText(str(user_data.get("department", "")))
        self.lbl_email.setText(str(user_data.get("emailaddress", "")))

        self.user_info_dialog.finished.connect(self.hide_blurred_overlay)
        self.user_info_dialog.exec()

    def check_for_bounce(self, target_email, inbox_email, app_password):
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(inbox_email, app_password)
            imap.select("inbox")

            # Search for recent emails from mailer-daemon or postmaster
            status, messages = imap.search(None, 'OR FROM "mailer-daemon@googlemail.com" FROM "postmaster@google.com"')
            if status != "OK":
                return False

            for num in reversed(messages[0].split()[-10:]):  # Check last 10 messages
                status, data = imap.fetch(num, "(RFC822)")
                if status != "OK":
                    continue

                msg = email.message_from_bytes(data[0][1])
                subject = msg.get("Subject", "").lower()
                body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode(errors="ignore")
                else:
                    body += msg.get_payload(decode=True).decode(errors="ignore")

                # Check for common bounce indicators
                if ("delivery status notification" in subject or "address not found" in body.lower()) and target_email.lower() in body.lower():
                    imap.logout()
                    return True
                

            imap.logout()
            return False
        except Exception as e:
            print(f"Bounce check error: {e}")
            return False


    def send_user_id_email(self, to_email, user_id, qr_image_bytes):
        try:
            # Connect to DB to get first name
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT first_name FROM user_account WHERE emailaddress = %s", (to_email,))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self, "User Not Found", f"No user found with email: {to_email}")
                return False

            first_name = result['first_name']

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to fetch first name: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        from_email = "axistupcems@gmail.com"
        password = "ajiu rivz ttgw lzka"  # Gmail App Password

        try:
            subject = "AXIS Account Approval Status"
            body = f"""
            <html>
            <body>
                <p>Dear {first_name},</p>
                <p>Your account in the Examination Management System (AXIS) has been approved.</p>
                <p>Your User ID is: <b>{user_id}</b></p>
                <p>Attached is your QR code for login and examination purposes.</p>
                <p>Please keep this secure.</p>
                <p>Regards,<br>AXIS Admin</p>
            </body>
            </html>
            """

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            qr_part = MIMEBase('application', 'octet-stream')
            qr_part.set_payload(qr_image_bytes)
            encoders.encode_base64(qr_part)
            qr_part.add_header('Content-Disposition', 'attachment; filename="qr_code.png"')
            msg.attach(qr_part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()

            time.sleep(15)
            if self.check_for_bounce(to_email, from_email, password):
                print(f"Confirmed bounce for {to_email}")
                return False

            return True

        except Exception as e:
            print(f"Email error: {e}")
            return False



    def approve_account(self, email):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT role, birthdate, first_name FROM user_account WHERE emailaddress = %s", (email,))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self, "Not Found", "Applicant not found.")
                return

            role = result['role']
            birthday = result['birthdate'].strftime('%Y-%m-%d')
            role_code = "F" if role.upper() == "FACULTY" else "S"

            pattern = f"TUPC-{role_code}-%"
            cursor.execute(
                "SELECT user_id FROM user_account WHERE user_id LIKE %s ORDER BY user_id DESC LIMIT 1",
                (pattern,)
            )
            last_user = cursor.fetchone()

            if last_user:
                last_number = int(last_user['user_id'].split("-")[-1])
                next_number = last_number + 1
            else:
                next_number = 1

            new_user_id = f"TUPC-{role_code}-{next_number:04d}"
            qr_token = f"user_id:{new_user_id};birthdate:{birthday}"

            qr_img = qrcode.make(qr_token)
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_bytes = qr_buffer.getvalue()

            first_letter = result['first_name'][0].upper()
            default_dp_path = f"UI/DP/{first_letter}.png"
            if not os.path.exists(default_dp_path):
                default_dp_path = "UI/DP/default.png"

            # Pre-approve user in DB
            cursor.execute(
                "UPDATE user_account SET status = 'approved', user_id = %s, date_approved = NOW(), qr_token = %s, profile_image = %s WHERE emailaddress = %s",
                (new_user_id, qr_token, default_dp_path, email)
            )
            connection.commit()

            loading_dialog = QProgressDialog("Validating email address...\nThis may take a moment to verify delivery and validity.", None, 0, 0, self)
            loading_dialog.setWindowTitle("Please Wait")
            loading_dialog.setWindowModality(Qt.ApplicationModal)
            loading_dialog.setCancelButton(None)
            loading_dialog.setMinimumDuration(0)
            loading_dialog.show()
            QApplication.processEvents()

            success = self.send_user_id_email(email, new_user_id, qr_bytes)

            loading_dialog.close()

            if success:
                QMessageBox.information(self, "Approved", f"Account for {email} approved.\nUser ID: {new_user_id}")
                self.user_info_dialog.accept()
                self.load_approvals_data()
                self.load_user_management_data()
            else:
                cursor.execute("""
                    UPDATE user_account
                    SET status = 'rejected', user_id = NULL, date_approved = NULL, qr_token = NULL
                    WHERE emailaddress = %s
                """, (email,))
                connection.commit()
                QMessageBox.warning(self, "Invalid Email", f"The email {email} could not be delivered.\nAccount has been rejected.")
                self.user_info_dialog.accept()
                self.load_approvals_data()
                self.load_user_management_data()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Approval failed:\n{e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    
    def reject_account(self, email_address):
        loader = QUiLoader()
        ui_file = QFile("UI/reject.ui")
        if not ui_file.open(QFile.ReadOnly):
            return

        dialog = loader.load(ui_file, self)
        ui_file.close()

        cb_invalid = dialog.findChild(QCheckBox, "invalid")
        cb_requirement = dialog.findChild(QCheckBox, "requirement")
        cb_others = dialog.findChild(QCheckBox, "others")
        line_others = dialog.findChild(QLineEdit, "others_l")
        btn_okay = dialog.findChild(QPushButton, "ok")
        btn_cancel = dialog.findChild(QPushButton, "cancel")

        if not cb_others or not line_others:
            return

        line_others.setEnabled(False)

        def toggle_line_edit(checked):
            line_others.setEnabled(checked)
            if not checked:
                line_others.clear()

        cb_others.toggled.connect(toggle_line_edit)

        def on_ok():
            reasons = []
            if cb_invalid and cb_invalid.isChecked():
                reasons.append(cb_invalid.text())
            if cb_requirement and cb_requirement.isChecked():
                reasons.append(cb_requirement.text())
            if cb_others and cb_others.isChecked() and line_others.text().strip():
                reasons.append(line_others.text().strip())

            if not reasons:
                QMessageBox.warning(dialog, "No Reason Selected", "Please select or input at least one reason.")
                return

            final_reason = "\n- " + "\n- ".join(reasons)

            self.send_rejection_email(email_address, final_reason)
            self.update_user_status(email_address, "rejected")
            QMessageBox.information(dialog, "User  Rejected", "The user has been rejected and notified via email.")

            if hasattr(self, 'user_info_dialog') and self.user_info_dialog.isVisible():
                self.user_info_dialog.reject()  

            dialog.accept()

            self.load_approvals_data()
            self.load_user_management_data() 

        btn_okay.clicked.connect(on_ok)
        btn_cancel.clicked.connect(dialog.reject)

        dialog.exec()

    def send_rejection_email(self, to_email, reason_text):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT first_name FROM user_account WHERE emailaddress = %s", (to_email,))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self, "User Not Found", f"No user found with email: {to_email}")
                return

            first_name = result['first_name']

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to fetch first name: {e}")
            return
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        from_email = "axistupcems@gmail.com"
        password = "ajiu rivz ttgw lzka"

        subject = "AXIS Account Approval Status"

        formatted_reason = reason_text.replace('Other: ', '')
        formatted_reason = formatted_reason.replace('\n', '<br>')

        body = f"""
        <html>
        <body>
            <p>Dear {first_name},</p>
            <p>We regret to inform you that your registration in the Examination Management System (AXIS) has been rejected for the following reason(s):<br><br>
            <b>{formatted_reason}</b><br><br>
            If you believe this was a mistake or have any questions, please don't hesitate to contact us.</p>
            <p>Sincerely,<br>
            AXIS Admin</p>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Show loading dialog
        loading_dialog = QProgressDialog("Sending rejection email...", None, 0, 0, self)
        loading_dialog.setWindowTitle("Please Wait")
        loading_dialog.setWindowModality(Qt.ApplicationModal)
        loading_dialog.setCancelButton(None)
        loading_dialog.setMinimumDuration(0)
        loading_dialog.show()
        QApplication.processEvents()

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()

            loading_dialog.close()
            QMessageBox.information(self, "Email Sent", "Rejection email sent successfully.")

        except Exception as e:
            loading_dialog.close()
            error_msg = QMessageBox(self)
            error_msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setText("Email Error")
            error_msg.setInformativeText(f"Failed to send email:\n{e}")
            error_msg.exec()

    def get_user_details_by_id(self, user_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT 
                    last_name, first_name, middle_name, suffix, sex, birthdate,
                    role, department, emailaddress, status, user_id
                FROM user_account
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()

            return user_data
        
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve user details:\n{e}")
            return None
        
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                

    def load_user_management_data(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True) 

            query = """
                SELECT 
                    user_id,
                    CONCAT(
                        last_name, ', ', first_name,
                        IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''),
                        IF(suffix IS NOT NULL AND suffix != '', CONCAT(' ', suffix), '')
                    ) AS full_name,
                    emailaddress,
                    role,
                    department,
                    created_at,
                    date_approved,
                    status
                FROM user_account
                WHERE status = 'approved'
                ORDER BY date_approved ASC
            """
            cursor.execute(query)
            data = cursor.fetchall()

            self.approved_table.setRowCount(len(data))
            self.approved_table.setColumnCount(7)
            self.approved_table.setHorizontalHeaderLabels([
                "USER ID", "FULL NAME", "EMAIL", "ROLE", "DEPARTMENT", "CREATED AT", "DATE APPROVED"
            ])

            try:
                self.approved_table.cellClicked.disconnect()
            except:
                pass  
                
            self.approved_table.cellClicked.connect(self.handle_approved_table_cell_clicked)

            for row_idx, row_data in enumerate(data):
                for col_idx, col_name in enumerate(["user_id", "full_name", "emailaddress", "role", "department", "created_at", "date_approved"]):
                    value = row_data[col_name]
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    item.setForeground(Qt.GlobalColor.black)
                    
                    if col_idx == 0: 
                        item.setData(Qt.ItemDataRole.UserRole, row_data["user_id"])
                        
                        font = item.font()
                        font.setUnderline(True)
                        item.setFont(font)
                        item.setForeground(QColor("blue"))
                    
                    self.approved_table.setItem(row_idx, col_idx, item)
            
            self.adjust_column_widths_to_header(self.approved_table)
            self.approved_table.horizontalHeader().setVisible(True)
            self.last_hovered_row = -1
            self.last_hovered_col = -1

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load user management data:\n{e}")
        
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def handle_approved_table_cell_clicked(self, row, column):
        if column == 0: 
            user_id_item = self.approved_table.item(row, column)
            if user_id_item:
                user_id = user_id_item.text()
                user_data = self.get_user_details_by_id(user_id)
                
                if user_data:
                    self.show_user_information_dialog(user_data, from_approval=False)

    def update_user_status(self, email_address, new_status):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            query = """
                UPDATE user_account
                SET status = %s
                WHERE emailaddress = %s
            """
            cursor.execute(query, (new_status, email_address))

            connection.commit()
            connection.close()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to update user status:\n{e}")

    def open_registration_details(self, notif_time_str):
        """Open Registration Details if notif_time matches created_at time in the database (with 1-second tolerance)."""
        try:
            # Remove brackets and strip whitespace from notif_time_str
            notif_time_str = notif_time_str.strip("[]").strip()

            # Parse the notification time string (12-hour format with seconds)
            notif_time = datetime.strptime(notif_time_str, "%I:%M:%S %p")

            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT 
                    id,
                    first_name,
                    middle_name,
                    last_name,
                    suffix,
                    emailaddress,
                    role,
                    birthdate,
                    sex,
                    department,
                    created_at
                FROM user_account
                WHERE status = 'pending'
            """
            cursor.execute(query)
            users = cursor.fetchall()

            for user in users:
                created_at = user['created_at']

                # Align dates for comparison: assume notif_time has the same date as created_at
                notif_dt = created_at.replace(
                    hour=notif_time.hour,
                    minute=notif_time.minute,
                    second=notif_time.second,
                    microsecond=0
                )

                # Condition: Exact match or 1-second delay
                time_difference = abs((created_at - notif_dt).total_seconds())
                if time_difference == 0 or time_difference == 1:
                    self.show_user_information_dialog(user)
                    return

            QMessageBox.warning(self, "User Not Found", "User Registration already processed.")

        except ValueError:
            QMessageBox.critical(self, "Invalid Time Format", f"Could not parse notification time: {notif_time_str}")
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to fetch user: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    
    def show_dashboard_page(self):
        if self.admin_stacked:
            self.admin_stacked.setCurrentIndex(0)
            self.admin_dashboard_table()

        # Button state
        self.dashboardbtn.setChecked(True)
        self.pendingaccsbtn.setChecked(False)
        self.usermanagementbtn.setChecked(False)

    def show_pendingaccs_page(self):
        if self.admin_stacked:
            self.admin_stacked.setCurrentIndex(1)
            self.load_approvals_data()
            if hasattr(self, 'pc_search'):
                self.pc_search.clear()
            if hasattr(self, 'pm_sort'):
                self.pm_sort.setCurrentIndex(0)

        # Button state
        self.dashboardbtn.setChecked(False)
        self.pendingaccsbtn.setChecked(True)
        self.usermanagementbtn.setChecked(False)

    def show_usermanagement_page(self):
        if self.admin_stacked:
            self.admin_stacked.setCurrentIndex(2)
            self.load_user_management_data()
            if hasattr(self, 'um_search'):
                self.um_search.clear()

        # Button state
        self.dashboardbtn.setChecked(False)
        self.pendingaccsbtn.setChecked(False)
        self.usermanagementbtn.setChecked(True)


    def logout(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Logout Confirmation")
        msg_box.setText("Are you sure you want to log out?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.login_window = Login_Register()
            self.login_window.show()
            self.hide()

class Student(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        if not isinstance(user_id, str) or not user_id.startswith("TUPC-S"):
            raise ValueError("Invalid user_id provided to Faculty class")

        self.user_id = user_id
        self.current_user_id = self.user_id
       
        loader = QUiLoader()
        self.student_ui = loader.load(resource_path("UI/Student.ui"), self)
        self.notification = loader.load(resource_path("UI/notification.ui"), self)
        

        Icons(self.student_ui)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.student_ui)
        self.setCentralWidget(self.stacked_widget)  
        self.showMaximized()

        self.student_stacked = self.student_ui.findChild(QStackedWidget, "student_stackedWidget")

        self.timedb = self.student_ui.findChild(QLabel, "time_dashboard")

        self.start_time_update()

        self.available_exam_dashboard = self.student_ui.findChild(QListWidget, "available_exam_dashboard")
        self.available_sort_dashboard = self.student_ui.findChild(QComboBox, "filter_assigned")
        self.missing_exam_dashboard = self.student_ui.findChild(QListWidget, "missed_exam_dashboard")
        self.missing_sort_dashboard = self.student_ui.findChild(QComboBox, "filter_missing")
        self.completed_exam_dashboard = self.student_ui.findChild(QListWidget, "completed_exam_dashboard")
        self.completed_sort_dashboard = self.student_ui.findChild(QComboBox, "filter_completed")
        self.upcoming_exam_dashboard = self.student_ui.findChild(QListWidget, "upcoming_exam_dashboard")
        self.upcoming_sort_dashboard = self.student_ui.findChild(QComboBox, "filter_upcoming")
        self.exams_status = self.student_ui.findChild(QTabWidget, "exams_status")

        self.exams_status.setTabText(0, "Assigned")
        self.exams_status.setTabText(1, "Upcoming")
        self.exams_status.setTabText(2, "Missing")
        self.exams_status.setTabText(3, "Done")

        self.exams_status.currentChanged.connect(self.handle_tab_change)
 
        self.sp_table = self.student_ui.findChild(QTableWidget, "sp_table")
        self.sp_graph = self.student_ui.findChild(QFrame, "sp_graph")
        self.prelim_chart = self.student_ui.findChild(QCheckBox, "prelim_chart")
        self.midterm_chart = self.student_ui.findChild(QCheckBox, "midterm_chart")
        self.finals_chart = self.student_ui.findChild(QCheckBox, "finals_chart")
        self.sem_sp = self.student_ui.findChild(QComboBox, "sem_sp")
        self.sp_pie = self.student_ui.findChild(QFrame, "sp_pie")
        self.perf_message = self.student_ui.findChild(QLabel, "perf_message")
        self.icon_label = self.student_ui.findChild(QLabel, "congrats_s")

        self.name = self.student_ui.findChild(QLabel, "name_label")
        self.birthdate = self.student_ui.findChild(QLabel, "birthdate")
        self.sex = self.student_ui.findChild(QLabel, "sex")
        self.email = self.student_ui.findChild(QLabel, "email")
        self.user_id_label = self.student_ui.findChild(QLabel, "user_id_label")

        
        self.dashboardbtn = self.student_ui.findChild(QPushButton, "dashboard_btn")
        self.myperfbtn = self.student_ui.findChild(QPushButton, "myperformance_btn")
        self.takeexambtn = self.student_ui.findChild(QPushButton, "takeexam_btn")
        self.notifbtn = self.student_ui.findChild(QPushButton, "notif_btn")
        self.settingsbtn = self.student_ui.findChild(QPushButton, "settings_btn")
        self.cpbtn = self.student_ui.findChild(QPushButton, "ForgotPassword_2")
        self.logoutbtn = self.student_ui.findChild(QPushButton, "logout_btn")
        self.start_exam = self.student_ui.findChild(QPushButton, "start_exam")
        self.countdown_timer = QTimer()
        self.profile_image = self.student_ui.findChild(QWidget, "photo")
        self.day = self.student_ui.findChild(QLabel, "day")
        self.date = self.student_ui.findChild(QLabel, "date")
        self.greetings = self.student_ui.findChild(QLabel, "greetings")
        self.analog_clock = self.student_ui.findChild(QFrame, "Analogclock")
        self.calendar_widget = self.student_ui.findChild(QCalendarWidget, "calendar_dashboard")

        self.dashboardbtn.setCheckable(True)
        self.myperfbtn.setCheckable(True)
        self.takeexambtn.setCheckable(True)
        self.dashboardbtn.setChecked(True)

        layout = QVBoxLayout(self.analog_clock)
        layout.setContentsMargins(0, 0, 0, 0)
        self.clock_widget = AnalogClock()
        layout.addWidget(self.clock_widget)

        today_format = QTextCharFormat()
        today_format.setForeground(QColor("#ff3b30"))     # Match your theme
        today_format.setFontWeight(QFont.Bold)
        self.calendar_widget.setDateTextFormat(QDate.currentDate(), today_format)

        self.dashboardbtn.clicked.connect(self.show_dashboard_page)
        self.myperfbtn.clicked.connect(self.show_myperf_page)
        self.takeexambtn.clicked.connect(self.show_takeexam_page)
        self.settingsbtn.clicked.connect(self.show_settings_page)
        self.cpbtn.clicked.connect(self.show_reset_password_dialog)
        self.logoutbtn.clicked.connect(self.logout)

        self.start_exam.clicked.connect(self.start_selected_exam)

        self.notifbtn.clicked.connect(self.show_notification_dialog)
        self.notification = NotificationManager(self)
        self.notification.load_notifications(role="student", user_id=self.user_id)
        self.notification.dialog.finished.connect(self.hide_blurred_overlay)

        
        self.display_student_performance()

        # Connect checkboxes to filter function
        self.prelim_chart.stateChanged.connect(self.update_bar_graph)
        self.midterm_chart.stateChanged.connect(self.update_bar_graph)
        self.finals_chart.stateChanged.connect(self.update_bar_graph)
        self.sem_sp.currentIndexChanged.connect(self.update_bar_graph)
        self.sem_sp.currentTextChanged.connect(self.update_bar_graph)
        
        
        self.student_stacked.setCurrentIndex(0)

        self.exambtn = self.student_ui.findChild(QPushButton, "exam_btn")
        self.exambtn.clicked.connect(self.start_selected_exam_from_dashboard)
        self.available_sort_dashboard.currentTextChanged.connect(self.filter_available_exam_dashboard)
        self.upcoming_sort_dashboard.currentTextChanged.connect(self.filter_upcoming_exam_dashboard)
        self.missing_sort_dashboard.currentTextChanged.connect(self.filter_missing_exam_dashboard)
        self.completed_sort_dashboard.currentTextChanged.connect(self.filter_completed_exam_dashboard)

        self.prelim_chart.stateChanged.connect(lambda: self.display_student_performance())
        self.midterm_chart.stateChanged.connect(lambda: self.display_student_performance())
        self.finals_chart.stateChanged.connect(lambda: self.display_student_performance())
        self.sem_sp.currentIndexChanged.connect(lambda: self.display_student_performance())


        self.take_prelim = self.student_ui.findChild(QListWidget, "take_prelim")
        self.take_midterm = self.student_ui.findChild(QListWidget, "take_midterm")
        self.take_finals = self.student_ui.findChild(QListWidget, "take_finals")

        self.sem_sp.currentTextChanged.connect(self.on_semester_changed)
        self.selected_exam_dashboard_item = None
        self.available_exam_dashboard.itemClicked.connect(self.set_selected_exam_dashboard_item)

        self.current_missing_exam_ids = set()
        self.selected_exam_take_item = None
        self.selected_exam_take_id = None

        self.take_prelim.itemClicked.connect(self.set_selected_exam_take_item)
        self.take_midterm.itemClicked.connect(self.set_selected_exam_take_item)
        self.take_finals.itemClicked.connect(self.set_selected_exam_take_item)
        
        
        self.load_all_exam_tabs()


    def set_selected_exam_dashboard_item(self, item):
        self.selected_exam_dashboard_id = item.data(Qt.UserRole)

    def set_selected_exam_take_item(self, item):
        self.selected_exam_take_item = item
        self.selected_exam_take_id = item.data(Qt.UserRole)

    def load_all_exam_tabs(self):
        self.fetch_student_data()
        self.load_student_exams()
        self.load_missing_exams()
        self.apply_default_filters()

        self.exam_dashboard_timer = QTimer(self)
        self.exam_dashboard_timer.timeout.connect(self.refresh_all_exam_dashboards)
        self.exam_dashboard_timer.start(1000) 

    def refresh_all_exam_dashboards(self):
        self.load_student_exams()
        self.load_missing_exams()

    def handle_tab_change(self, index):
            tab_text = self.exams_status.tabText(index)

            if tab_text == "Assigned":
                self.filter_available_exam_dashboard(self.available_sort_dashboard.currentText())
            elif tab_text == "Upcoming":
                self.filter_upcoming_exam_dashboard(self.upcoming_sort_dashboard.currentText())
            elif tab_text == "Missing":
                self.filter_missing_exam_dashboard(self.missing_sort_dashboard.currentText())  # This already calls the filter after loading
            elif tab_text == "Done":
                self.filter_completed_exam_dashboard(self.completed_sort_dashboard.currentText())

    def update_exam_button_visibility(self):
        count = self.available_exam_dashboard.count()

        if count == 0:
            self.exambtn.hide()
            return

        # If the only item is the placeholder text
        if count == 1:
            item = self.available_exam_dashboard.item(0)
            if item and item.text().strip() == "No available exams yet for this term.":
                self.exambtn.hide()
                return

        # Check if there's at least one visible, real item
        has_real_exam = any(
            self.available_exam_dashboard.item(i).isHidden() == False and
            self.available_exam_dashboard.item(i).flags() & Qt.ItemIsEnabled
            for i in range(count)
        )

        self.exambtn.setVisible(has_real_exam)
    
    def apply_default_filters(self):
        self.available_sort_dashboard.setCurrentText("PRELIM EXAM")
        self.upcoming_sort_dashboard.setCurrentText("PRELIM EXAM")
        self.missing_sort_dashboard.setCurrentText("PRELIM EXAM")
        self.completed_sort_dashboard.setCurrentText("PRELIM EXAM")

        self.filter_available_exam_dashboard("PRELIM EXAM")
        self.filter_upcoming_exam_dashboard("PRELIM EXAM")
        self.filter_missing_exam_dashboard("PRELIM EXAM")
        self.filter_completed_exam_dashboard("PRELIM EXAM")

    def filter_available_exam_dashboard(self, selected_type):
        has_visible_items = False

        for index in range(self.available_exam_dashboard.count()):
            item = self.available_exam_dashboard.item(index)

            if not item or not item.flags() & Qt.ItemIsEnabled:
                continue  # Skip placeholder items

            text = item.text()
            if selected_type.upper() in text.upper():
                item.setHidden(False)
                has_visible_items = True
            else:
                item.setHidden(True)

        # Remove existing placeholder if any
        for index in range(self.available_exam_dashboard.count()):
            item = self.available_exam_dashboard.item(index)
            if item and not item.flags() & Qt.ItemIsEnabled:
                self.available_exam_dashboard.takeItem(index)
                break  # There should be only one placeholder
            

        # If no matching exams, show placeholder message
        if not has_visible_items:
            placeholder = QListWidgetItem("No available exams yet for this term.")
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(QColor("gray"))
            font = placeholder.font()
            font.setItalic(True)
            font.setPointSize(10)
            placeholder.setFont(font)
            placeholder.setTextAlignment(Qt.AlignCenter)
            self.available_exam_dashboard.addItem(placeholder)

        self.update_exam_button_visibility()
        


    def filter_upcoming_exam_dashboard(self, selected_type):
        has_visible_items = False

        for index in range(self.upcoming_exam_dashboard.count()):
            item = self.upcoming_exam_dashboard.item(index)

            if not item or not item.flags() & Qt.ItemIsEnabled:
                continue

            text = item.text()
            if selected_type.upper() in text.upper():
                item.setHidden(False)
                has_visible_items = True
            else:
                item.setHidden(True)

        # Remove any old placeholder
        for index in range(self.upcoming_exam_dashboard.count()):
            item = self.upcoming_exam_dashboard.item(index)
            if item and not item.flags() & Qt.ItemIsEnabled:
                self.upcoming_exam_dashboard.takeItem(index)
                break

        # Add placeholder if nothing is visible
        if not has_visible_items:
            placeholder = QListWidgetItem("No upcoming exams yet for this term.")
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(QColor("gray"))
            font = placeholder.font()
            font.setItalic(True)
            font.setPointSize(10)
            placeholder.setFont(font)
            placeholder.setTextAlignment(Qt.AlignCenter)
            self.upcoming_exam_dashboard.addItem(placeholder)

    def filter_missing_exam_dashboard(self, selected_type):
        has_visible_items = False

        for index in range(self.missing_exam_dashboard.count()):
            item = self.missing_exam_dashboard.item(index)

            if not item or not item.flags() & Qt.ItemIsEnabled:
                continue

            text = item.text()
            if selected_type.upper() in text.upper():
                item.setHidden(False)
                has_visible_items = True
            else:
                item.setHidden(True)

        # Remove any existing placeholder
        for index in range(self.missing_exam_dashboard.count()):
            item = self.missing_exam_dashboard.item(index)
            if item and not item.flags() & Qt.ItemIsEnabled:
                self.missing_exam_dashboard.takeItem(index)
                break

        if not has_visible_items:
            placeholder = QListWidgetItem("No missed exams yet for this term.")
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(QColor("gray"))
            font = placeholder.font()
            font.setItalic(True)
            font.setPointSize(10)
            placeholder.setFont(font)
            placeholder.setTextAlignment(Qt.AlignCenter)
            self.missing_exam_dashboard.addItem(placeholder)

    def filter_completed_exam_dashboard(self, selected_type):
        has_visible_items = False

        for index in range(self.completed_exam_dashboard.count()):
            item = self.completed_exam_dashboard.item(index)

            if not item or not item.flags() & Qt.ItemIsEnabled:
                continue

            text = item.text()
            if selected_type.upper() in text.upper():
                item.setHidden(False)
                has_visible_items = True
            else:
                item.setHidden(True)

        # Remove any existing placeholder
        for index in range(self.completed_exam_dashboard.count()):
            item = self.completed_exam_dashboard.item(index)
            if item and not item.flags() & Qt.ItemIsEnabled:
                self.completed_exam_dashboard.takeItem(index)
                break

        if not has_visible_items:
            placeholder = QListWidgetItem("No completed exams yet for this term.")
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(QColor("gray"))
            font = placeholder.font()
            font.setItalic(True)
            font.setPointSize(10)
            placeholder.setFont(font)
            placeholder.setTextAlignment(Qt.AlignCenter)
            self.completed_exam_dashboard.addItem(placeholder)

    def start_selected_exam_from_dashboard(self):
    # Use the stored exam_id, not the QListWidgetItem itself
        exam_id = getattr(self, "selected_exam_dashboard_id", None)

        if exam_id is None:
            QMessageBox.warning(self, "No Selection", "Please select an exam to start.")
            return

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                # Fetch full exam details
                cursor.execute("SELECT * FROM examination_form WHERE exam_id = %s", (exam_id,))
                exam_data = cursor.fetchall()

                if not exam_data:
                    QMessageBox.warning(self, "Not Found", "Could not find the selected exam.")
                    return

                first = exam_data[0]
                major_exam = first["major_exam_type"]
                semester = first["semester"]
                subject_code = first["subject_code"]
                time_limit = first["time_limit"]
                exam_date = first["exam_date"]
                schedule_time = first.get("schedule_time")

                # ✅ Time restriction check
                try:
                    exam_available = True
                    if schedule_time:
                        start_time_str = schedule_time.split(" - ")[0].strip()
                        exam_datetime = datetime.strptime(f"{exam_date} {start_time_str}", "%Y-%m-%d %I:%M %p")
                        now = datetime.now()
                        if now < exam_datetime:
                            exam_available = False
                except Exception as e:
                    print(f"[WARNING] Failed to parse exam time: {e}")
                    exam_available = True  # Fail-safe access

                if not exam_available:
                    QMessageBox.information(
                        self,
                        "Exam Not Yet Available",
                        f"This exam will be available on {exam_date} at {start_time_str}."
                    )
                    return

                # Consolidate exam parts and types
                parts = [(row["exam_part"], row["exam_type"], int(row["number_of_items"])) for row in exam_data]
                consolidated = {}
                for _, exam_type, num in parts:
                    consolidated[exam_type] = consolidated.get(exam_type, 0) + num

                consolidated_parts = [(etype, count) for etype, count in consolidated.items()]

                # Start exam
                self.load_exam_template_session(
                    exam_id,
                    major_exam,
                    time_limit,
                    subject_code,
                    semester,
                    consolidated_parts
                )

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading exam:\n{e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def start_time_update(self):
        self.update_time()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  

    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss AP")
        self.timedb.setText(current_time)

        now = datetime.now()
        day_string = now.strftime("%A")
        self.day.setText(day_string)

        date_string = f"{now.day} {now.strftime('%B')}"
        self.date.setText(date_string)

        hour = now.hour

        if 5 <= hour < 8:
            greeting = "Rise and shine ✨"
        elif 8 <= hour < 11:
            greeting = "Bright morning ☀️"
        elif 11 <= hour < 12:
            greeting = "Late morning glow 🌤️"
        elif 12 <= hour < 13:
            greeting = "Midday calm 🌞"
        elif 13 <= hour < 16:
            greeting = "Soft afternoon breeze 🌿"
        elif 16 <= hour < 17:
            greeting = "Golden hour ☀️"
        elif 17 <= hour < 19:
            greeting = "Hello, evening 🌇"
        elif 19 <= hour < 21:
            greeting = "Serene twilight 🌆"
        else:
            greeting = "Peaceful night 🌙"

        self.greetings.setText(greeting)

    def fetch_student_data(self):
        try:
            # Initialize the available_exam_dashboard here
            self.available_exam_dashboard = self.student_ui.findChild(QListWidget, "available_exam_dashboard")

            # Ensure that all necessary widgets are found
            if not self.available_exam_dashboard:
                QMessageBox.warning(self, "Interface Error", "Could not find the available_exam_dashboard QListWidget.")
                return

            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                # STEP 1: Fetch student data including profile_image
                query = """
                    SELECT user_id, first_name, last_name, middle_name, suffix, profile_image
                    FROM user_account 
                    WHERE user_id = %s
                """
                cursor.execute(query, (self.current_user_id,))
                student_data = cursor.fetchone()

                if student_data:
                    name_parts = []

                    if student_data['first_name']:
                        name_parts.append(student_data['first_name'])
                    if student_data['middle_name'] and student_data['middle_name'] != "None":
                        name_parts.append(student_data['middle_name'])
                    if student_data['last_name']:
                        name_parts.append(student_data['last_name'])
                    if student_data['suffix'] and student_data['suffix'] != "None":
                        name_parts.append(student_data['suffix'])

                    full_name = " ".join(name_parts).upper()

                    name_label = self.student_ui.findChild(QLabel, "name_dashboard")
                    user_id_labels = self.student_ui.findChild(QLabel, "user_id_dashboard")

                    if name_label:
                        name_label.setText(full_name)
                    if user_id_labels:
                        user_id_labels.setText(student_data['user_id'])
                        self.user_id_labels = user_id_labels

                    from PySide6.QtGui import QPixmap
                    from PySide6.QtCore import Qt
                    import os

                    profile_path = student_data.get('profile_image')
                    if profile_path and os.path.exists(profile_path):
                        pixmap = QPixmap(profile_path)
                    else:
                        pixmap = QPixmap("UI/DP/default.png")

                    # Make sure this QLabel exists in your UI with objectName 'profile_image'
                    self.profile_image = self.student_ui.findChild(QLabel, "photo")
                    if self.profile_image:
                        self.profile_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

                # STEP 2: Fetch latest exam data
                latest_exam_query = """
                    SELECT exam_id, end_time 
                    FROM student_answers 
                    WHERE student_id = %s AND end_time IS NOT NULL
                    ORDER BY end_time DESC
                    LIMIT 1
                """
                cursor.execute(latest_exam_query, (self.current_user_id,))
                latest_exam_data = cursor.fetchone()

                latest_score_label = self.student_ui.findChild(QLabel, "latest_dashboard")
                out_of_label = self.student_ui.findChild(QLabel, "out_of")
                subject_label = self.student_ui.findChild(QLabel, "subject_dashboard")

                if latest_exam_data:
                    exam_id = latest_exam_data['exam_id']

                    cursor.execute("""
                        SELECT COUNT(*) AS correct_count 
                        FROM student_answers 
                        WHERE student_id = %s AND exam_id = %s AND is_correct = 1
                    """, (self.current_user_id, exam_id))
                    score_result = cursor.fetchone()
                    correct_score = score_result['correct_count'] if score_result else 0

                    cursor.execute("""
                        SELECT COUNT(*) AS total_items 
                        FROM student_answers 
                        WHERE student_id = %s AND exam_id = %s
                    """, (self.current_user_id, exam_id))
                    total_items_result = cursor.fetchone()
                    total_items = total_items_result['total_items'] if total_items_result else 0

                    cursor.execute("""
                        SELECT number_of_items, subject_code 
                        FROM examination_form 
                        WHERE exam_id = %s
                    """, (exam_id,))
                    exam_details = cursor.fetchone()

                    if latest_score_label:
                        latest_score_label.setText(str(correct_score))
                    if out_of_label:
                        out_of_label.setText(f"out of {total_items}")
                    if subject_label and exam_details and 'subject_code' in exam_details:
                        subject_label.setText(exam_details['subject_code'] or "N/A")
                    else:
                        subject_label.setText("N/A")

                else:
                    if latest_score_label:
                        latest_score_label.setText("0")
                    if out_of_label:
                        out_of_label.setText("out of 0")
                    if subject_label:
                        subject_label.setText("N/A")

                # Load available exams
                self.available_exam_dashboard.clear()

                cursor.execute("""
                    SELECT DISTINCT exam_id FROM student_answers 
                    WHERE student_id = %s
                """, (self.current_user_id,))
                taken_exams = set(row['exam_id'] for row in cursor.fetchall())

                cursor.execute("""
                    SELECT exam_id, subject_code, semester, major_exam_type, 
                        exam_status, exam_date, schedule_time, created_by
                    FROM examination_form
                    WHERE exam_status = 'Published'
                """)
                exams = cursor.fetchall()

                if exams:
                    added_exam_ids = set()
                    
                    # Get current datetime for comparison
                    now = datetime.now()

                    for exam in exams:
                        exam_id = exam['exam_id']
                        if exam_id in taken_exams or exam_id in added_exam_ids:
                            continue
                            
                        # Check if the exam has already ended
                        is_past_due = False
                        if exam['schedule_time']:
                            try:
                                # Extract end time from the schedule
                                end_time_str = exam['schedule_time'].split(" - ")[1].strip()
                                exam_end_datetime = datetime.strptime(f"{exam['exam_date']} {end_time_str}", "%Y-%m-%d %I:%M %p")
                                is_past_due = now > exam_end_datetime
                                
                                if is_past_due:
                                    # Skip this exam for the available dashboard as it's past due
                                    continue
                            except Exception as e:
                                print(f"[WARNING] Failed to parse exam end time: {e}")
                        
                        added_exam_ids.add(exam_id)

                        try:
                            cursor.execute("""
                                SELECT first_name, middle_name, last_name, suffix
                                FROM user_account
                                WHERE user_id = %s
                            """, (exam['created_by'],))
                            user_data = cursor.fetchone()

                            if user_data:
                                middle_initial = f" {user_data['middle_name'][0]}." if user_data['middle_name'] else ""
                                suffix = f" {user_data['suffix']}" if user_data['suffix'] else ""
                                creator_name = f"{user_data['first_name']}{middle_initial} {user_data['last_name']}{suffix}".upper()
                            else:
                                creator_name = exam['created_by'].upper()
                        except Exception:
                            creator_name = exam['created_by'].upper()

                        datetime_line = f"{exam['exam_date']} | {exam['schedule_time']}" if exam['schedule_time'] else f"{exam['exam_date']}"
                        subject_sem_line = f"{exam['subject_code']} - {exam['semester']} - {exam['major_exam_type']}"
                        creator_line = f"BY: {creator_name}"

                        full_text = f"{datetime_line}\n{subject_sem_line}\n{creator_line}"
                        

                        dashboard_item = QListWidgetItem(full_text)
                        dashboard_item.setData(Qt.UserRole, exam_id)

                        font = dashboard_item.font()
                        font.setPointSize(11)
                        dashboard_item.setFont(font)
                        dashboard_item.setBackground(QColor(0, 102, 128))
                        dashboard_item.setForeground(QColor(255, 255, 255))

                        self.available_exam_dashboard.addItem(dashboard_item)

                if self.available_exam_dashboard.count() == 0:
                    item = QListWidgetItem("No exam available at the moment.")
                    item.setFlags(Qt.NoItemFlags)
                    item.setForeground(QColor("gray"))
                    font = item.font()
                    font.setItalic(True)
                    font.setPointSize(10)
                    item.setFont(font)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.available_exam_dashboard.addItem(item)
                
                self.update_exam_button_visibility()
                self.filter_available_exam_dashboard(self.available_sort_dashboard.currentText())
                self.filter_upcoming_exam_dashboard(self.upcoming_sort_dashboard.currentText())
                self.filter_missing_exam_dashboard(self.missing_sort_dashboard.currentText())
                self.filter_completed_exam_dashboard(self.completed_sort_dashboard.currentText())

                cursor.close()
                connection.close()

        except mysql.connector.Error as e:
            # QMessageBox.critical(self, "Database Error", f"An error occurred while loading data:\n{e}")
            pass
        except Exception as e:
            # QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{e}")
            pass


    def load_student_exams(self):
        self.take_prelim = self.student_ui.findChild(QListWidget, "take_prelim")
        self.take_midterm = self.student_ui.findChild(QListWidget, "take_midterm")
        self.take_finals = self.student_ui.findChild(QListWidget, "take_finals")
        self.available_exam_dashboard = self.student_ui.findChild(QListWidget, "available_exam_dashboard")
        self.missing_exam_dashboard = self.student_ui.findChild(QListWidget, "missed_exam_dashboard")
        self.completed_exam_dashboard = self.student_ui.findChild(QListWidget, "completed_exam_dashboard")
        self.upcoming_exam_dashboard = self.student_ui.findChild(QListWidget, "upcoming_exam_dashboard")
        self.exams_status = self.student_ui.findChild(QTabWidget, "exams_status")

        self.exams_status.setTabText(0, "Assigned")
        self.exams_status.setTabText(1, "Upcoming")
        self.exams_status.setTabText(2, "Missing")
        self.exams_status.setTabText(3, "Done")

        if not all([self.take_prelim, self.take_midterm, self.take_finals,
                    self.available_exam_dashboard, self.upcoming_exam_dashboard]):
            QMessageBox.warning(self, "Interface Error", "Could not find all required QListWidgets.")
            return

        self.take_prelim.clear()
        self.take_midterm.clear()
        self.take_finals.clear()
        
        if any(self.available_exam_dashboard.item(i).flags() & Qt.ItemIsEnabled
               for i in range(self.available_exam_dashboard.count())):
            self.available_exam_dashboard.clear()

        if any(self.upcoming_exam_dashboard.item(i).flags() & Qt.ItemIsEnabled
               for i in range(self.upcoming_exam_dashboard.count())):
            self.upcoming_exam_dashboard.clear()

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                cursor.execute("""
                    SELECT DISTINCT exam_id FROM student_answers 
                    WHERE student_id = %s
                """, (self.user_id,))
                taken_exams = set(row['exam_id'] for row in cursor.fetchall())

                cursor.execute("""
                    SELECT exam_id, subject_code, semester, major_exam_type, 
                        exam_status, exam_date, schedule_time, created_by
                    FROM examination_form
                    WHERE exam_status = 'Published'
                """)
                exams = cursor.fetchall()
                if not exams:
                    return

                added_exam_ids = set()
                now = datetime.now()

                for exam in exams:
                    exam_id = exam['exam_id']
                    if exam_id in taken_exams or exam_id in added_exam_ids:
                        continue

                    is_past_due = False
                    end_time_str = ""
                    if exam['schedule_time']:
                        try:
                            end_time_parts = exam['schedule_time'].split(" - ")
                            if len(end_time_parts) > 1:
                                end_time_str = end_time_parts[1].strip()
                                exam_end_datetime = datetime.strptime(f"{exam['exam_date']} {end_time_str}", "%Y-%m-%d %I:%M %p")
                                is_past_due = now >= exam_end_datetime  # ✅ At exactly 2:00 PM, exam is no longer available
                            if is_past_due:
                                continue
                        except Exception as e:
                            print(f"[WARNING] Failed to parse exam end time: {e}")

                    added_exam_ids.add(exam_id)
                    major_exam_type = exam['major_exam_type'].upper()
                    creator_id = exam['created_by']

                    try:
                        cursor.execute("""
                            SELECT first_name, middle_name, last_name, suffix
                            FROM user_account
                            WHERE user_id = %s
                        """, (creator_id,))
                        user_data = cursor.fetchone()
                        if user_data:
                            middle_initial = f" {user_data['middle_name'][0]}." if user_data['middle_name'] else ""
                            suffix = f" {user_data['suffix']}" if user_data['suffix'] else ""
                            creator_name = f"{user_data['first_name']}{middle_initial} {user_data['last_name']}{suffix}".upper()
                        else:
                            creator_name = creator_id.upper()
                    except Exception:
                        creator_name = creator_id.upper()

                    datetime_line = f"{exam['exam_date']} | {exam['schedule_time']}" if exam['schedule_time'] else f"{exam['exam_date']}"
                    creator_line = f"BY: {creator_name}"

                    subject_sem_line_tab = f"{exam['subject_code']} - {exam['semester']}"
                    full_text_tab = f"{datetime_line}\n{subject_sem_line_tab}\n{creator_line}"

                    # 👇 Format for dashboard
                    subject_sem_line_dashboard = f"{exam['subject_code']} - {exam['semester']} - {exam['major_exam_type']}"
                    full_text_dashboard = f"{datetime_line}\n{subject_sem_line_dashboard}\n{creator_line}"

                    exam_available = True
                    start_time_str = ""
                    try:
                        if exam['schedule_time']:
                            start_time_str = exam['schedule_time'].split(" - ")[0].strip()
                            exam_datetime = datetime.strptime(f"{exam['exam_date']} {start_time_str}", "%Y-%m-%d %I:%M %p")
                            exam_available = now >= exam_datetime
                    except Exception as e:
                        print(f"[WARNING] Failed to parse exam time: {e}")
                        exam_available = True

                    item = QListWidgetItem(full_text_tab)
                    item.setData(Qt.UserRole, exam_id)
                    font = item.font()
                    font.setPointSize(11)
                    item.setFont(font)

                    if exam_available:
                        item.setBackground(QColor(0, 128, 85))
                        item.setForeground(QColor(255, 255, 255))

                        if "PRELIM" in major_exam_type:
                            self.take_prelim.insertItem(0, item.clone())  # LIFO
                        elif "MIDTERM" in major_exam_type:
                            self.take_midterm.insertItem(0, item.clone())  # LIFO
                        elif "FINAL" in major_exam_type:
                            self.take_finals.insertItem(0, item.clone())  # LIFO

                        dashboard_item = QListWidgetItem(full_text_dashboard)
                        dashboard_item.setData(Qt.UserRole, exam_id)
                        font = dashboard_item.font()
                        font.setPointSize(11)
                        dashboard_item.setFont(font)
                        dashboard_item.setBackground(QColor(0, 102, 128))
                        self.available_exam_dashboard.insertItem(0, dashboard_item)  # LIFO
                    else:
                        upcoming_item = QListWidgetItem(full_text_dashboard)
                        upcoming_item.setData(Qt.UserRole, exam_id)
                        font = upcoming_item.font()
                        font.setPointSize(11)
                        upcoming_item.setFont(font)
                        upcoming_item.setBackground(QColor(102, 51, 153))
                        upcoming_item.setForeground(QColor(255, 255, 255))
                        upcoming_item.setToolTip(f"This examination will be available on {exam['exam_date']} at {start_time_str}")
                        self.upcoming_exam_dashboard.insertItem(0, upcoming_item)  # LIFO

                def add_placeholder_if_empty(list_widget, message):
                    if list_widget.count() == 0:
                        item = QListWidgetItem(message)
                        item.setFlags(Qt.NoItemFlags)
                        item.setForeground(QColor("gray"))
                        font = item.font()
                        font.setItalic(True)
                        font.setPointSize(10)
                        item.setFont(font)
                        item.setTextAlignment(Qt.AlignCenter)
                        list_widget.addItem(item)

                add_placeholder_if_empty(self.take_prelim, "No PRELIM exam available at the moment.")
                add_placeholder_if_empty(self.take_midterm, "No MIDTERM exam available at the moment.")
                add_placeholder_if_empty(self.take_finals, "No FINAL exam available at the moment.")
                add_placeholder_if_empty(self.available_exam_dashboard, "No exam available at the moment.")
                add_placeholder_if_empty(self.upcoming_exam_dashboard, "No upcoming exams at the moment.")
                QTimer.singleShot(0, self.update_exam_button_visibility)

                self.completed_exam_dashboard.clear()

                cursor.execute("""
                    SELECT DISTINCT sa.exam_id, ef.subject_code, ef.major_exam_type, ef.semester, ef.exam_date, ef.schedule_time, ef.created_by
                    FROM student_answers sa
                    JOIN examination_form ef ON sa.exam_id = ef.exam_id
                    WHERE sa.student_id = %s AND sa.status = 'Completed'
                """, (self.user_id,))

                completed_exams = cursor.fetchall()

                for exam in completed_exams:
                    exam_id = exam['exam_id']
                    creator_id = exam['created_by']

                    try:
                        cursor.execute("""
                            SELECT first_name, middle_name, last_name, suffix
                            FROM user_account
                            WHERE user_id = %s
                        """, (creator_id,))
                        user_data = cursor.fetchone()
                        if user_data:
                            middle_initial = f" {user_data['middle_name'][0]}." if user_data['middle_name'] else ""
                            suffix = f" {user_data['suffix']}" if user_data['suffix'] else ""
                            creator_name = f"{user_data['first_name']}{middle_initial} {user_data['last_name']}{suffix}".upper()
                        else:
                            creator_name = creator_id.upper()
                    except Exception:
                        creator_name = creator_id.upper()

                    datetime_line = f"{exam['exam_date']} | {exam['schedule_time']}" if exam['schedule_time'] else f"{exam['exam_date']}"
                    subject_sem_line = f"{exam['subject_code']} - {exam['semester']} - {exam['major_exam_type']}"
                    creator_line = f"BY: {creator_name}"
                    full_text = f"{datetime_line}\n{subject_sem_line}\n{creator_line}"

                    done_item = QListWidgetItem(full_text)
                    done_item.setData(Qt.UserRole, exam_id)
                    font = done_item.font()
                    font.setPointSize(11)
                    done_item.setFont(font)
                    done_item.setBackground(QColor(85, 85, 85))
                    done_item.setForeground(QColor(255, 255, 255))

                    self.completed_exam_dashboard.insertItem(0, done_item)  # LIFO

                add_placeholder_if_empty(self.completed_exam_dashboard, "No completed exams yet.")
                self.filter_available_exam_dashboard(self.available_sort_dashboard.currentText())
                self.filter_upcoming_exam_dashboard(self.upcoming_sort_dashboard.currentText())
                self.filter_missing_exam_dashboard(self.missing_sort_dashboard.currentText())
                self.filter_completed_exam_dashboard(self.completed_sort_dashboard.currentText())

        except mysql.connector.Error as e:
            error_message = f"An error occurred while loading exams:\n{e}"
            QMessageBox.critical(self, "Database Error", error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred:\n{e}"
            QMessageBox.critical(self, "Error", error_message)
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def load_missing_exams(self):
        if not hasattr(self, "current_missing_exam_ids"):
            self.current_missing_exam_ids = set()

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                # Current date and time for comparison
                now = datetime.now()
                
                # Step 1: Get all exams that the student hasn't taken and are past their end time
                cursor.execute("""
                    SELECT DISTINCT exam_id FROM student_answers 
                    WHERE student_id = %s
                """, (self.user_id,))
                taken_exams = set(row['exam_id'] for row in cursor.fetchall())
                
                cursor.execute("""
                    SELECT exam_id, subject_code, semester, major_exam_type, exam_date, schedule_time, created_by, exam_status
                    FROM examination_form
                    WHERE exam_status = 'Published'
                """)
                
                all_published_exams = cursor.fetchall()

                def get_exam_end_datetime(exam):
                    try:
                        if exam['schedule_time']:
                            end_time_str = exam['schedule_time'].split(" - ")[1].strip()
                            return datetime.strptime(f"{exam['exam_date']} {end_time_str}", "%Y-%m-%d %I:%M %p")
                    except Exception:
                        pass
                    return datetime.min

                all_published_exams.sort(key=get_exam_end_datetime, reverse=True)
                added_count = 0
                
                for exam in all_published_exams:
                    exam_id = exam['exam_id']
                    
                    # Skip if student has already taken this exam
                    if exam_id in taken_exams or exam_id in self.current_missing_exam_ids:
                        continue
                    
                    # Check if exam's end time has passed
                    is_past_due = False
                    
                    if exam['schedule_time']:
                        try:
                            # Extract end time from the schedule
                            end_time_parts = exam['schedule_time'].split(" - ")
                            
                            if len(end_time_parts) > 1:
                                end_time_str = end_time_parts[1].strip()
                                exam_end_datetime = datetime.strptime(f"{exam['exam_date']} {end_time_str}", "%Y-%m-%d %I:%M %p")
                                is_past_due = now >= exam_end_datetime
                        except Exception as e:
                            print(f"[WARNING] Failed to parse exam end time: {e}")
                            continue
                        
                        # Add to missing dashboard if the exam is past due
                        if is_past_due:
                            # Get creator details
                            creator_id = exam['created_by']
                            
                            try:
                                cursor.execute("""
                                    SELECT first_name, middle_name, last_name, suffix 
                                    FROM user_account 
                                    WHERE user_id = %s
                                """, (creator_id,))
                                user_data = cursor.fetchone()

                                if user_data:
                                    middle_initial = f" {user_data['middle_name'][0]}." if user_data['middle_name'] else ""
                                    suffix = f" {user_data['suffix']}" if user_data['suffix'] else ""
                                    creator_name = f"{user_data['first_name']}{middle_initial} {user_data['last_name']}{suffix}".upper()
                                else:
                                    creator_name = creator_id.upper()
                            except Exception:
                                creator_name = creator_id.upper()

                            datetime_line = f"{exam['exam_date']} | {exam['schedule_time']}" if exam['schedule_time'] else f"{exam['exam_date']}"
                            subject_sem_line = f"{exam['subject_code']} - {exam['semester']} - {exam['major_exam_type']}"
                            creator_line = f"BY: {creator_name}"
                            full_text = f"{datetime_line}\n{subject_sem_line}\n{creator_line}"

                            missing_item = QListWidgetItem(full_text)
                            missing_item.setData(Qt.UserRole, exam_id)
                            font = missing_item.font()
                            font.setPointSize(11)
                            missing_item.setFont(font)
                            missing_item.setBackground(QColor(128, 0, 0))  # Deep red for missing
                            missing_item.setForeground(QColor(255, 255, 255))
                            self.missing_exam_dashboard.insertItem(0, missing_item)

                            self.current_missing_exam_ids.add(exam_id)
                            added_count += 1

                if added_count == 0 and self.missing_exam_dashboard.count() == 0:
                    item = QListWidgetItem("No missed exams detected.")
                    item.setFlags(Qt.NoItemFlags)
                    item.setForeground(QColor("gray"))
                    font = item.font()
                    font.setItalic(True)
                    font.setPointSize(10)
                    item.setFont(font)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.missing_exam_dashboard.addItem(item)
                            
        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Error", f"Database error: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def _add_exam_to_table(self, table, exam_id, subject_code, exam_date, schedule_time, creator_name):
        row_position = table.rowCount()
        table.insertRow(row_position)
        
        subject_item = QListWidgetItem(subject_code)
        subject_item.setData(Qt.UserRole, exam_id)

        try:
            if isinstance(exam_date, str):
                formatted_date = exam_date
            else:
                formatted_date = exam_date.strftime("%Y-%m-%d")
        except:
            formatted_date = str(exam_date)
        
        table.setItem(row_position, 0, subject_item)
        table.setItem(row_position, 1, QListWidgetItem(formatted_date))
        table.setItem(row_position, 2, QListWidgetItem(str(schedule_time)))
        table.setItem(row_position, 3, QListWidgetItem(creator_name))
        
        for col in range(table.columnCount()):
            item = table.item(row_position, col)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def start_selected_exam(self):
        exam_id = getattr(self, "selected_exam_take_id", None)

        if exam_id is None:
            QMessageBox.warning(self, "No Selection", "Please select an exam before starting.")
            return
    

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                cursor.execute("SELECT * FROM examination_form WHERE exam_id = %s", (exam_id,))
                exam_data = cursor.fetchall()

                if not exam_data:
                    QMessageBox.warning(self, "Not Found", "Could not find the selected exam.")
                    return
                
                first = exam_data[0]
                major_exam = first["major_exam_type"]
                semester = first["semester"]
                subject_code = first["subject_code"]
                time_limit = first["time_limit"]

                parts = [(row["exam_part"], row["exam_type"], int(row["number_of_items"])) for row in exam_data]
                consolidated = {}
                for _, exam_type, num in parts:
                    consolidated[exam_type] = consolidated.get(exam_type, 0) + num

                consolidated_parts = [(etype, count) for etype, count in consolidated.items()]

                self.load_exam_template_session(
                    exam_id,
                    major_exam,
                    time_limit,
                    subject_code,
                    semester,
                    consolidated_parts
                )

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading exam:\n{e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def load_exam_template_session(self, exam_id, major_type, time_limit, subject_code, semester, consolidated_parts):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                cursor.execute("""
                    SELECT description, question, option_a, option_b, option_c, option_d, correct_answer 
                    FROM multiple_choice_exam 
                    WHERE exam_id = %s
                """, (exam_id,))
                mc_questions = cursor.fetchall()

                cursor.execute("""
                    SELECT description, question, correct_answer 
                    FROM true_false_exam 
                    WHERE exam_id = %s
                """, (exam_id,))
                tf_questions = cursor.fetchall()

                cursor.execute("""
                    SELECT description, question, correct_answer 
                    FROM identification_exam 
                    WHERE exam_id = %s
                """, (exam_id,))
                id_questions = cursor.fetchall()

                current_time = datetime.now().strftime("%I:%M %p")

                self.exam_template_window = ConductExam(
                    major_type,
                    time_limit,
                    subject_code,
                    semester,
                    consolidated_parts,
                    self.user_id,
                    user_role="student",
                    exam_id=exam_id,
                    student_loaded_data={
                        "multiple_choice": mc_questions,
                        "true_false": tf_questions,
                        "identification": id_questions
                    },
                    start_time=current_time,
                    current_window=self,
                    student_dashboard=self  # ✅ pass reference for performance refresh
                )
                self.exam_template_window.show()
                self.hide()


        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading draft exam data:\n{e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                
    def display_student_performance(self):
        # Helper: get list of checked exam types (only for table display)
        exam_types = []
        if self.prelim_chart.isChecked():
            exam_types.append("PRELIM EXAM")
        if self.midterm_chart.isChecked():
            exam_types.append("MIDTERM EXAM")
        if self.finals_chart.isChecked():
            exam_types.append("FINAL EXAM")

        selected_semester = self.sem_sp.currentText()

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor()

            # Step 1: Fetch taken exams (with checkbox filtering for table)
            query = """
            SELECT 
                ef.exam_id,
                ef.subject_code AS Course, 
                sa.major_exam_type AS "Major Exam Type",
                ef.semester AS Semester, 
                (
                    SELECT SUM(number_of_items) 
                    FROM examination_form 
                    WHERE exam_id = ef.exam_id
                ) AS Total_Items, 
                (
                    SELECT COUNT(DISTINCT sa_sub.question_id)
                    FROM student_answers sa_sub
                    WHERE sa_sub.exam_id = ef.exam_id
                    AND sa_sub.student_id = sa.student_id
                    AND sa_sub.status = 'Completed'
                    AND sa_sub.is_correct = 1
                ) AS Correct_Answers
            FROM student_answers sa
            JOIN examination_form ef ON sa.exam_id = ef.exam_id
            WHERE sa.student_id = %s 
            AND sa.status = 'Completed' 
            AND ef.semester = %s
            """

            if exam_types:
                format_strings = ','.join(['%s'] * len(exam_types))
                query += f" AND sa.major_exam_type IN ({format_strings})"

            query += """
            GROUP BY ef.exam_id, ef.subject_code, sa.major_exam_type, ef.semester, sa.student_id
            ORDER BY ef.subject_code, sa.major_exam_type;
            """

            params = [self.user_id, selected_semester]
            if exam_types:
                params.extend(exam_types)

            cursor.execute(query, params)
            taken_results = cursor.fetchall()

            # Step 2: Fetch ALL taken exams for graph (without checkbox filtering)
            query_all = """
            SELECT 
                ef.exam_id,
                ef.subject_code AS Course, 
                sa.major_exam_type AS "Major Exam Type",
                ef.semester AS Semester, 
                (
                    SELECT SUM(number_of_items) 
                    FROM examination_form 
                    WHERE exam_id = ef.exam_id
                ) AS Total_Items, 
                (
                    SELECT COUNT(DISTINCT sa_sub.question_id)
                    FROM student_answers sa_sub
                    WHERE sa_sub.exam_id = ef.exam_id
                    AND sa_sub.student_id = sa.student_id
                    AND sa_sub.status = 'Completed'
                    AND sa_sub.is_correct = 1
                ) AS Correct_Answers
            FROM student_answers sa
            JOIN examination_form ef ON sa.exam_id = ef.exam_id
            WHERE sa.student_id = %s 
            AND sa.status = 'Completed' 
            AND ef.semester = %s
            GROUP BY ef.exam_id, ef.subject_code, sa.major_exam_type, ef.semester, sa.student_id
            ORDER BY ef.subject_code, sa.major_exam_type;
            """

            cursor.execute(query_all, [self.user_id, selected_semester])
            all_taken_results = cursor.fetchall()

            # Step 3: Fetch missing exams
            cursor.execute("""
                SELECT DISTINCT exam_id FROM student_answers 
                WHERE student_id = %s
            """, (self.user_id,))
            taken_exam_ids = set(row[0] for row in cursor.fetchall())

            # Now get published exams for the semester and filter missing
            cursor.execute("""
                SELECT exam_id, subject_code, semester, major_exam_type, exam_date, schedule_time
                FROM examination_form
                WHERE exam_status = 'Published' AND semester = %s
            """, (selected_semester,))
            all_exams = cursor.fetchall()

            from datetime import datetime
            now = datetime.now()
            missing_results = []
            missing_results_for_graph = []

            already_added_exam_ids = set()

            for exam_id, subject_code, semester, exam_type, exam_date, schedule_time in all_exams:
                if exam_id in taken_exam_ids or exam_id in already_added_exam_ids:
                    continue

                # Check if exam has ended
                if schedule_time:
                    try:
                        time_parts = schedule_time.split(" - ")
                        if len(time_parts) > 1:
                            end_time = time_parts[1].strip()
                            exam_end = datetime.strptime(f"{exam_date} {end_time}", "%Y-%m-%d %I:%M %p")
                            if now < exam_end:
                                continue
                    except Exception:
                        continue

                # Only add once per exam_id
                cursor.execute("SELECT SUM(number_of_items) FROM examination_form WHERE exam_id = %s", (exam_id,))
                total_items = cursor.fetchone()[0] or 0

                if exam_types and exam_type not in exam_types:
                    pass
                else:
                    missing_results.append((exam_id, subject_code, exam_type, semester, total_items, 0))

                missing_results_for_graph.append((exam_id, subject_code, exam_type, semester, total_items, 0))
                already_added_exam_ids.add(exam_id)

            # Combine results for table (with checkbox filtering)
            all_results = taken_results + missing_results
            all_results.sort(key=lambda x: x[0], reverse=True)  # Stack-like order

            # Combine results for graph (all exam types)
            self.exam_data_for_graph = all_taken_results + missing_results_for_graph
            self.exam_data_for_graph.sort(key=lambda x: x[0], reverse=True)

            # Update table
            self.sp_table.setRowCount(0)
            self.sp_table.setColumnCount(5)
            self.sp_table.setHorizontalHeaderLabels(["Exam ID", "Course", "Major Exam Type", "Semester", "Result"])
            
            # Hide the vertical header (row numbers)
            self.sp_table.verticalHeader().hide()

            # Check if there's no data to display
            if not all_results:
                # Clear the table and show "no data" message
                self.sp_table.setRowCount(1)
                self.sp_table.setColumnCount(1)
                
                # Create a "no data" message item
                no_data_item = QTableWidgetItem("No exam data available for the selected criteria.")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                no_data_item.setForeground(QBrush(QColor('gray')))
                
                # Set font style for the message
                font = QFont()
                font.setItalic(True)
                font.setPointSize(12)
                no_data_item.setFont(font)
                
                self.sp_table.setItem(0, 0, no_data_item)
                self.sp_table.horizontalHeader().hide()
                self.sp_table.verticalHeader().hide()
                self.sp_table.setEditTriggers(QTableWidget.NoEditTriggers)
                
                # Make the cell span the entire table width
                self.sp_table.setSpan(0, 0, 1, 1)
                self.sp_table.resizeColumnsToContents()
                self.sp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
                # Update graphs with empty data
                self.update_bar_graph()
                self.update_pie_gauge()

                self.sp_table.setEnabled(False)
                try:
                    self.sp_table.cellClicked.disconnect()
                except Exception:
                    pass
                
                cursor.close()
                connection.close()
                return

            # Show header again if it was hidden
            self.sp_table.horizontalHeader().show()
            # Keep vertical header hidden
            self.sp_table.verticalHeader().hide()

            for row_index, (exam_id, course, exam_type, semester, total_items, correct_answers) in enumerate(all_results):
                self.sp_table.insertRow(row_index)

                percentage = (correct_answers / total_items * 100) if total_items else 0
                result_str = f"{correct_answers}/{total_items}"
                result_item = QTableWidgetItem(result_str)
                result_item.setTextAlignment(Qt.AlignCenter)
                result_item.setForeground(QBrush(QColor('red' if percentage < 75 else 'green')))

                exam_id_item = QTableWidgetItem(str(exam_id))
                font = QFont()
                font.setUnderline(True)
                exam_id_item.setFont(font)
                exam_id_item.setForeground(QBrush(QColor('blue')))
                exam_id_item.setTextAlignment(Qt.AlignCenter)

                items = [
                    exam_id_item,
                    QTableWidgetItem(course),
                    QTableWidgetItem(exam_type),
                    QTableWidgetItem(semester),
                    result_item
                ]

                for col_index, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    self.sp_table.setItem(row_index, col_index, item)

            self.sp_table.resizeColumnsToContents()
            self.sp_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.sp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Hide the vertical header (row numbers) for normal display
            self.sp_table.verticalHeader().hide()

            self.sp_table.setEnabled(True)
            try:
                self.sp_table.cellClicked.disconnect()
            except Exception:
                pass
            self.sp_table.cellClicked.connect(self.handle_exam_id_click)

            cursor.close()
            connection.close()

            self.update_bar_graph()
            self.update_pie_gauge()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            
            # Show error message in table
            self.sp_table.setRowCount(1)
            self.sp_table.setColumnCount(1)
            
            error_item = QTableWidgetItem(f"Error loading exam data: {str(err)}")
            error_item.setTextAlignment(Qt.AlignCenter)
            error_item.setForeground(QBrush(QColor('red')))
            
            font = QFont()
            font.setItalic(True)
            error_item.setFont(font)
            
            self.sp_table.setItem(0, 0, error_item)
            self.sp_table.horizontalHeader().hide()
            self.sp_table.verticalHeader().hide()
            self.sp_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.sp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def on_semester_changed(self, text):
        self.display_student_performance(text)

    def get_checked_exam_types(self):
        exam_types = []
        if self.prelim_chart.isChecked():
            exam_types.append("PRELIM EXAM")
        if self.midterm_chart.isChecked():
            exam_types.append("MIDTERM EXAM")
        if self.finals_chart.isChecked():
            exam_types.append("FINAL EXAM")
        return exam_types

    def update_bar_graph(self):
        selected_semester = self.sem_sp.currentText() if self.sem_sp else "All"
        checked_exam_types = self.get_checked_exam_types()

        # Filter based on semester and checked exam types
        filtered_results = []
        for exam_id, course, exam_type, semester, total_items, correct_answers in self.exam_data_for_graph:
            if (selected_semester == "All" or selected_semester.lower() == semester.lower()) and \
            (not checked_exam_types or exam_type in checked_exam_types):
                filtered_results.append((exam_id, course, exam_type, semester, total_items, correct_answers))

        layout = self.sp_graph.layout()
        if layout is None:
            layout = QVBoxLayout(self.sp_graph)
            self.sp_graph.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        if not filtered_results:
            message_label = QLabel("No existing data as of the moment.")
            message_label.setAlignment(Qt.AlignCenter)
            message_label.setStyleSheet("font-size: 16px; color: lightgray;")
            layout.addWidget(message_label)
            return

        courses = [result[1] for result in filtered_results]
        correct_answers = [result[5] for result in filtered_results]
        total_items = [result[4] for result in filtered_results]
        percentages = [(ca / ti * 100) if ti else 0 for ca, ti in zip(correct_answers, total_items)]

        bar_set = QBarSet("Performance")
        bar_set.append(percentages)
        bar_set.setColor(QColor("#004953"))  # Midnight green for bars

        bar_series = QBarSeries()
        bar_series.append(bar_set)

        # Apply Cerulean Blue Theme
        chart = QChart()
        chart.setTheme(QChart.ChartThemeBlueCerulean)
        chart.addSeries(bar_series)
        chart.setTitle(f"Student Exam Performance - {selected_semester}")
        chart.setAnimationOptions(QChart.AllAnimations)

        # Axis X
        axis_x = QBarCategoryAxis()
        axis_x.append(courses)
        axis_x.setLabelsBrush(QColor("white"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)

        # Axis Y
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTitleText("Percentage (%)")
        axis_y.setTitleBrush(QColor("white"))
        axis_y.setLabelsBrush(QColor("white"))
        chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(chart_view)


    def update_pie_gauge(self):
        if not hasattr(self, 'exam_data_for_graph') or not self.exam_data_for_graph:
            return

        # Step 1: Aggregate performance per semester
        semester_totals = {}
        for _, _, _, semester, total_items, correct_answers in self.exam_data_for_graph:
            if semester not in semester_totals:
                semester_totals[semester] = {'correct': 0, 'total': 0}
            semester_totals[semester]['correct'] += correct_answers
            semester_totals[semester]['total'] += total_items

        # Step 2: Clear old charts from sp_pie layout
        layout = self.sp_pie.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        else:
            layout = QHBoxLayout(self.sp_pie)
            self.sp_pie.setLayout(layout)

        # Step 3: Create pie chart per semester
        semester_percentages = {}
        for semester, score in semester_totals.items():
            correct = score['correct']
            total = score['total']
            percentage = int((correct / total) * 100) if total else 0
            semester_percentages[semester] = percentage

            # Create pie (donut) series
            series = QPieSeries()
            series.append("Achieved", percentage)
            series.append("Remaining", 100 - percentage)

            # Style the slices
            achieved_slice = series.slices()[0]
            remaining_slice = series.slices()[1]

            achieved_slice.setColor(QColor("green" if percentage >= 75 else "red"))
            achieved_slice.setLabelVisible(False)

            remaining_slice.setColor(QColor("#e0e0e0"))
            remaining_slice.setLabelVisible(False)

            series.setHoleSize(0.6)

            # Create chart
            chart = QChart()
            chart.setTheme(QChart.ChartThemeBlueCerulean)  # Apply Cerulean Blue Theme
            chart.addSeries(series)
            chart.setTitle(f"{semester} - {percentage}%")
            chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.legend().hide()
            chart.setBackgroundVisible(True)
            chart.setContentsMargins(0, 0, 0, 0)
            chart.setMargins(QMargins(0, 0, 0, 0))

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumWidth(200)  # optional, for spacing
            chart_view.setMaximumWidth(300)

            layout.addWidget(chart_view)

        percentages = list(semester_percentages.values())

        if len(percentages) == 2:
            if all(p >= 75 for p in percentages):
                self.perf_message.setText("Great job! You're performing well in most of your exams. Keep it up!")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/20.png"))
            elif any(p >= 75 for p in percentages):
                self.perf_message.setText("You're making progress! One semester went well—keep pushing to improve the other.")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/21.png"))
            else:
                self.perf_message.setText("There's room to grow. Focus on your studies and aim higher next examinations!")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/22.png"))
        elif len(percentages) == 1:
            if percentages[0] >= 75:
                self.perf_message.setText("Strong start! You're off to a great performance this semester. Keep it going!")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/23.png"))
            else:
                self.perf_message.setText("You've made a start—now aim higher in your exams to reach your full potential.")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/24.png"))
        else:
            self.perf_message.setText("No exam performance data available yet.")
            self.icon_label.setPixmap(QPixmap(r"UI/Resources/25.png"))

    def filter_by_exam_type(self, exam_type):
        # Check which checkboxes are selected and filter accordingly
        if self.prelim_chart.isChecked() and "PRELIM" in exam_type:
            return True
        if self.midterm_chart.isChecked() and "MIDTERM" in exam_type:
            return True
        if self.finals_chart.isChecked() and "FINAL" in exam_type:
            return True
        return False

    
    def handle_exam_id_click(self, row, column):
        if column != 0:
            return

        exam_id_item = self.sp_table.item(row, 0)
        if not exam_id_item:
            return

        exam_id = exam_id_item.text()

        # Create the ExamResult instance but do not show it
        exam_result_window = ExamResult(exam_id=exam_id, student_id=self.user_id)
        exam_result_window.hide()  # Ensures the window does not appear

        # Just generate the PDF
        exam_result_window.generate_pdf_report()

    
    def load_user_settings(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT first_name, middle_name, last_name, suffix, birthdate, sex, emailaddress, user_id, profile_image
                    FROM user_account 
                    WHERE user_id = %s
                """
                cursor.execute(query, (self.current_user_id,))
                result = cursor.fetchone()

                if result:
                    # Construct full name
                    name_parts = [
                        result['first_name'],
                        result['middle_name'] if result['middle_name'] not in (None, '', 'None') else '',
                        result['last_name'],
                        result['suffix'] if result['suffix'] not in (None, '', 'None') else ''
                    ]
                    full_name = " ".join(part for part in name_parts if part).upper()

                    # Set values in UI
                    if self.name:
                        self.name.setText(full_name)

                    if self.birthdate:
                        self.birthdate.setText(str(result['birthdate']))

                    if self.sex:
                        self.sex.setText(result['sex'])

                    if self.email:
                        self.email.setText(result['emailaddress'])

                    if self.user_id_label:
                        print("Fetched user ID:", result['user_id'])  # ✅ Debug print
                        self.user_id_label.setText(str(result['user_id']))

                    # === Load and Set Profile Image ===
                    from PySide6.QtGui import QPixmap
                    from PySide6.QtCore import Qt
                    import os

                    profile_path = result.get('profile_image')
                    if profile_path and os.path.exists(profile_path):
                        pixmap = QPixmap(profile_path)
                    else:
                        pixmap = QPixmap("UI/DP/default.png")

                    photo_label = self.findChild(QLabel, "photo_s")
                    if photo_label:
                        photo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))

                else:
                    print(f"No user found with ID {self.current_user_id}")

                cursor.close()
                connection.close()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Database Error", f"Error loading user settings: {err}")

        except Exception as e:
            print(f"Unexpected error: {e}")


    def open_exam_details(self, exam_details):
        self.show_takeexam_page(exam_details)

        # Wait until exams are fully loaded before matching
        QTimer.singleShot(500, lambda: self.match_exam_after_load(exam_details))

    def match_exam_after_load(self, exam_details):
            matched_exam = None

            # Iterate through the categorized exam lists
            for exam_list in [self.take_prelim, self.take_midterm, self.take_finals, self.available_exam_dashboard]:
                for i in range(exam_list.count()):
                    item = exam_list.item(i)
                    full_text = item.text()  # The exam details as shown in the UI

                    # If full_text matches the exam details from the notification
                    if (
                        exam_details["subject_code"] in full_text and
                        exam_details["semester"] in full_text and
                        exam_details["exam_date"] in full_text and
                        exam_details["exam_schedule"] in full_text
                    ):
                        matched_exam = item
                        break

                if matched_exam:
                    # If a match is found, select the item (visually highlight)
                    exam_list.setCurrentItem(matched_exam)
                    return  # Exit after matching
            
            if not matched_exam:
            # Ensure the QMessageBox doesn't appear more than once
                existing_dialogs = QApplication.topLevelWidgets()  # Get all top-level widgets (dialogs)
                if not any(isinstance(d, QMessageBox) for d in existing_dialogs):
                    QMessageBox.information(self, "Exam Already Taken", "This exam has already been taken or is no longer available.")

    def start_time_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) 

    def show_dashboard_page(self):
        if self.student_stacked:
            self.student_stacked.setCurrentIndex(0)
            self.fetch_student_data()
            self.load_student_exams()

        self.filter_available_exam_dashboard(self.available_sort_dashboard.currentText())
        self.filter_upcoming_exam_dashboard(self.upcoming_sort_dashboard.currentText())
        self.filter_missing_exam_dashboard(self.missing_sort_dashboard.currentText())
        self.filter_completed_exam_dashboard(self.completed_sort_dashboard.currentText())

        self.dashboardbtn.setChecked(True)
        self.myperfbtn.setChecked(False)
        self.takeexambtn.setChecked(False)
        

    def show_myperf_page(self):
        if self.student_stacked:
            self.student_stacked.setCurrentIndex(1)
        
        self.dashboardbtn.setChecked(False)
        self.myperfbtn.setChecked(True)
        self.takeexambtn.setChecked(False)

    def show_takeexam_page(self, exam_details=None):
        if self.student_stacked:
            self.student_stacked.setCurrentIndex(2)
            self.load_student_exams()

            if isinstance(exam_details, dict):
                QTimer.singleShot(500, lambda ed=exam_details.copy(): self.match_exam_after_load(ed))

        self.dashboardbtn.setChecked(False)
        self.myperfbtn.setChecked(False)
        self.takeexambtn.setChecked(True)

    def show_settings_page(self):
        if self.student_stacked:
            self.load_user_settings()  # <-- load data
            self.student_stacked.setCurrentIndex(3)

    def show_reset_password_dialog(self):
        loader = QUiLoader()
        reset_password_ui = loader.load(resource_path("UI/reset_password.ui"), self)

        self.reset_dialog = QDialog(self)
        self.reset_dialog.setWindowTitle("Reset Password")
        self.reset_dialog.setModal(True)
        self.reset_dialog.setLayout(QVBoxLayout())
        self.reset_dialog.layout().addWidget(reset_password_ui)

        self.reset_stacked_widget = reset_password_ui.findChild(QStackedWidget, "reset_stackedWidget")

        self.show_blurred_overlay()

        self.enter_email = reset_password_ui.findChild(QLineEdit, "Enter_email")
        self.enter_id = reset_password_ui.findChild(QLineEdit, "enter_ID")
        self.enter_id.textChanged.connect(lambda text: self.enter_id.setText(text.upper()))
        self.enter_OTP = reset_password_ui.findChild(QLineEdit, "enter_OTP")
        self.otp_timer = reset_password_ui.findChild(QLabel, "otp_timer")
        self.old_pass = reset_password_ui.findChild(QLabel, "old_pass")
        self.enter_old = reset_password_ui.findChild(QLineEdit, "enter_old")  
        self.enter_new = reset_password_ui.findChild(QLineEdit, "enter_new")
        self.confirm_new = reset_password_ui.findChild(QLineEdit, "confirm_new")
        self.verify_btn = reset_password_ui.findChild(QPushButton, "verify")
        self.resetpass_btn = reset_password_ui.findChild(QPushButton, "reset_pass") 
        self.resend_otp_btn = reset_password_ui.findChild(QPushButton, "resend_otp")
        self.cancel_btn2 = reset_password_ui.findChild(QPushButton, "cancel_2") 
        self.cancel_btn = reset_password_ui.findChild(QPushButton, "cancel") 
        self.send_otp_btn = reset_password_ui.findChild(QPushButton, "send_OTP")

        self.reset_dialog.finished.connect(self.hide_blurred_overlay)
        self.add_eye_icon(self.enter_old)
        self.add_eye_icon(self.enter_new)
        self.add_eye_icon(self.confirm_new)

        if self.send_otp_btn:
            self.send_otp_btn.clicked.connect(self.send_otp_for_password_reset)

        if self.verify_btn:
            self.verify_btn.clicked.connect(self.verify_otp)
            self.verify_btn.clicked.connect(self.check_otp_input)

        if self.send_otp_btn and self.verify_btn and self.resetpass_btn and self.reset_stacked_widget:
            def enter_pressed_trigger():
                idx = self.reset_stacked_widget.currentIndex()
                if idx == 0:
                    self.send_otp_btn.click()
                elif idx == 1:
                    self.verify_btn.click()
                elif idx == 2:
                    self.resetpass_btn.click()

            enter_shortcut_return = QShortcut(QKeySequence("Return"), reset_password_ui)
            enter_shortcut_return.activated.connect(enter_pressed_trigger)

            enter_shortcut_enter = QShortcut(QKeySequence("Enter"), reset_password_ui)
            enter_shortcut_enter.activated.connect(enter_pressed_trigger)

        if self.resend_otp_btn:
            self.resend_otp_btn.clicked.connect(self.resend_otp)

        if self.cancel_btn:
            self.cancel_btn.clicked.connect(self.close_reset_password_dialog)

        if self.cancel_btn2:
            self.cancel_btn2.clicked.connect(self.close_reset_password_dialog)

        if self.resetpass_btn:
            self.resetpass_btn.clicked.connect(self.verify_pass)

        self.reset_dialog.exec()

    def check_otp_input(self):
        if not self.enter_OTP.text().strip():
            QMessageBox.critical(self, "Error", "Please enter the OTP.")
        else:
            # Proceed with OTP verification
            print("OTP entered:", self.enter_OTP.text())

    def add_eye_icon(self, password_field):
        if password_field:
            show_password_action = QAction(self)
            show_password_action.setIcon(QIcon(r"UI/Resources/hidden.png"))
            
            password_field.addAction(show_password_action, QLineEdit.TrailingPosition)
            password_field.setEchoMode(QLineEdit.Password)
            
            show_password_action.triggered.connect(
                lambda checked=False, field=password_field, action=show_password_action: 
                self.toggle_password_visibility(field, action))

    def toggle_password_visibility(self, password_field, show_password_action):
        if password_field.echoMode() == QLineEdit.Password:
            password_field.setEchoMode(QLineEdit.Normal)
            show_password_action.setIcon(QIcon(r"UI/Resources/show.png"))
        else:
            password_field.setEchoMode(QLineEdit.Password)
            show_password_action.setIcon(QIcon(r"UI/Resources/hidden.png"))

    def show_otp_page(self):
        user_id = self.enter_id.text().strip()
        email = self.enter_email.text().strip()

        if not user_id or not email:
            QMessageBox.warning(self.reset_dialog, "Error", "User ID and Email cannot be empty.")
            return  

        self.reset_stacked_widget.setCurrentIndex(1)

    def show_changepass_page(self):
        if self.reset_stacked_widget:
            self.reset_stacked_widget.setCurrentIndex(2)  
  
    def verify_otp(self):
        entered_otp = self.enter_OTP.text().strip()

        if not self.otp_valid:
            QMessageBox.warning(self.reset_dialog, "OTP Expired", "The OTP has expired. Please request a new one.")
            return

        if not re.fullmatch(r"\d{6}", entered_otp):
            QMessageBox.warning(self.reset_dialog, "Invalid OTP", "OTP must be a 6-digit number.")
            return

        if entered_otp == getattr(self, "generated_otp", None):
            QMessageBox.information(self.reset_dialog, "Success", "OTP Verified!")
            self.countdown_timer.stop()
            self.show_changepass_page()
        else:
            QMessageBox.warning(self.reset_dialog, "Error", "Incorrect OTP. Please try again.")

    def resend_otp(self):
        email = self.enter_email.text().strip()

        if not email:
            QMessageBox.warning(self.reset_dialog, "Error", "Email address cannot be empty.")
            return

        otp = self.generate_otp()
        self.generated_otp = otp
        self.send_otp_email(email, otp)
        self.start_otp_timer()

        QMessageBox.information(self.reset_dialog, "OTP Resent", "A new OTP has been sent to your email.")

    def verify_pass(self):
        entered_old_pass = self.enter_old.text().strip()
        entered_new_pass = self.enter_new.text().strip()
        entered_confirm_pass = self.confirm_new.text().strip()

        if not entered_old_pass or not entered_new_pass or not entered_confirm_pass:
            QMessageBox.warning(self.reset_dialog, "Error", "All fields must be filled.")
            return

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            # Fetch the current hashed password from the database
            cursor.execute("SELECT password FROM user_account WHERE user_id = %s", (self.enter_id.text().strip(),))
            result = cursor.fetchone()

            if result:
                hashed_password = result[0]

                # Check if the entered old password matches the hashed password
                if not bcrypt.checkpw(entered_old_pass.encode('utf-8'), hashed_password.encode('utf-8')):
                    QMessageBox.warning(self.reset_dialog, "Error", "Old password is incorrect.")
                    return

                # Check if the new password matches the old password
                if entered_new_pass == entered_old_pass:
                    QMessageBox.warning(self.reset_dialog, "Error", "Please create a new password that is different from the old password.")
                    return

                # Proceed to check if new passwords match
                if entered_new_pass != entered_confirm_pass:
                    QMessageBox.warning(self.reset_dialog, "Error", "New passwords do not match.")
                    return

                if not self.is_strong_password(entered_new_pass):
                    QMessageBox.warning(self.reset_dialog, "Error", "Password must be at least 8 characters long, contain both upper and lowercase letters, and atleast one number.")
                    return

                # Hash the new password and update it in the database
                new_hashed_password = self.hash_password(entered_new_pass)
                cursor.execute("UPDATE user_account SET password = %s WHERE user_id = %s", (new_hashed_password, self.enter_id.text().strip()))
                connection.commit()

                QMessageBox.information(self.reset_dialog, "Success", "Password changed successfully!")
                self.reset_dialog.close()

            else:
                QMessageBox.warning(self.reset_dialog, "Error", "User  ID does not exist.")

        except mysql.connector.Error as e:
            QMessageBox.warning(self.reset_dialog, "Error", f"An error occurred while updating your password: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def is_strong_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):  
            return False
        if not re.search(r"[a-z]", password): 
            return False
        if not re.search(r"[0-9]", password):  
            return False
        return True


    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password
        
    def start_otp_timer(self):
            self.remaining_time = 60
            self.otp_valid = True
            self.otp_timer.setText(f"OTP valid for: {self.remaining_time} seconds")

            self.resend_otp_btn.setVisible(False)  # 🔴 Hide the resend button during countdown

            if hasattr(self, "countdown_timer") and self.countdown_timer.isActive():
                self.countdown_timer.stop()

            self.countdown_timer = QTimer()
            self.countdown_timer.timeout.connect(self.update_otp_timer)
            self.countdown_timer.start(1000)

    def update_otp_timer(self):
            self.remaining_time -= 1
            if self.remaining_time <= 0:
                self.countdown_timer.stop()
                self.otp_valid = False
                self.otp_timer.setText("OTP expired.")
                self.resend_otp_btn.setVisible(True)

                if self.reset_dialog.isVisible():  # ✅ Only show the message box if dialog is still open
                    QMessageBox.information(self.reset_dialog, "OTP Expired", "The OTP has expired. Please request a new one.")
            else:
                self.otp_timer.setText(f"OTP valid for: {self.remaining_time} seconds")


    def get_db_connection(self):
        return mysql.connector.connect(
            host="localhost",  
            user="root",  
            password="TUPCcoet@23!",  
            database="axis"  
        )

    def send_otp_email(self, user_email, otp):
        try:
            sender_email = "axistupcems@gmail.com"
            password = "ajiu rivz ttgw lzka"

            message = MIMEMultipart("alternative")
            message["From"] = sender_email
            message["To"] = user_email
            message["Subject"] = "Password Reset Request"

            html_body = f"""\
            <html>
                <body>
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Please use the following One-Time Password (OTP) to proceed with the password reset process:</p>
                    <p style="font-size: 24px; color: red; font-weight: bold;">{otp}</p>
                    <p>This OTP is valid for <strong>1 minute only</strong>.</p>
                    <p>If you did not request this change, please ignore this email or contact support immediately.</p>
                    <p>Thank you,<br>Axis Support Team</p>
                </body>
            </html>
            """
            message.attach(MIMEText(html_body, "html"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, user_email, message.as_string())
            server.quit()

            print("OTP email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")


    def generate_otp(self):
        return str(random.randint(100000, 999999))  

    def send_otp_for_password_reset(self):
        user_id = self.enter_id.text().strip()
        email = self.enter_email.text().strip()

        if not user_id or not email:
            QMessageBox.warning(self.reset_dialog, "Error", "User ID and Email cannot be empty.")
            return

        if user_id != self.user_id_label.text().strip():
            QMessageBox.warning(self.reset_dialog, "Error", "User ID does not match your account.")
            return

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT emailaddress FROM user_account WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self.reset_dialog, "Error", "User ID does not exist in the database.")
                return

            db_email = result[0]
            if email != db_email:
                QMessageBox.warning(self.reset_dialog, "Error", "Email does not match the registered email for this User ID.")
                return

            # All checks passed — show loading dialog now
            loading_dialog = QProgressDialog("Sending OTP email...", None, 0, 0, self.reset_dialog)
            loading_dialog.setWindowTitle("Please Wait")
            loading_dialog.setWindowModality(Qt.ApplicationModal)
            loading_dialog.setCancelButton(None)
            loading_dialog.setMinimumDuration(0)  # Optional: ensure it's visible
            loading_dialog.show()
            QApplication.processEvents()

            otp = self.generate_otp()
            self.generated_otp = otp
            self.send_otp_email(email, otp)
            self.start_otp_timer()

            self.reset_stacked_widget.setCurrentIndex(1)
            loading_dialog.cancel()
            QMessageBox.information(self.reset_dialog, "OTP Sent", "An OTP has been sent to your email.")

        except mysql.connector.Error as e:
            QMessageBox.warning(self.reset_dialog, "Error", f"An error occurred while checking your account: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def close_reset_password_dialog(self):
        if hasattr(self, 'reset_dialog') and self.reset_dialog:
            self.reset_dialog.close()
    
    def show_blurred_overlay(self):
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        self.overlay.setGeometry(self.rect())
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.show()

    def hide_blurred_overlay(self):
        if hasattr(self, "overlay"):
            self.overlay.deleteLater()
            del self.overlay

    def show_notification_dialog(self):
        self.show_blurred_overlay()
        self.notification.show_dialog()

    def logout(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Logout Confirmation")
        msg_box.setText("Are you sure you want to log out?")
        msg_box.setIcon(QMessageBox.Question)
        
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)  

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            self.login_window = Login_Register()  
            self.login_window.show()
            self.hide() 

            
class Faculty(QMainWindow):
    def __init__(self, user_id, semester=None, exam_type=None):
        super().__init__()
        if not isinstance(user_id, str) or not user_id.startswith("TUPC-F"):
            raise ValueError("Invalid user_id provided to Faculty class")

        self.user_id = user_id
        self.semester = semester
        self.exam_type = exam_type
        self.current_user_id = self.user_id
        self.selected_exam_type_filter = None
        self.class_standing_data = []

        loader = QUiLoader()
        self.faculty_ui = loader.load(resource_path("UI/Faculty.ui"), self)
        self.load_exam_lists()

        Icons(self.faculty_ui)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.faculty_ui)
        self.setCentralWidget(self.stacked_widget)
        self.showMaximized()

        self.faculty_stacked = self.faculty_ui.findChild(QStackedWidget, "faculty_stackedWidget")

        self.timedb = self.faculty_ui.findChild(QLabel, "time_dashboard")
        self.start_time_update()

        self.name = self.faculty_ui.findChild(QLabel, "name")
        self.department = self.faculty_ui.findChild(QLabel, "department")
        self.birthdate = self.faculty_ui.findChild(QLabel, "birthdate")
        self.sex = self.faculty_ui.findChild(QLabel, "sex")
        self.email = self.faculty_ui.findChild(QLabel, "email")
        self.user_id_label = self.faculty_ui.findChild(QLabel, "user_id_label")

        self.dashboardbtn = self.faculty_ui.findChild(QPushButton, "dashboard_btn")
        self.classbtn = self.faculty_ui.findChild(QPushButton, "class_btn")
        self.examinationbtn = self.faculty_ui.findChild(QPushButton, "examination_btn")
        self.createexambtn = self.faculty_ui.findChild(QPushButton, "createexam_btn")
        self.backbtn = self.faculty_ui.findChild(QPushButton, "back_btn")
        self.continue_2 = self.faculty_ui.findChild(QPushButton, "continue_2")
        self.studentstatsbtn = self.faculty_ui.findChild(QPushButton, "studentstats_btn")
        self.notifbtn = self.faculty_ui.findChild(QPushButton, "notif_btn")
        self.settingsbtn = self.faculty_ui.findChild(QPushButton, "settings_btn")
        self.cpbtn = self.faculty_ui.findChild(QPushButton, "change_password_settings")
        self.logoutbtn = self.faculty_ui.findChild(QPushButton, "logout_btn")
        self.edit_exam = self.faculty_ui.findChild(QPushButton, "edit")
        self.delete_exam = self.faculty_ui.findChild(QPushButton, "delete_2")
        self.assigned_tab = self.findChild(QTabWidget, "assigned_tab")
        self.exam_type_filter = self.findChild(QComboBox, "exam_type_filter")
        self.exam_type_filter_2 = self.findChild(QComboBox, "exam_type_filter_2")
        self.table_assigned_exam = self.findChild(QListWidget, "table_assigned_exam")
        self.table_assigned_exam_2 = self.findChild(QListWidget, "table_assigned_exam_2")
        
        self.countdown_timer = QTimer()

        self.dashboardbtn.clicked.connect(self.show_dashboard_page)
        self.dashboardbtn.setChecked(True)
        self.studentstatsbtn.clicked.connect(self.show_studperf_page)
        self.classbtn.clicked.connect(self.show_class_page)
        self.examinationbtn.clicked.connect(self.show_exams_page)
        self.createexambtn.clicked.connect(self.show_createexam_page)
        self.backbtn.clicked.connect(self.show_exams_page)
        self.settingsbtn.clicked.connect(self.show_settings_page)
        self.cpbtn.clicked.connect(self.show_reset_password_dialog)
        self.logoutbtn.clicked.connect(self.logout)
        self.continue_2.clicked.connect(self.open_exam_template)

        self.major_exam = self.faculty_ui.findChild(QComboBox, "major_exam")
        self.semester = self.faculty_ui.findChild(QComboBox, "semester")
        self.subject_code = self.faculty_ui.findChild(QComboBox, "subject_code")
        self.part_1 = self.faculty_ui.findChild(QCheckBox, "part_1")
        self.type_exam_1 = self.faculty_ui.findChild(QComboBox, "type_exam_1")
        self.number_item_1 = self.faculty_ui.findChild(QComboBox, "number_item_1")
        self.part_2 = self.faculty_ui.findChild(QCheckBox, "part_2")
        self.type_exam_2 = self.faculty_ui.findChild(QComboBox, "type_exam_2")
        self.number_item_2 = self.faculty_ui.findChild(QComboBox, "number_item_2")
        self.part_3 = self.faculty_ui.findChild(QCheckBox, "part_3")
        self.type_exam_3 = self.faculty_ui.findChild(QComboBox, "type_exam_3")
        self.number_item_3 = self.faculty_ui.findChild(QComboBox, "number_item_3")

        self.data1_tabs = self.faculty_ui.findChild(QFrame, "data1_tabs")
        self.data2_tabs = self.faculty_ui.findChild(QFrame, "data2_tabs")
        self.data3 = self.faculty_ui.findChild(QFrame, "data3")

        self.exam_draft_table = self.faculty_ui.findChild(QListWidget, "exam_draft_table")
        self.exam_published_table = self.faculty_ui.findChild(QListWidget, "exam_published_table")

        self.notifbtn.clicked.connect(self.show_notification_dialog)
        self.notification = NotificationManager(self)
        self.notification.load_notifications(role="faculty", user_id=self.user_id)
        self.notification.dialog.finished.connect(self.hide_blurred_overlay)
        self.day = self.faculty_ui.findChild(QLabel, "day")
        self.date = self.faculty_ui.findChild(QLabel, "date")
        self.greetings = self.faculty_ui.findChild(QLabel, "greetings")
        self.analog_clock = self.faculty_ui.findChild(QFrame, "Analogclock")
        self.calendar_widget = self.faculty_ui.findChild(QCalendarWidget, "calendar")

        layout = QVBoxLayout(self.analog_clock)
        layout.setContentsMargins(0, 0, 0, 0)
        self.clock_widget = AnalogClock()
        layout.addWidget(self.clock_widget)

        today_format = QTextCharFormat()
        today_format.setForeground(QColor("#ff3b30"))     # Match your theme
        today_format.setFontWeight(QFont.Bold)
        self.calendar_widget.setDateTextFormat(QDate.currentDate(), today_format)

        self.edit_exam.clicked.connect(self.edit_selected_exam)
        self.delete_exam.clicked.connect(self.delete_selected_exam)


        self.assigned_tab.setTabText(0, "1st Semester")
        self.assigned_tab.setTabText(1, "2nd Semester")

        self.exam_type_filter.currentTextChanged.connect(
            lambda value: self.filter_assigned_exams("1st Semester", value)
        )

        self.exam_type_filter_2.currentTextChanged.connect(
            lambda value: self.filter_assigned_exams("2nd Semester", value)
        )

        self.filter_assigned_exams(self.semester, self.exam_type)

        self.setup_exam_form_logic()
        self.fetch_faculty_data()
        self.update_exam_parts_visibility()
    
    def adjust_column_widths_to_header(self, table):
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def start_time_update(self):
        self.update_time()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  

    def fetch_faculty_data(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                query = """
                    SELECT user_id, first_name, last_name, middle_name, suffix, department, profile_image
                    FROM user_account 
                    WHERE user_id = %s
                """
                cursor.execute(query, (self.current_user_id,))
                faculty_data = cursor.fetchone()
                
                if faculty_data:
                    name_parts = []
                    if faculty_data['first_name']:
                        name_parts.append(faculty_data['first_name'])
                    if faculty_data['middle_name'] and faculty_data['middle_name'] != "None":
                        name_parts.append(faculty_data['middle_name'])
                    if faculty_data['last_name']:
                        name_parts.append(faculty_data['last_name'])
                    if faculty_data['suffix'] and faculty_data['suffix'] != "None":
                        name_parts.append(faculty_data['suffix'])
                    
                    full_name = " ".join(name_parts).upper()

                    name_label = self.faculty_ui.findChild(QLabel, "name_dashboard")
                    user_id_label = self.faculty_ui.findChild(QLabel, "user_id_dashboard")
                    department_label = self.faculty_ui.findChild(QLabel, "department_label")

                    if name_label:
                        name_label.setText(full_name)
                    if user_id_label:
                        user_id_label.setText(faculty_data['user_id'])
                    if department_label:
                        department_label.setText(faculty_data['department'])

                    # === Set Profile Picture ===
                    from PySide6.QtGui import QPixmap
                    from PySide6.QtCore import Qt
                    import os

                    profile_path = faculty_data.get('profile_image')
                    if profile_path and os.path.exists(profile_path):
                        pixmap = QPixmap(profile_path)
                    else:
                        pixmap = QPixmap("UI/DP/default.png")

                    self.profile_image = self.faculty_ui.findChild(QLabel, "photo_f")
                    if self.profile_image:
                        self.profile_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

                cursor.execute("SELECT COUNT(*) as count FROM user_account WHERE role = 'STUDENT' AND status = 'approved'")
                student_result = cursor.fetchone()
                student_count = student_result['count'] if student_result else 0
                student_total_label = self.faculty_ui.findChild(QLabel, "total_student_dashboard")
                if student_total_label:
                    student_total_label.setText(str(student_count))

                self.setup_assigned_exam_dashboard(cursor)
                self.setup_exam_tracking(cursor)

                cursor.close()
                connection.close()

        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def setup_assigned_exam_dashboard(self, cursor):
        try:
            self.assigned_tab.setTabText(0, "1st Semester")
            self.assigned_tab.setTabText(1, "2nd Semester")

            self.table_assigned_exam_1 = self.faculty_ui.findChild(QListWidget, "table_assigned_exam")
            self.exam_type_filter_1 = self.faculty_ui.findChild(QComboBox, "exam_type_filter")
            self.table_assigned_exam_2 = self.faculty_ui.findChild(QListWidget, "table_assigned_exam_2")
            self.exam_type_filter_2 = self.faculty_ui.findChild(QComboBox, "exam_type_filter_2")

            for list_widget in [self.table_assigned_exam_1, self.table_assigned_exam_2]:
                if list_widget:
                    list_widget.setStyleSheet("""
                        QListWidget {
                            background-color: #0F3D3E;
                            border: none;
                        }
                    """)
                    list_widget.setSpacing(8)

            for combo in [self.exam_type_filter_1, self.exam_type_filter_2]:
                if combo:
                    combo.clear()
                    combo.addItems(["PRELIM EXAM", "MIDTERM EXAM", "FINAL EXAM"])
                    combo.setCurrentIndex(0)  # Set to PRELIM EXAM by default

            try:
                self.exam_type_filter_1.currentTextChanged.disconnect()
            except:
                pass
            self.exam_type_filter_1.currentTextChanged.connect(lambda val: self.filter_assigned_exams("1st Semester", val))

            try:
                self.exam_type_filter_2.currentTextChanged.disconnect()
            except:
                pass
            self.exam_type_filter_2.currentTextChanged.connect(lambda val: self.filter_assigned_exams("2nd Semester", val))

            user_id = getattr(self, 'user_id', None)
            if user_id is None:
                user_id = getattr(self, 'current_user_id', None)
            if user_id is None:
                print("Warning: No user ID found. Using empty string.")
                user_id = ""

            cursor.execute("""
                SELECT ef.subject_code, ef.major_exam_type, ef.exam_id, ef.semester,
                    COUNT(DISTINCT sa.student_id) AS done_count
                FROM examination_form ef
                LEFT JOIN student_answers sa ON ef.exam_id = sa.exam_id
                WHERE ef.created_by = %s AND ef.exam_status = 'Published'
                GROUP BY ef.subject_code, ef.major_exam_type, ef.exam_id, ef.semester
            """, (user_id,))
            results = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total_students FROM user_account WHERE role = 'STUDENT' AND status = 'approved'")
            total_students = cursor.fetchone()['total_students']

            self.semester_data = {'1st Semester': [], '2nd Semester': []}
            for row in results:
                semester = row['semester']
                if semester not in self.semester_data:
                    continue
                row['undone_count'] = total_students - (row['done_count'] or 0)
                self.semester_data[semester].append(row)

            # Load with PRELIM EXAM by default for both semesters
            self.filter_assigned_exams("1st Semester", self.exam_type_filter_1.currentText())
            self.filter_assigned_exams("2nd Semester", self.exam_type_filter_2.currentText())

        except Exception as e:
            print(f"Error in setup_assigned_exam_dashboard: {e}")
            import traceback
            traceback.print_exc()


    def filter_assigned_exams(self, semester: str, exam_type: str):
        try:
            if not hasattr(self, 'semester_data') or not self.semester_data or semester not in self.semester_data:
                print(f"No data available for {semester}")
                return

            if semester == "1st Semester":
                list_widget = self.table_assigned_exam_1
            elif semester == "2nd Semester":
                list_widget = self.table_assigned_exam_2
            else:
                return

            list_widget.clear()

            # Filter data by specific exam type only (no more "All" option)
            filtered_data = [
                item for item in self.semester_data[semester]
                if item['major_exam_type'] == exam_type
            ]

            grouped = {}
            for item in filtered_data:
                subject_code = item['subject_code']
                if subject_code not in grouped:
                    grouped[subject_code] = {'done_count': 0, 'undone_count': 0}
                grouped[subject_code]['done_count'] += item['done_count'] or 0
                grouped[subject_code]['undone_count'] += item['undone_count'] or 0

            for subject_code, data in grouped.items():
                container = QWidget()
                container.setStyleSheet("""
                    QWidget {
                        background: #ECF0F1;
                        border-radius: 16px;
                        border: 1px solid #D5D8DC;
                        padding: 10px;
                    }
                """)
                layout = QHBoxLayout(container)
                layout.setContentsMargins(12, 4, 12, 4)
                layout.setSpacing(12)

                subject_label = QLabel(subject_code)
                subject_label.setStyleSheet("""
                    QLabel {
                        color: #2C3E50;
                        font-weight: 700;
                        font-size: 15px;
                        min-width: 80px;
                    }
                """)
                layout.addWidget(subject_label)

                done_pill = QLabel(f"{data['done_count']} Done")
                done_pill.setAlignment(Qt.AlignCenter)
                done_pill.setStyleSheet("""
                    QLabel {
                        background: #D5D8DC;
                        color: #004953;
                        border-radius: 16px;
                        font-weight: bold;
                        font-size: 14px;
                        min-width: 100px;
                        padding: 6px 0;
                    }
                """)
                layout.addWidget(done_pill)

                not_done_pill = QLabel(f"{data['undone_count']} Not Done")
                not_done_pill.setAlignment(Qt.AlignCenter)
                not_done_pill.setStyleSheet("""
                    QLabel {
                        background: #D5D8DC;
                        color: #004953;
                        border-radius: 16px;
                        font-weight: bold;
                        font-size: 14px;
                        min-width: 100px;
                        padding: 6px 0;
                    }
                """)
                layout.addWidget(not_done_pill)

                item = QListWidgetItem()
                item.setSizeHint(QSize(list_widget.width() - 40, 48))
                list_widget.addItem(item)
                list_widget.setItemWidget(item, container)

            if list_widget.count() == 0:
                no_data_widget = QWidget()
                no_data_layout = QVBoxLayout(no_data_widget)
                no_data_label = QLabel(f"No subjects found for {exam_type}")
                no_data_label.setStyleSheet("color: white; font-size: 14px; font-style: italic;")
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_layout.addWidget(no_data_label)
                no_data_layout.setAlignment(Qt.AlignCenter)
                item = QListWidgetItem()
                item.setSizeHint(QSize(list_widget.width() - 40, 48))
                list_widget.addItem(item)
                list_widget.setItemWidget(item, no_data_widget)

        except Exception as e:
            import traceback
            traceback.print_exc()

    def setup_exam_tracking(self, cursor):
        assigned_exam_dashboard = self.faculty_ui.findChild(QComboBox, "assigned_exam_dashboard")
        done_dashboard = self.faculty_ui.findChild(QLabel, "done_dashboard")
        not_done_dashboard = self.faculty_ui.findChild(QLabel, "not_done_dashboard")
        
        if assigned_exam_dashboard:
            assigned_exam_dashboard.clear()
            
            query = """
                SELECT DISTINCT major_exam_type 
                FROM examination_form 
                WHERE created_by = %s 
                AND exam_status = 'published'
                ORDER BY CASE 
                    WHEN major_exam_type = 'PRELIM EXAM' THEN 1
                    WHEN major_exam_type = 'MIDTERM EXAM' THEN 2
                    WHEN major_exam_type = 'FINALS EXAM' THEN 3
                    ELSE 4
                END
            """
            cursor.execute(query, (self.current_user_id,))
            available_exam_types = cursor.fetchall()
            
            if available_exam_types:
                for exam_type in available_exam_types:
                    assigned_exam_dashboard.addItem(exam_type['major_exam_type'])
                
                assigned_exam_dashboard.currentTextChanged.connect(
                    lambda: self.update_exam_stats(assigned_exam_dashboard.currentText(), done_dashboard, not_done_dashboard)
                )
                
                current_exam_type = assigned_exam_dashboard.currentText()
                self.update_exam_stats(current_exam_type, done_dashboard, not_done_dashboard)
            else:
                if done_dashboard:
                    done_dashboard.setText("0 Done")
                if not_done_dashboard:
                    not_done_dashboard.setText("0 Not Done")

    def update_exam_stats(self, exam_type, done_label, not_done_label):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                
                student_query = """
                    SELECT COUNT(*) as total_students
                    FROM user_account
                    WHERE role = 'STUDENT' AND status = 'approved'
                """
                cursor.execute(student_query)
                result = cursor.fetchone()
                total_students = result['total_students'] if result else 0
                
                query = """
                    SELECT COUNT(DISTINCT sa.student_id) as completed_count
                    FROM examination_form ef
                    JOIN student_answers sa ON ef.exam_id = sa.exam_id
                    WHERE ef.created_by = %s AND ef.major_exam_type = %s AND ef.exam_status = 'Published'
                """
                cursor.execute(query, (self.current_user_id, exam_type))
                result = cursor.fetchone()
                
                done_count = result['completed_count'] if result else 0
                
                not_done_count = max(0, total_students - done_count)

                if done_label:
                    done_label.setText(f"{done_count} Done")
                if not_done_label:
                    not_done_label.setText(f"{not_done_count} Not Done")
                
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"Error in update_exam_stats: {e}")
            import traceback
            traceback.print_exc()

    def is_valid_user_id(self, user_id):
        return isinstance(user_id, int) and user_id > 0

    def reset_exam_form_visibility(self):
        self.major_exam.setVisible(True)
        self.semester.setVisible(False)
        self.subject_code.setVisible(False)
        for part in [(self.part_1, self.type_exam_1, self.number_item_1),
                     (self.part_2, self.type_exam_2, self.number_item_2),
                     (self.part_3, self.type_exam_3, self.number_item_3)]:
            part[0].setVisible(False)
            part[1].setVisible(False)
            part[2].setVisible(False)

    def update_exam_parts_visibility(self):
        if self.faculty_stacked.currentIndex() != 4:
            return

        # Block signals during visibility updates
        widgets_to_block = [
            self.major_exam, self.semester, self.subject_code,
            self.part_1, self.type_exam_1, self.number_item_1,
            self.part_2, self.type_exam_2, self.number_item_2,
            self.part_3, self.type_exam_3, self.number_item_3
        ]
        
        # Block all signals first
        for widget in widgets_to_block:
            widget.blockSignals(True)
            
        try:
            major_selected = self.major_exam.currentIndex() != 0
            self.semester.setVisible(major_selected)
            self.subject_code.setVisible(major_selected)

            subject_selected = major_selected and self.subject_code.currentIndex() > 0
            self.part_1.setVisible(subject_selected)

            part1_checked = subject_selected and self.part_1.isChecked()
            self.type_exam_1.setVisible(part1_checked)
            self.number_item_1.setVisible(part1_checked)

            part_1_complete = part1_checked and \
                            self.type_exam_1.currentIndex() != 0 and \
                            self.number_item_1.currentIndex() != 0

            self.part_2.setVisible(part_1_complete)

            part2_checked = part_1_complete and self.part_2.isChecked()
            self.type_exam_2.setVisible(part2_checked)
            self.number_item_2.setVisible(part2_checked)

            part_2_complete = part2_checked and \
                            self.type_exam_2.currentIndex() != 0 and \
                            self.number_item_2.currentIndex() != 0

            self.part_3.setVisible(part_2_complete)

            part3_checked = part_2_complete and self.part_3.isChecked()
            self.type_exam_3.setVisible(part3_checked)
            self.number_item_3.setVisible(part3_checked)
        finally:
            # Unblock all signals after visibility updates
            for widget in widgets_to_block:
                widget.blockSignals(False)
        
        # Call update_exam_type_options without blocking signals
        QApplication.processEvents()

    def update_exam_type_options(self):
        """Update available exam types to prevent duplicates"""
        type_options = ["--- TYPE OF EXAM ---", "MULTIPLE CHOICES", "TRUE OR FALSE", "IDENTIFICATION"]

        # Create a clean collection of selected types
        selected_types = {}
        combo_boxes = [
            (self.part_1.isChecked(), self.type_exam_1),
            (self.part_2.isChecked(), self.type_exam_2),
            (self.part_3.isChecked(), self.type_exam_3)
        ]
        
        # First pass: collect current values
        for is_checked, combo in combo_boxes:
            if is_checked and combo.currentIndex() > 0:
                selected_types[id(combo)] = combo.currentText()
        
        # Second pass: update combo boxes
        for is_checked, combo in combo_boxes:
            if not is_checked:
                continue
                
            # Remember current value and index
            current_value = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(type_options[0])
            
            # Add available options (not used by other combos or currently selected in this combo)
            for opt in type_options[1:]:
                if opt not in selected_types.values() or selected_types.get(id(combo)) == opt:
                    combo.addItem(opt)
            
            # Restore previous selection if possible
            index = combo.findText(current_value)
            combo.setCurrentIndex(index if index >= 0 else 0)
            combo.blockSignals(False)

    def update_subject_code_options(self):
        """Update subject code options based on major exam and semester"""
        # Store current value before clearing
        current_text = self.subject_code.currentText()
        
        # Get available subjects based on semester
        first_sem_subjects = ["CPET3", "CPET3L", "CPET4", "CPET5L", "CPET6", "GEC5", "GEC8", "GEM14", "PATHFIT3"]
        second_sem_subjects = ["CPET10", "CPET7L", "CPET8", "CPET8L", "CPET9", "CPET9L", "GEC3", "GEE11A", "PATHFIT4"]
        
        available_subjects = []
        if self.semester.currentIndex() == 1:
            available_subjects = first_sem_subjects[:]
        elif self.semester.currentIndex() == 2:
            available_subjects = second_sem_subjects[:]
        
        # If no semester selected or no major exam, just clear and exit
        if not available_subjects or self.major_exam.currentIndex() == 0:
            self.subject_code.blockSignals(True)
            self.subject_code.clear()
            self.subject_code.addItem("--- SUBJECT CODE ---")
            self.subject_code.blockSignals(False)
            return
        
        selected_major_exam = self.major_exam.currentText()
        semester_text = self.semester.currentText()
        
        # Block signals during update
        self.subject_code.blockSignals(True)
        
        try:
            # Connect to database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor()
                
                # Improved query with semester condition
                query = """
                    SELECT DISTINCT subject_code 
                    FROM examination_form 
                    WHERE major_exam_type = %s AND semester = %s
                """
                cursor.execute(query, (selected_major_exam, semester_text))
                used_subjects = [row[0] for row in cursor.fetchall()]
                
                # Filter out already used subjects
                filtered_subjects = [subj for subj in available_subjects if subj not in used_subjects]
                
                # Update the combo box
                self.subject_code.clear()
                self.subject_code.addItem("--- SUBJECT CODE ---")
                self.subject_code.addItems(filtered_subjects)
                
                # Try to restore previous selection if still valid
                index = self.subject_code.findText(current_text)
                if index >= 0:
                    self.subject_code.setCurrentIndex(index)
                else:
                    self.subject_code.setCurrentIndex(0)
                    
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        
        finally:
            # Always close database connection
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
            
            # Always unblock signals
            self.subject_code.blockSignals(False)

    def setup_exam_form_logic(self):
        """Connect all signals for combo box updates"""
        # First disconnect any existing connections to avoid duplicates
        try:
            self.major_exam.currentIndexChanged.disconnect()
            self.semester.currentIndexChanged.disconnect()
            self.subject_code.currentIndexChanged.disconnect()
            self.part_1.stateChanged.disconnect()
            self.part_2.stateChanged.disconnect() 
            self.part_3.stateChanged.disconnect()
            self.type_exam_1.currentIndexChanged.disconnect()
            self.type_exam_2.currentIndexChanged.disconnect()
            self.type_exam_3.currentIndexChanged.disconnect()
            self.number_item_1.currentIndexChanged.disconnect()
            self.number_item_2.currentIndexChanged.disconnect()
            self.number_item_3.currentIndexChanged.disconnect()
        except:
            # Ignore errors if connections don't exist
            pass
            
        # Reset the form
        self.reset_exam_form_visibility()
        
        # Connect signals in proper order
        self.major_exam.currentIndexChanged.connect(lambda: self.handle_combo_change("major"))
        self.semester.currentIndexChanged.connect(lambda: self.handle_combo_change("semester"))
        self.subject_code.currentIndexChanged.connect(lambda: self.handle_combo_change("subject"))
        
        self.part_1.stateChanged.connect(lambda: self.handle_combo_change("part1"))
        self.part_2.stateChanged.connect(lambda: self.handle_combo_change("part2"))
        self.part_3.stateChanged.connect(lambda: self.handle_combo_change("part3"))
        
        self.type_exam_1.currentIndexChanged.connect(lambda: self.handle_combo_change("type1"))
        self.type_exam_2.currentIndexChanged.connect(lambda: self.handle_combo_change("type2"))
        self.type_exam_3.currentIndexChanged.connect(lambda: self.handle_combo_change("type3"))
        
        self.number_item_1.currentIndexChanged.connect(lambda: self.handle_combo_change("num1"))
        self.number_item_2.currentIndexChanged.connect(lambda: self.handle_combo_change("num2"))
        self.number_item_3.currentIndexChanged.connect(lambda: self.handle_combo_change("num3"))

    def handle_combo_change(self, source):
        """Central handler for all combo box changes"""
        # Process different update sequences based on which combo changed
        if source == "major":
            if self.major_exam.currentIndex() == 0:
                # Reset downstream combos if major is reset
                self.semester.setCurrentIndex(0)
                self.subject_code.clear()
                self.subject_code.addItem("--- SUBJECT CODE ---")
            self.update_exam_parts_visibility()
            
        elif source == "semester":
            # Update subject codes when semester changes
            self.update_subject_code_options()
            self.update_exam_parts_visibility()
            
        elif source == "subject" or source.startswith("part") or source.startswith("type") or source.startswith("num"):
            # These all affect visibility and available options
            self.update_exam_parts_visibility()
            self.update_exam_type_options()
            
        # Process all events to ensure UI is updated
        QApplication.processEvents()
        
        # Initial update
        QTimer.singleShot(100, self.refresh_all_comboboxes)

    def on_major_exam_changed(self, index):
        if index == 0:
            # If "--- SELECT ---" is chosen, reset semester and subject
            self.semester.setCurrentIndex(0)
            self.subject_code.clear()
            self.subject_code.addItem("--- SUBJECT CODE ---")
        
        # Only update visibility first, wait for semester to update subject codes
        self.update_exam_parts_visibility()
    
    def on_semester_changed(self, index):
        # Update subject codes based on new semester selection
        self.update_subject_code_options()
        # Then update visibility based on new state
        self.update_exam_parts_visibility()

    def is_exam_form_complete(self):
        if self.major_exam.currentIndex() == 0 or self.semester.currentIndex() == 0 or self.subject_code.currentIndex() == 0:
            return False  

        if not self.part_1.isChecked():
            return False
        if self.type_exam_1.currentIndex() == 0 or self.number_item_1.currentIndex() == 0:
            return False

        if self.part_2.isChecked():
            if self.type_exam_2.currentIndex() == 0 or self.number_item_2.currentIndex() == 0:
                return False

        if self.part_3.isChecked():
            if self.type_exam_3.currentIndex() == 0 or self.number_item_3.currentIndex() == 0:
                return False

        return True

    def save_exam_form_to_database(self):
        if not self.current_user_id or self.current_user_id is False:
            QMessageBox.critical(self, "Error", "Invalid user ID. Please log out and log in again.")
            return None
        
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor()
                
                cursor.execute("SELECT user_id FROM user_account WHERE user_id = %s", (self.current_user_id,))
                user_exists = cursor.fetchone()
                if not user_exists:
                    QMessageBox.critical(self, "Error", f"User ID {self.current_user_id} does not exist in the database.")
                    return None

                cursor.execute("SELECT MAX(CAST(SUBSTRING(exam_id, 3) AS UNSIGNED)) FROM examination_form")
                result = cursor.fetchone()

                next_num = 1 if result[0] is None else result[0] + 1
                next_id = f"EX{next_num:03d}"

                major_exam_type = self.major_exam.currentText()
                semester = self.semester.currentText()
                subject_code = self.subject_code.currentText()

                exam_parts = []
                if self.part_1.isChecked():
                    exam_parts.append(("Part 1", self.type_exam_1.currentText(), self.number_item_1.currentText()))
                if self.part_2.isChecked():
                    exam_parts.append(("Part 2", self.type_exam_2.currentText(), self.number_item_2.currentText()))
                if self.part_3.isChecked():
                    exam_parts.append(("Part 3", self.type_exam_3.currentText(), self.number_item_3.currentText()))

                insert_query = """
                    INSERT INTO examination_form (
                        exam_id,
                        major_exam_type,
                        semester,
                        subject_code,
                        exam_part,
                        number_of_items,
                        exam_type,
                        exam_status,
                        created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                for part_name, exam_type, number_of_items in exam_parts:
                    data = (
                        next_id,
                        major_exam_type,
                        semester,
                        subject_code,
                        part_name,
                        number_of_items,
                        exam_type,
                        "Created",
                        self.current_user_id 
                    )
                    cursor.execute(insert_query, data)

                connection.commit()
                QMessageBox.information(self, "Success", "Exam successfully created and saved to database.")
                return next_id

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            return None

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def reset_exam_form_fields(self):
        self.major_exam.setCurrentIndex(0)
        self.semester.setCurrentIndex(0)
        self.subject_code.clear()
        self.subject_code.addItem("--- SUBJECT CODE ---")

        self.part_1.setChecked(False)
        self.type_exam_1.setCurrentIndex(0)
        self.number_item_1.setCurrentIndex(0)
        
        self.part_2.setChecked(False)
        self.type_exam_2.setCurrentIndex(0)
        self.number_item_2.setCurrentIndex(0)
        
        self.part_3.setChecked(False)
        self.type_exam_3.setCurrentIndex(0)
        self.number_item_3.setCurrentIndex(0)

        self.reset_exam_form_visibility()

    def open_exam_template(self):
        if not self.is_exam_form_complete():
            QMessageBox.warning(self, "Incomplete Form", "Please complete the required fields before proceeding.")
            return  

        major_type = self.get_selected_major_type()
        time_limit = self.get_time_limit()
        subject_code = self.get_subject_code()
        semester = self.get_semester()

        exam_parts = {}
        
        if self.part_1.isChecked():
            exam_type = self.type_exam_1.currentText()
            num_items = int(self.number_item_1.currentText())
            exam_parts[exam_type] = exam_parts.get(exam_type, 0) + num_items

        if self.part_2.isChecked():
            exam_type = self.type_exam_2.currentText()
            num_items = int(self.number_item_2.currentText())
            exam_parts[exam_type] = exam_parts.get(exam_type, 0) + num_items

        if self.part_3.isChecked():
            exam_type = self.type_exam_3.currentText()
            num_items = int(self.number_item_3.currentText())
            exam_parts[exam_type] = exam_parts.get(exam_type, 0) + num_items

        consolidated_exam_parts = [(etype, count) for etype, count in exam_parts.items()]

        exam_id = self.save_exam_form_to_database()
        
        if not exam_id:
            return

        self.reset_exam_form_fields()

        self.exam_template_window = ExamTemplate(
            major_type, 
            time_limit, 
            subject_code, 
            semester, 
            consolidated_exam_parts,
            self.current_user_id,       
            exam_id=exam_id,
            current_window=self         
        )
        self.exam_template_window.show()
        self.hide()

    def load_exam_lists(self):
        self.exam_draft_table = self.faculty_ui.findChild(QListWidget, "exam_draft_table")
        self.exam_published_table = self.faculty_ui.findChild(QListWidget, "exam_published_table")

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                query = """
                    SELECT exam_id, subject_code, semester, major_exam_type, exam_status, exam_date, schedule_time
                    FROM examination_form
                    WHERE created_by = %s
                    ORDER BY exam_id DESC
                """

                cursor.execute(query, (self.user_id,))
                exams = cursor.fetchall()

                self.exam_draft_table.clear()
                self.exam_published_table.clear()

                seen_exam_ids = set()
                draft_count = 0
                published_count = 0

                for exam in exams:
                    exam_id = exam['exam_id']
                    if exam_id in seen_exam_ids:
                        continue  # Avoid duplicates
                    seen_exam_ids.add(exam_id)

                    schedule_time = exam['schedule_time'] if exam['schedule_time'] else ""
                    if schedule_time:
                        datetime_line = f"{exam['exam_date']} | {schedule_time}"
                    else:
                        datetime_line = f"{exam['exam_date']}"

                    first_line = f"{exam['exam_id']} - {exam['subject_code']}"
                    second_line = f"{exam['semester']} - {exam['major_exam_type']}"
                    full_text = f"{datetime_line}\n{first_line}\n{second_line}"

                    item = QListWidgetItem(full_text)
                    item.setData(Qt.UserRole, exam_id)

                    font = item.font()
                    font.setPointSize(11)
                    item.setFont(font)

                    if exam["exam_status"] == "Published":
                        self.exam_published_table.addItem(item)
                        published_count += 1
                    elif exam["exam_status"] == "Draft":
                        self.exam_draft_table.addItem(item)
                        draft_count += 1

                                # Add placeholder messages if lists are empty
                if draft_count == 0:
                    placeholder_item = QListWidgetItem("No exam drafts available")
                    placeholder_item.setData(Qt.UserRole, None)

                    font = placeholder_item.font()
                    font.setPointSize(11)
                    font.setItalic(True)
                    placeholder_item.setFont(font)

                    placeholder_item.setFlags(Qt.NoItemFlags)  # ✅ Fully disables hover/selection
                    placeholder_item.setForeground(QColor(128, 128, 128))  # Gray
                    placeholder_item.setTextAlignment(Qt.AlignCenter)

                    self.exam_draft_table.addItem(placeholder_item)

                if published_count == 0:
                    placeholder_item = QListWidgetItem("No published exams available")
                    placeholder_item.setData(Qt.UserRole, None)

                    font = placeholder_item.font()
                    font.setPointSize(11)
                    font.setItalic(True)
                    placeholder_item.setFont(font)

                    placeholder_item.setFlags(Qt.NoItemFlags)  # ✅ Fully disables hover/selection
                    placeholder_item.setForeground(QColor(128, 128, 128))  # Gray
                    placeholder_item.setTextAlignment(Qt.AlignCenter)

                    self.exam_published_table.addItem(placeholder_item)


        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while loading exams:\n{e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def set_exam_schedule(self, total_items,exam_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Exam Schedule")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)

        date_label = QLabel("Select Exam Date:")
        date_picker = QDateEdit()
        date_picker.setCalendarPopup(True)
        date_picker.setDate(QDate.currentDate())

        start_time_label = QLabel("Start Time:")
        start_time_edit = QTimeEdit()
        start_time_edit.setDisplayFormat("hh:mm AP")
        start_time_edit.setTime(QTime.currentTime())

        end_time_label = QLabel("End Time:")
        end_time_edit = QTimeEdit()
        end_time_edit.setDisplayFormat("hh:mm AP")
        end_time_edit.setTime(QTime.currentTime().addSecs(3600))  # default +1 hour

        # Calculate minimum time limit
        min_minutes = total_items * 2  # 2 minutes per item
        min_hours = min_minutes // 60
        min_remaining_minutes = min_minutes % 60

        hour_label = QLabel("Time Limit (Hours):")
        hour_input = QSpinBox()
        hour_input.setRange(min_hours, 5)

        minute_label = QLabel("Time Limit (Minutes):")
        minute_input = QSpinBox()
        minute_input.setRange(0, 59)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(date_label)
        layout.addWidget(date_picker)
        layout.addWidget(start_time_label)
        layout.addWidget(start_time_edit)
        layout.addWidget(end_time_label)
        layout.addWidget(end_time_edit)
        layout.addWidget(hour_label)
        layout.addWidget(hour_input)
        layout.addWidget(minute_label)
        layout.addWidget(minute_input)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            selected_date = date_picker.date()
            selected_time = start_time_edit.time()
            datetime_combined = QDateTime(selected_date, selected_time)

            # Convert to Python datetime for comparison
            selected_start_datetime = datetime(
                selected_date.year(), selected_date.month(), selected_date.day(),
                selected_time.hour(), selected_time.minute()
            )
            current_datetime = datetime.now().replace(second=0, microsecond=0)

            if selected_start_datetime < current_datetime:
                QMessageBox.warning(self, "Invalid Schedule", "You cannot schedule an exam in the past.")
                return False

            start_dt = datetime(
                selected_date.year(), selected_date.month(), selected_date.day(),
                start_time_edit.time().hour(), start_time_edit.time().minute()
            )
            end_dt = datetime(
                selected_date.year(), selected_date.month(), selected_date.day(),
                end_time_edit.time().hour(), end_time_edit.time().minute()
            )
            allowed_duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
            entered_total_minutes = hour_input.value() * 60 + minute_input.value()

            if allowed_duration_minutes < min_minutes:
                QMessageBox.warning(
                    self,
                    "Invalid Schedule",
                    f"The selected time window is too short.\nYou need at least {min_minutes} minutes for {total_items} items."
                )
                return False

            if entered_total_minutes > allowed_duration_minutes:
                QMessageBox.warning(
                    self,
                    "Invalid Time Limit",
                    f"The entered time limit ({entered_total_minutes} min) exceeds the allowed duration "
                    f"between start and end time ({allowed_duration_minutes} min)."
                )
                return False

            if entered_total_minutes < min_minutes:
                QMessageBox.warning(
                    self,
                    "Invalid Time Limit",
                    f"The minimum time allowed for {total_items} items is {min_minutes} minutes."
                )
                return False

            # Save values
            self.exam_date = datetime_combined.toString("yyyy-MM-dd hh:mm AP")
            self.exam_date_only = selected_date.toString("yyyy-MM-dd")
            self.exam_time_limit = (hour_input.value(), minute_input.value())

            start_12hr = start_time_edit.time().toString("hh:mm AP")
            end_12hr = end_time_edit.time().toString("hh:mm AP")
            self.exam_schedule_time = f"{start_12hr} - {end_12hr}"
            self.exam_schedule_display = self.exam_schedule_time

            QMessageBox.information(
                self,
                "Updated Exam Schedule",
                f"📅 Date: {self.exam_date}\n"
                f"⏳ Time Limit: {self.exam_time_limit[0]} hr {self.exam_time_limit[1]} min\n"
                f"🕒 Schedule: {self.exam_schedule_display}"
            )
            
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="TUPCcoet@23!",
                    database="axis"
                )
                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute(
                        """
                        UPDATE examination_form
                        SET exam_date = %s, schedule_time = %s
                        WHERE exam_id = %s
                        """,
                        (self.exam_date_only, self.exam_schedule_time, exam_id)
                    )
                    connection.commit()
                    cursor.close()
                    connection.close()

                    self.load_exam_lists()

            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to update schedule:\n{e}")
                return False

            return True

        return False

    def edit_selected_exam(self):
        selected_item = self.exam_draft_table.currentItem()

        if not selected_item:
            published_selected_item = self.exam_published_table.currentItem()
            if published_selected_item:
                exam_id = published_selected_item.data(Qt.UserRole)
                try:
                    connection = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="TUPCcoet@23!",
                        database="axis"
                    )
                    if connection.is_connected():
                        cursor = connection.cursor(dictionary=True)

                        # ✅ First: Get exam_date and schedule_time (assumed consistent for the exam_id)
                        cursor.execute(
                            "SELECT exam_date, schedule_time FROM examination_form WHERE exam_id = %s LIMIT 1",
                            (exam_id,)
                        )
                        schedule_data = cursor.fetchone()

                        # ✅ Second: Get the total number of items
                        cursor.execute(
                            "SELECT SUM(number_of_items) AS total_items FROM examination_form WHERE exam_id = %s",
                            (exam_id,)
                        )
                        sum_data = cursor.fetchone()

                        if schedule_data and sum_data and sum_data["total_items"]:
                            exam_date_str = schedule_data["exam_date"]
                            schedule_time_str = schedule_data["schedule_time"]
                            total_items = int(sum_data["total_items"])

                            # Parse exam date
                            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
                            now = datetime.now()
                            today = now.date()
                            current_time = now.time()

                            # Parse schedule time window
                            try:
                                start_str, end_str = schedule_time_str.split(" - ")
                                start_time = datetime.strptime(start_str.strip(), "%I:%M %p").time()
                                end_time = datetime.strptime(end_str.strip(), "%I:%M %p").time()
                            except ValueError:
                                QMessageBox.warning(self, "Invalid Schedule", "Cannot parse schedule time format.")
                                return

                            end_datetime = datetime.combine(exam_date, end_time)

                            if today == exam_date and start_time <= current_time <= end_time:
                                QMessageBox.warning(self, "Edit Not Allowed", "You cannot reschedule an exam while it's ongoing.")
                                return
                            elif datetime.now() > end_datetime:
                                QMessageBox.warning(self, "Edit Not Allowed", "You cannot reschedule an exam that has already ended.")
                                return

                            # ✅ Proceed to edit schedule
                            if self.set_exam_schedule(total_items, exam_id):
                                QMessageBox.information(self, "Schedule Updated", "Exam schedule has been updated.")
                        else:
                            QMessageBox.warning(self, "Not Found", "Unable to retrieve schedule or item count for selected exam.")
                except mysql.connector.Error as e:
                    QMessageBox.critical(self, "Database Error", f"Error fetching item count:\n{e}")
                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()
                return
            else:
                QMessageBox.warning(self, "No Selection", "Please select a draft exam to edit.")
            return

        exam_id = selected_item.data(Qt.UserRole)  

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM examination_form WHERE exam_id = %s", (exam_id,))
                exam_data = cursor.fetchall()

                if not exam_data:
                    QMessageBox.warning(self, "Not Found", "Could not find the selected exam.")
                    return

                first = exam_data[0]
                major_exam = first["major_exam_type"]
                semester = first["semester"]
                subject_code = first["subject_code"]
                time_limit = first["time_limit"]

                parts = []
                for row in exam_data:
                    parts.append((row["exam_part"], row["exam_type"], int(row["number_of_items"])))

                consolidated = {}
                for _, exam_type, num in parts:
                    consolidated[exam_type] = consolidated.get(exam_type, 0) + num

                consolidated_parts = [(etype, count) for etype, count in consolidated.items()]

                self.load_exam_template_draft(
                    exam_id,
                    major_exam,
                    time_limit,
                    subject_code,
                    semester,
                    consolidated_parts
                )

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading exam:\n{e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def load_exam_template_draft(self, exam_id, major_type, time_limit, subject_code, semester, consolidated_parts):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                cursor.execute("""
                    SELECT description, question, option_a, option_b, option_c, option_d, correct_answer 
                    FROM multiple_choice_exam 
                    WHERE exam_id = %s
                """, (exam_id,))
                mc_questions = cursor.fetchall()

                cursor.execute("""
                    SELECT description, question, correct_answer 
                    FROM true_false_exam 
                    WHERE exam_id = %s
                """, (exam_id,))
                tf_questions = cursor.fetchall()

                cursor.execute("""
                    SELECT description, question, correct_answer 
                    FROM identification_exam 
                    WHERE exam_id = %s
                """, (exam_id,))
                id_questions = cursor.fetchall()

                self.exam_template_window = ExamTemplate(
                    major_type,
                    time_limit,
                    subject_code,
                    semester,
                    consolidated_parts,
                    self.user_id,
                    exam_id=exam_id,
                    faculty_loaded_data={
                        "multiple_choice": mc_questions,
                        "true_false": tf_questions,
                        "identification": id_questions
                    },
                    current_window=self
                )
                self.exam_template_window.show()
                self.hide()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading draft exam data:\n{e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def _assign_parts_to_questions(self, exam_parts_info, questions, question_type):
        result = []
        question_index = 0
        
        parts_with_type = [part for part in exam_parts_info if part['exam_type'] == question_type]
        
        for part in parts_with_type:
            exam_part = part['exam_part']
            num_items = part['number_of_items']
            
            description = questions[question_index]['description'] if question_index < len(questions) else ""
            
            for i in range(num_items):
                if question_index < len(questions):
                    question_data = dict(questions[question_index])
                    question_data['exam_part'] = exam_part
                    if i == 0:
                        part_description = question_data.get('description', '')
                    else:
                        question_data['description'] = part_description
                    
                    result.append(question_data)
                    question_index += 1
        
        return result

    def delete_selected_exam(self):
        selected_item = self.exam_draft_table.currentItem() or self.exam_published_table.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select an exam (draft or published) to delete.")
            return

        exam_id = selected_item.data(Qt.UserRole) 

        confirm = QMessageBox.question(
            self, "Confirm Deletion", f"Are you sure you want to delete exam {exam_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="TUPCcoet@23!",
                    database="axis"
                )
                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM examination_form WHERE exam_id = %s", (exam_id,))
                    connection.commit()
                    QMessageBox.information(self, "Deleted", f"Exam {exam_id} deleted successfully.")
                    self.load_exam_lists()

            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Database Error", f"Error deleting exam:\n{e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        
    def load_user_settings(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT first_name, middle_name, last_name, suffix, birthdate, sex, emailaddress, department, user_id, profile_image
                    FROM user_account 
                    WHERE user_id = %s
                """
                cursor.execute(query, (self.current_user_id,))
                result = cursor.fetchone()

                if result:
                    # Construct full name
                    name_parts = [
                        result['first_name'],
                        result['middle_name'] if result['middle_name'] not in (None, '', 'None') else '',
                        result['last_name'],
                        result['suffix'] if result['suffix'] not in (None, '', 'None') else ''
                    ]
                    full_name = " ".join(part for part in name_parts if part).upper()

                    # Set values in UI
                    if self.name:
                        self.name.setText(full_name)

                    if self.birthdate:
                        self.birthdate.setText(str(result['birthdate']))

                    if self.sex:
                        self.sex.setText(result['sex'])

                    if self.email:
                        self.email.setText(result['emailaddress'])

                    if self.department:
                        self.department.setText(result['department'])

                    if self.user_id_label:
                        self.user_id_label.setText(str(result['user_id']))

                    # === Load and Set Profile Image ===
                    from PySide6.QtGui import QPixmap
                    from PySide6.QtCore import Qt
                    import os

                    profile_path = result.get('profile_image')
                    if profile_path and os.path.exists(profile_path):
                        pixmap = QPixmap(profile_path)
                    else:
                        pixmap = QPixmap("UI/DP/default.png")

                    photo_label = self.findChild(QLabel, "photo")
                    if photo_label:
                        photo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))

                else:
                    print(f"No user found with ID {self.current_user_id}")

                cursor.close()
                connection.close()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    
    def show_blurred_overlay(self):
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        self.overlay.setGeometry(self.rect())
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.show()

    def hide_blurred_overlay(self):
        if hasattr(self, "overlay"):
            self.overlay.deleteLater()
            del self.overlay

    def show_notification_dialog(self):
        self.show_blurred_overlay()
        self.notification.show_dialog()

    def get_selected_major_type(self):
        return self.major_exam.currentText()
    
    def get_time_limit(self):
        if hasattr(self, "exam_time_limit"):
            hours, minutes = self.exam_time_limit
            return f"{hours} hr {minutes} min"
        return "Not Set"

    def get_subject_code(self):
        return self.subject_code.currentText()

    def get_semester(self):
        return self.semester.currentText()

    def update_time(self):
        # Time display (hh:mm:ss AM/PM)
        current_time = QTime.currentTime().toString("hh:mm:ss AP")
        self.timedb.setText(current_time)

        # Day like "Monday"
        now = datetime.now()
        day_string = now.strftime("%A")
        self.day.setText(day_string)

        # Date like "20 May"
        date_string = f"{now.day} {now.strftime('%B')}"
        self.date.setText(date_string)

        # Aesthetic and soft greetings
        hour = now.hour

        if 5 <= hour < 8:
            greeting = "Rise and shine ✨"
        elif 8 <= hour < 11:
            greeting = "Bright morning ☀️"
        elif 11 <= hour < 12:
            greeting = "Late morning glow 🌤️"
        elif 12 <= hour < 13:
            greeting = "Midday calm 🌞"
        elif 13 <= hour < 16:
            greeting = "Soft afternoon breeze 🌿"
        elif 16 <= hour < 17:
            greeting = "Golden hour ☀️"
        elif 17 <= hour < 19:
            greeting = "Hello, evening 🌇"
        elif 19 <= hour < 21:
            greeting = "Serene twilight 🌆"
        else:
            greeting = "Peaceful night 🌙"

        self.greetings.setText(greeting)

    def start_time_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) 
    
    def show_dashboard_page(self):
        if self.faculty_stacked:
            self.faculty_stacked.setCurrentIndex(0)

        self.dashboardbtn.setChecked(True)
        self.studentstatsbtn.setChecked(False)
        self.classbtn.setChecked(False)
        self.examinationbtn.setChecked(False)


    def handle_excel_button(self):
        from excel_handler import excel_exists, save_table_to_excel, load_excel_path

        table_widget = self.findChild(QTableWidget, "student_performance_table")
        course_sort = self.findChild(QComboBox, "course_sort")
        semester_sort = self.findChild(QComboBox, "semester_sort")
        no_data_label = self.findChild(QLabel, "no_data_label")
        
        if not table_widget or not course_sort or not semester_sort:
            QMessageBox.warning(self, "Error", "Required UI elements not found.")
            return

        # Store current selections to restore them later
        current_course = course_sort.currentText() if course_sort.count() > 0 else ""
        current_semester = semester_sort.currentText()
        current_exam_type = self.selected_exam_type_filter

        try:
            # Create or update Excel with complete data
            busy_cursor = QCursor(Qt.WaitCursor)
            QApplication.setOverrideCursor(busy_cursor)
            
            # Show a progress dialog
            progress = QProgressDialog("Generating Excel file with all data...", None, 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(1000)  # Show after 1 second
            progress.setValue(10)
            
            # If Excel already exists, first generate a new one then open it
            path = save_table_to_excel(
                table_widget, 
                self.current_user_id,
                course_sort_combobox=course_sort,
                populate_callback=self.populate_student_performance_table
            )
            
            progress.setValue(90)
            
            # Update button label
            viewsheet_btn = self.findChild(QPushButton, "viewsheet_btn")
            if viewsheet_btn:
                viewsheet_btn.setText("View Excel")
                
            # Reset cursor
            QApplication.restoreOverrideCursor()
            progress.setValue(100)
            
            # Show success message if this is the first time creating the Excel
            if not excel_exists(self.current_user_id):
                QMessageBox.information(self, "Success", "Excel file created with all semester and course data!")
            
            # Restore the table to its original state and ensure it's visible
            if course_sort.count() > 0 and table_widget:
                # Make sure the table is visible and the no data label is hidden
                if no_data_label:
                    no_data_label.hide()
                table_widget.show()
                
                # Restore the selected exam type filter
                if current_exam_type:
                    self.selected_exam_type_filter = current_exam_type
                    
                # Re-populate with current filters
                self.populate_student_performance_table(table_widget, current_course, current_semester)
            
            # Open the Excel file
            os.startfile(path)
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error", f"Failed to create Excel file: {str(e)}")

    def show_studperf_page(self):
        if self.faculty_stacked:
            self.faculty_stacked.setCurrentIndex(1)

            self.selected_exam_type_filter = None

            prelim_data = self.findChild(QPushButton, "prelim_data")
            midterm_data = self.findChild(QPushButton, "midterm_data")
            finals_data = self.findChild(QPushButton, "finals_data")
            course_sort = self.findChild(QComboBox, "course_sort")
            semester_sort = self.findChild(QComboBox, "semester_sort")
            student_performance_table = self.findChild(QTableWidget, "student_performance_table")
            no_data_label = self.findChild(QLabel, "no_data_label")

            # Set buttons checkable for visual toggle effect
            prelim_data.setCheckable(True)
            midterm_data.setCheckable(True)
            finals_data.setCheckable(True)

            # Connect with unchecking others
            prelim_data.clicked.connect(lambda: self.set_exam_type_filter_with_toggle("PRELIM EXAM", prelim_data, [midterm_data, finals_data]))
            midterm_data.clicked.connect(lambda: self.set_exam_type_filter_with_toggle("MIDTERM EXAM", midterm_data, [prelim_data, finals_data]))
            finals_data.clicked.connect(lambda: self.set_exam_type_filter_with_toggle("FINAL EXAM", finals_data, [prelim_data, midterm_data]))

            # If no_data_label doesn't exist, create it
            if not no_data_label:
                no_data_label = QLabel("No exam data available for the selected filters.", self)
                no_data_label.setObjectName("no_data_label")
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: #666; font-style: italic;")
                no_data_label.hide()
                parent_layout = student_performance_table.parent().layout()
                if parent_layout:
                    parent_layout.addWidget(no_data_label)

            if semester_sort:
                semester_sort.clear()
                semester_sort.addItems(["1st Semester", "2nd Semester"])

                try:
                    semester_sort.currentIndexChanged.disconnect()
                except TypeError:
                    pass

                semester_sort.currentIndexChanged.connect(self.update_table_on_filter_change)

            if course_sort:
                courses_available = self.populate_course_combobox(course_sort)

                try:
                    course_sort.currentIndexChanged.disconnect()
                except TypeError:
                    pass

                course_sort.currentIndexChanged.connect(self.update_table_on_filter_change)

                if not courses_available and no_data_label:
                    student_performance_table.setRowCount(0)
                    student_performance_table.hide()
                    no_data_label.setText(f"No exams created for {semester_sort.currentText()}. Please create an exam first.")
                    no_data_label.show()
                else:
                    student_performance_table.show()
                    no_data_label.hide()

            # Set up Excel button
            from excel_handler import excel_exists
            viewsheet_btn = self.findChild(QPushButton, "viewsheet_btn")
            if viewsheet_btn:
                if excel_exists(self.current_user_id):
                    viewsheet_btn.setText("View Excel")
                else:
                    viewsheet_btn.setText("Make Excel")

                try:
                    viewsheet_btn.clicked.disconnect()
                except Exception:
                    pass

                viewsheet_btn.clicked.connect(self.handle_excel_button)

            # Populate the table if courses are available
            if student_performance_table:
                if course_sort and semester_sort and course_sort.count() > 0:
                    self.populate_student_performance_table(
                        student_performance_table,
                        course_sort.currentText(),
                        semester_sort.currentText()
                    )
                else:
                    student_performance_table.setRowCount(0)

        self.dashboardbtn.setChecked(False)
        self.studentstatsbtn.setChecked(True)
        self.classbtn.setChecked(False)
        self.examinationbtn.setChecked(False)
        
    def set_exam_type_filter_with_toggle(self, exam_type, clicked_button, other_buttons):
        self.selected_exam_type_filter = exam_type

        clicked_button.setChecked(True)
        for btn in other_buttons:
            btn.setChecked(False)

        self.update_table_on_filter_change()


    def update_table_on_filter_change(self):
        course_sort = self.findChild(QComboBox, "course_sort")
        semester_sort = self.findChild(QComboBox, "semester_sort")
        student_performance_table = self.findChild(QTableWidget, "student_performance_table")
        no_data_label = self.findChild(QLabel, "no_data_label")

        # First check if courses need to be repopulated based on semester change
        if self.sender() == semester_sort:
            courses_available = self.populate_course_combobox(course_sort)
            
            # Handle case when no courses are available for the selected semester
            if not courses_available:
                student_performance_table.setRowCount(0)
                if no_data_label:
                    no_data_label.setText(f"No exams created for {semester_sort.currentText()}. Please create an exam first.")
                    student_performance_table.hide()
                    no_data_label.show()
                return
        
        # If we have courses and the table, populate it
        if course_sort and semester_sort and student_performance_table:
            if course_sort.count() > 0:
                selected_course = course_sort.currentText()
                selected_semester = semester_sort.currentText()
                
                # Show the table and hide the "no data" message
                student_performance_table.show()
                if no_data_label:
                    no_data_label.hide()
                    
                self.populate_student_performance_table(student_performance_table, selected_course, selected_semester)
            else:
                student_performance_table.setRowCount(0)
                if no_data_label:
                    no_data_label.setText(f"No exams created for {semester_sort.currentText()}. Please create an exam first.")
                    student_performance_table.hide()
                    no_data_label.show()

    def populate_course_combobox(self, course_sort):
        """Populate the course combobox with available courses for the current faculty and semester."""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            faculty_id = self.current_user_id
            
            # Get currently selected semester
            semester_sort = self.findChild(QComboBox, "semester_sort")
            selected_semester = semester_sort.currentText() if semester_sort else "1st Semester"
            
            # Query to find courses with exams for this faculty and semester
            cursor.execute("""
                SELECT DISTINCT subject_code 
                FROM examination_form 
                WHERE created_by = %s AND semester = %s
            """, (faculty_id, selected_semester))
            
            courses = cursor.fetchall()
            
            course_sort.clear()
            
            # Add courses to the combobox
            if courses:
                for course in courses:
                    course_sort.addItem(course["subject_code"])
                
            cursor.close()
            connection.close()
            
            return course_sort.count() > 0
            
        except mysql.connector.Error as err:
            print(f"Database Error in populate_course_combobox: {err}")
            return False
        except Exception as e:
            print(f"Error in populate_course_combobox: {e}")
            return False


    def handle_score_cell_click(self, row, col, table, subject_code):
        """Handle clicks on score cells in the student performance table"""

        # Ignore clicks on the student name column
        if col == 0:
            return

        # Get the clicked cell item
        item = table.item(row, col)
        if not item:
            return

        # Check if this is a non-clickable type of score
        non_clickable_texts = [
            "No exam created",
            "Not taken yet",
            "0/0 (0%)",
            "0",
            "Missing",
        ]

        score_text = item.text().strip()
        if score_text in non_clickable_texts or "missed this exam" in (item.toolTip() or "").lower():
            return

        # Get student_id from the first column
        student_name_item = table.item(row, 0)
        if not student_name_item:
            return

        student_id = student_name_item.data(Qt.UserRole)

        # Get exam_id from the clicked cell
        exam_id = item.data(Qt.UserRole)

        # Check if the required data is present
        if not exam_id or not student_id:
            print("Missing exam_id or student_id for clicked cell")
            return

        print(f"Opening exam result for student {student_id}, exam {exam_id}")

        # Open the exam result window using the appropriate method
        if hasattr(self, "open_exam_result"):
            self.open_exam_result(student_id, exam_id)
        else:
            QMessageBox.warning(self, "Error", "Cannot view exam results.")


    def populate_course_combobox(self, course_sort):
        """Populate the course combobox with available courses for the current faculty and semester."""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            faculty_id = self.current_user_id
            
            # Get currently selected semester
            semester_sort = self.findChild(QComboBox, "semester_sort")
            selected_semester = semester_sort.currentText() if semester_sort else "1st Semester"
            
            # Query to find courses with exams for this faculty and semester
            cursor.execute("""
                SELECT DISTINCT subject_code 
                FROM examination_form 
                WHERE created_by = %s AND semester = %s
            """, (faculty_id, selected_semester))
            
            courses = cursor.fetchall()
            
            course_sort.clear()
            
            # Add courses to the combobox
            if courses:
                for course in courses:
                    course_sort.addItem(course["subject_code"])
                
            cursor.close()
            connection.close()
            
            return course_sort.count() > 0
            
        except mysql.connector.Error as err:
            print(f"Database Error in populate_course_combobox: {err}")
            return False
        except Exception as e:
            print(f"Error in populate_course_combobox: {e}")
            return False

    def set_exam_type_filter_and_update(self, exam_type):
        self.selected_exam_type_filter = exam_type

        course_sort = self.findChild(QComboBox, "course_sort")
        semester_sort = self.findChild(QComboBox, "semester_sort")
        student_performance_table = self.findChild(QTableWidget, "student_performance_table")

        if not course_sort or not semester_sort or not student_performance_table:
            return

        selected_course = course_sort.currentText()
        selected_semester = semester_sort.currentText()

        reverse_mapping = {
            "PRELIM EXAM": "Prelim",
            "MIDTERM EXAM": "Midterm",
            "FINAL EXAM": "Finals"
        }

        exam_key = reverse_mapping.get(exam_type)
        if not exam_key:
            self.clear_all_charts()
            return

        # Extract chart data from table
        chart_data = []
        for row in range(student_performance_table.rowCount()):
            name_item = student_performance_table.item(row, 0)
            score_item = student_performance_table.item(row, {"Prelim": 1, "Midterm": 2, "Finals": 3}[exam_key])

            if name_item and score_item:
                match = re.search(r"\(([\d.]+)%\)", score_item.text())
                if match:
                    percent = float(match.group(1))
                    chart_data.append((name_item.text(), percent))

        self.update_charts(chart_data, selected_course, selected_semester, exam_type)

    def clear_all_charts(self):
        for container in [self.data1_tabs.currentWidget(), self.data2_tabs.currentWidget(), self.data3]:
            if container and container.layout():
                layout = container.layout()
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)

    def update_table_on_filter_change(self):
        course_sort = self.findChild(QComboBox, "course_sort")
        semester_sort = self.findChild(QComboBox, "semester_sort")
        student_performance_table = self.findChild(QTableWidget, "student_performance_table")
        no_data_label = self.findChild(QLabel, "no_data_label")

        # First check if courses need to be repopulated based on semester change
        if self.sender() == semester_sort:
            courses_available = self.populate_course_combobox(course_sort)
            
            # Handle case when no courses are available for the selected semester
            if not courses_available:
                student_performance_table.setRowCount(0)
                if no_data_label:
                    no_data_label.setText(f"No exams created for {semester_sort.currentText()}. Please create an exam first.")
                    student_performance_table.hide()
                    no_data_label.show()
                return
        
        # If we have courses and the table, populate it
        if course_sort and semester_sort and student_performance_table:
            if course_sort.count() > 0:
                selected_course = course_sort.currentText()
                selected_semester = semester_sort.currentText()
                
                # Show the table and hide the "no data" message
                student_performance_table.show()
                if no_data_label:
                    no_data_label.hide()
                    
                self.populate_student_performance_table(student_performance_table, selected_course, selected_semester)
            else:
                student_performance_table.setRowCount(0)
                if no_data_label:
                    no_data_label.setText(f"No exams created for {semester_sort.currentText()}. Please create an exam first.")
                    student_performance_table.hide()
                    no_data_label.show()


    def populate_student_performance_table(self, student_performance_table, selected_course, selected_semester):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            faculty_id = self.current_user_id

            cursor.execute("""
                SELECT DISTINCT major_exam_type
                FROM examination_form
                WHERE created_by = %s AND subject_code = %s AND semester = %s
            """, (faculty_id, selected_course, selected_semester))
            faculty_exam_types = [row["major_exam_type"] for row in cursor.fetchall()]

            if not faculty_exam_types:
                no_data_label = self.findChild(QLabel, "no_data_label")
                if no_data_label:
                    no_data_label.setText(f"No {self.selected_exam_type_filter or ''} exams found for {selected_course} in {selected_semester}.")
                    student_performance_table.hide()
                    no_data_label.show()
                student_performance_table.setRowCount(0)
                cursor.close()
                connection.close()
                return False

            cursor.execute("""
                SELECT DISTINCT user_id, first_name, middle_name, last_name, suffix 
                FROM user_account 
                WHERE role = 'student' AND status = 'approved'
            """)
            students = cursor.fetchall()

            student_performance_table.setRowCount(0)
            student_performance_table.setColumnCount(4)
            student_performance_table.setHorizontalHeaderLabels(["Full Name", "Prelim", "Midterm", "Finals"])
            student_performance_table.horizontalHeader().setStretchLastSection(True)
            self.adjust_column_widths_to_header(student_performance_table)

            passing_percentage = 75

            exam_type_mapping = {
                "Prelim": "PRELIM EXAM",
                "Midterm": "MIDTERM EXAM",
                "Finals": "FINAL EXAM"
            }
            reverse_mapping = {v: k for k, v in exam_type_mapping.items()}

            try:
                student_performance_table.cellClicked.disconnect()
            except TypeError:
                pass

            student_performance_table.cellClicked.connect(
                lambda row, col: self.handle_score_cell_click(row, col, student_performance_table, selected_course)
            )

            top_performers = []
            self.class_standing_data = top_performers

            now = datetime.now()

            for student in students:
                student_id = student["user_id"]
                middle_initial = f" {student['middle_name'][0]}." if student['middle_name'] and student['middle_name'].strip() else ""
                suffix = f" {student['suffix']}" if student['suffix'] and student['suffix'].strip() else ""
                full_name = f"{student['first_name']}{middle_initial} {student['last_name']}{suffix}"

                exam_scores = {
                    "Prelim": {"correct": 0, "total": 0, "percentage": 0, "available": False, "exam_id": None, "is_missing": False},
                    "Midterm": {"correct": 0, "total": 0, "percentage": 0, "available": False, "exam_id": None, "is_missing": False},
                    "Finals": {"correct": 0, "total": 0, "percentage": 0, "available": False, "exam_id": None, "is_missing": False}
                }

                for db_exam_type in faculty_exam_types:
                    if db_exam_type in reverse_mapping:
                        exam_key = reverse_mapping[db_exam_type]
                        exam_scores[exam_key]["available"] = True

                for exam_key, score_data in exam_scores.items():
                    if score_data["available"]:
                        db_exam_type = exam_type_mapping[exam_key]

                        cursor.execute("""
                            SELECT DISTINCT ef.exam_id
                            FROM examination_form ef
                            JOIN student_answers sa ON sa.exam_id = ef.exam_id
                            WHERE sa.student_id = %s AND ef.major_exam_type = %s
                            AND ef.subject_code = %s AND ef.semester = %s AND ef.created_by = %s
                            LIMIT 1
                        """, (student_id, db_exam_type, selected_course, selected_semester, faculty_id))

                        exam_result = cursor.fetchone()
                        if exam_result:
                            score_data["exam_id"] = exam_result["exam_id"]

                            cursor.execute("""
                                SELECT COUNT(*) as total_count,
                                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count
                                FROM student_answers
                                WHERE student_id = %s AND exam_id = %s
                            """, (student_id, exam_result["exam_id"]))

                            result = cursor.fetchone()
                            if result and result["total_count"] > 0:
                                total_answers = float(result["total_count"])
                                correct_answers = float(result["correct_count"] or 0)
                                percentage = int(round(correct_answers / total_answers * 100))

                                score_data["correct"] = int(correct_answers)
                                score_data["total"] = int(total_answers)
                                score_data["percentage"] = percentage
                        else:
                            cursor.execute("""
                                SELECT ef.exam_id, ef.number_of_items, ef.exam_date, ef.schedule_time
                                FROM examination_form ef
                                WHERE ef.major_exam_type = %s AND ef.subject_code = %s 
                                AND ef.semester = %s AND ef.created_by = %s
                                AND ef.exam_status = 'Published'
                                LIMIT 1
                            """, (db_exam_type, selected_course, selected_semester, faculty_id))

                            published_exam = cursor.fetchone()
                            if published_exam:
                                exam_id = published_exam["exam_id"]
                                total_items = published_exam["number_of_items"] or 0
                                exam_date = published_exam["exam_date"]
                                schedule_time = published_exam["schedule_time"]

                                is_past_due = False
                                if schedule_time and exam_date:
                                    try:
                                        end_time_parts = schedule_time.split(" - ")
                                        if len(end_time_parts) > 1:
                                            end_time_str = end_time_parts[1].strip()
                                            exam_end_datetime = datetime.strptime(f"{exam_date} {end_time_str}", "%Y-%m-%d %I:%M %p")
                                            is_past_due = now > exam_end_datetime
                                    except Exception as e:
                                        print(f"[WARNING] Failed to parse exam end time: {e}")

                                if is_past_due:
                                    score_data["exam_id"] = exam_id
                                    score_data["correct"] = 0
                                    score_data["total"] = total_items
                                    score_data["percentage"] = 0
                                    score_data["is_missing"] = True

                has_available_exam = any(score_data["available"] for score_data in exam_scores.values())
                if not has_available_exam:
                    continue

                total_percent = 0
                available_count = 0
                for data in exam_scores.values():
                    if data["available"]:
                        if data["total"] > 0 or data["is_missing"]:
                            total_percent += data["percentage"]
                            available_count += 1

                avg_percent = total_percent / available_count if available_count > 0 else 0
                top_performers.append((full_name, avg_percent))

                student_performance_table.insertRow(student_performance_table.rowCount())
                row_idx = student_performance_table.rowCount() - 1
                student_performance_table.setItem(row_idx, 0, QTableWidgetItem(full_name))
                student_performance_table.item(row_idx, 0).setData(Qt.UserRole, student_id)

                for idx, exam_key in enumerate(["Prelim", "Midterm", "Finals"], 1):
                    score_data = exam_scores[exam_key]
                    
                    if score_data["available"]:
                        if score_data["total"]:
                            score_text = f"{score_data['correct']}/{score_data['total']} ({score_data['percentage']}%)"
                            score_item = QTableWidgetItem(score_text)

                            if score_data["exam_id"]:
                                score_item.setData(Qt.UserRole, score_data["exam_id"])
                                if score_data["correct"] > 0:
                                    font = score_item.font()
                                    font.setUnderline(True)
                                    score_item.setFont(font)
                                    score_item.setToolTip("Click to view exam details")
                            if score_data["is_missing"]:
                                score_item = QTableWidgetItem("Missing")
                                score_item.setForeground(QColor(139, 0, 0))
                                score_item.setBackground(QColor(255, 240, 240))
                                score_item.setToolTip("Student missed this exam - automatic 0 score")
                            else:
                                score_item.setForeground(Qt.green if score_data["percentage"] >= passing_percentage else Qt.red)
                        else:
                            score_item = QTableWidgetItem("Not taken yet")
                            score_item.setForeground(Qt.gray)
                            score_item.setToolTip("Student has not taken this exam yet")
                    else:
                        score_item = QTableWidgetItem("No exam created")
                        score_item.setForeground(Qt.gray)
                        score_item.setToolTip("No exam created for this period yet")
                    
                    student_performance_table.setItem(row_idx, idx, score_item)

            if not self.selected_exam_type_filter:
                self.clear_all_charts()
                cursor.close()
                connection.close()
                return True

            chart_exam_key = reverse_mapping.get(self.selected_exam_type_filter, None)
            if not chart_exam_key:
                self.clear_all_charts()
                cursor.close()
                connection.close()
                return True

            chart_data = []
            for row in range(student_performance_table.rowCount()):
                name = student_performance_table.item(row, 0).text()
                score_item = student_performance_table.item(row, {"Prelim":1, "Midterm":2, "Finals":3}[chart_exam_key])
                if score_item and score_item.text() and not score_item.text().startswith("No") and score_item.text() != "Not taken yet":
                    import re
                    match = re.search(r"\((\d+)%\)", score_item.text())
                    if match:
                        percent = int(match.group(1))
                        chart_data.append((name, percent))

            self.update_charts(chart_data, selected_course, selected_semester, self.selected_exam_type_filter)

            cursor.close()
            connection.close()
            return True

        except mysql.connector.Error as e:
            print("Error while connecting to MySQL", e)
            return False

    def set_glassmorphism_style(self, widget: QWidget):
        # Applies a translucent white glass effect with blur and rounded corners
        widget.setStyleSheet("""
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        """)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(12)
        widget.setGraphicsEffect(blur)


    def update_charts(self, top_performers, selected_course, selected_semester, exam_type):
        major_exam_display = exam_type.replace(" EXAM", "").title() if exam_type else "Selected Exam"
        formatted_semester = selected_semester.title()

        # Create separate title strings for custom labels
        main_chart_title = f"{formatted_semester}\nTop Performing Students in {selected_course}\n{major_exam_display}"
        pie_chart_title = f"{formatted_semester}\nPass vs Fail Distribution\n{major_exam_display}"
        graph_title = f"{formatted_semester}\nClass Standing Distribution"

        # Check if we have valid data to display
        has_valid_data = len(top_performers) > 0

        # ===== BAR CHART: Top Performing Students =====
        page1 = self.data1_tabs
        if not page1.layout():
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            page1.setLayout(layout)
        layout = page1.layout()

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if not has_valid_data:
            # Show "No data available" message
            no_data_widget = self.create_no_data_widget(main_chart_title, "No exam data available to display charts")
            layout.addWidget(no_data_widget)
        else:
            # Original chart creation code
            top_performers.sort(key=lambda x: x[1], reverse=True)
            top_5 = top_performers[:5][::-1]

            names = [item[0] for item in top_5]
            scores = [item[1] for item in top_5]

            bar_set = QBarSet("Average %")
            bar_set.append(scores)

            gradient = QLinearGradient(0, 0, 0, 1)
            gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QColor("#3373B9"))
            gradient.setColorAt(0.5, QColor("#5A95D1"))
            gradient.setColorAt(1.0, QColor("#215988"))
            bar_set.setBrush(gradient)
            bar_set.setBorderColor(QColor("#14466A"))

            series = QHorizontalBarSeries()
            series.append(bar_set)

            chart = QChart()
            chart.addSeries(series)
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.setDropShadowEnabled(True)
            chart.setBackgroundRoundness(15)

            axis_y = QBarCategoryAxis()
            axis_y.append(names)
            axis_y.setLabelsColor(QColor(50, 70, 100))
            axis_y.setLabelsFont(QFont("Segoe UI", 8))
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)

            axis_x = QValueAxis()
            axis_x.setRange(0, 100)
            axis_x.setTitleText("Average Score (%)")
            axis_x.setLabelsColor(QColor(80, 80, 90))
            axis_x.setLabelsFont(QFont("Segoe UI", 8))
            axis_x.setTitleFont(QFont("Segoe UI", 9, QFont.Medium))
            axis_x.setGridLineColor(QColor(150, 150, 150, 60))
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Create custom title label
            title_label1 = QLabel(main_chart_title)
            title_label1.setAlignment(Qt.AlignCenter)
            title_label1.setFont(QFont("Segoe UI", 11, QFont.Bold))
            title_label1.setStyleSheet("color: rgb(33, 55, 80); margin: 5px;")
            title_label1.setWordWrap(True)

            container1 = QWidget()
            container1_layout = QVBoxLayout()
            container1_layout.setContentsMargins(10, 10, 10, 10)
            container1_layout.addWidget(title_label1)
            container1_layout.addWidget(chart_view)
            container1.setLayout(container1_layout)
            container1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.set_glassmorphism_style(container1)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setOffset(5, 5)
            shadow.setColor(QColor(0, 0, 0, 70))
            container1.setGraphicsEffect(shadow)

            layout.addWidget(container1)

        self.data1_tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ===== PIE CHART: Pass vs Fail =====
        page2 = self.data2_tabs
        if not page2.layout():
            layout2 = QVBoxLayout()
            layout2.setContentsMargins(0, 0, 0, 0)
            layout2.setSpacing(10)
            page2.setLayout(layout2)
        layout2 = page2.layout()

        while layout2.count():
            item = layout2.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if not has_valid_data:
            # Show "No data available" message
            no_data_widget = self.create_no_data_widget(pie_chart_title, "No exam data available to display pass/fail distribution")
            layout2.addWidget(no_data_widget)
        else:
            # Original pie chart creation code
            passing_percentage = 75.0
            passed = sum(1 for _, avg in top_performers if avg >= passing_percentage)
            failed = len(top_performers) - passed

            pie_series = QPieSeries()
            pie_series.append(f"Passed ({passed})", passed)
            pie_series.append(f"Failed ({failed})", failed)

            for slice in pie_series.slices():
                slice.setLabelVisible(True)
                slice.setLabelFont(QFont("Segoe UI", 8, QFont.Medium))
                if "Passed" in slice.label():
                    slice.setBrush(QColor("#3373B9"))
                    slice.setBorderColor(QColor("#1B3A70"))
                else:
                    slice.setBrush(QColor("#FF5929"))
                    slice.setBorderColor(QColor("#B03E20"))

            pie_chart = QChart()
            pie_chart.addSeries(pie_series)
            pie_chart.setDropShadowEnabled(True)
            pie_chart.legend().setAlignment(Qt.AlignRight)

            pie_chart_view = QChartView(pie_chart)
            pie_chart_view.setRenderHint(QPainter.Antialiasing)
            pie_chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Create custom title label
            title_label2 = QLabel(pie_chart_title)
            title_label2.setAlignment(Qt.AlignCenter)
            title_label2.setFont(QFont("Segoe UI", 11, QFont.Bold))
            title_label2.setStyleSheet("color: rgb(33, 55, 80); margin: 5px;")
            title_label2.setWordWrap(True)

            container2 = QWidget()
            container2_layout = QVBoxLayout()
            container2_layout.setContentsMargins(10, 10, 10, 10)
            container2_layout.addWidget(title_label2)
            container2_layout.addWidget(pie_chart_view)
            container2.setLayout(container2_layout)
            container2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.set_glassmorphism_style(container2)

            shadow2 = QGraphicsDropShadowEffect()
            shadow2.setBlurRadius(20)
            shadow2.setOffset(5, 5)
            shadow2.setColor(QColor(0, 0, 0, 70))
            container2.setGraphicsEffect(shadow2)

            layout2.addWidget(container2)

        self.data2_tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ===== BAR CHART: Class Standing =====
        if not self.data3.layout():
            layout3 = QVBoxLayout()
            layout3.setContentsMargins(0, 0, 0, 0)
            layout3.setSpacing(10)
            self.data3.setLayout(layout3)
        layout3 = self.data3.layout()

        while layout3.count():
            item = layout3.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        class_standing = self.class_standing_data
        if not class_standing:
            no_data_widget = self.create_no_data_widget(graph_title, "No exam data available to display class standing distribution")
            layout3.addWidget(no_data_widget)
        else:
            bins = {"90-100": 0, "80-89": 0, "75-79": 0, "Below 75": 0}
            for _, avg in class_standing:
                if avg >= 90:
                    bins["90-100"] += 1
                elif avg >= 80:
                    bins["80-89"] += 1
                elif avg >= 75:
                    bins["75-79"] += 1
                else:
                    bins["Below 75"] += 1

            bar_set2 = QBarSet("Students")
            bar_set2.append(list(bins.values()))

            gradient2 = QLinearGradient(0, 0, 0, 1)
            gradient2.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
            gradient2.setColorAt(0.0, QColor("#5A95D1"))
            gradient2.setColorAt(1.0, QColor("#215988"))
            bar_set2.setBrush(gradient2)
            bar_set2.setBorderColor(QColor("#14466A"))

            series2 = QBarSeries()
            series2.append(bar_set2)

            chart2 = QChart()
            chart2.addSeries(series2)
            chart2.setAnimationOptions(QChart.SeriesAnimations)
            chart2.setDropShadowEnabled(True)
            chart2.setBackgroundRoundness(15)

            axis_x2 = QBarCategoryAxis()
            axis_x2.append(list(bins.keys()))
            axis_x2.setLabelsColor(QColor(50, 70, 100))
            axis_x2.setLabelsFont(QFont("Segoe UI", 8))
            chart2.addAxis(axis_x2, Qt.AlignBottom)
            series2.attachAxis(axis_x2)

            axis_y2 = QValueAxis()
            axis_y2.setRange(0, max(bins.values()) or 1)
            axis_y2.setTitleText("Number of Students")
            axis_y2.setLabelsColor(QColor(80, 80, 90))
            axis_y2.setLabelsFont(QFont("Segoe UI", 8))
            axis_y2.setTitleFont(QFont("Segoe UI", 9, QFont.Medium))
            axis_y2.setGridLineColor(QColor(150, 150, 150, 60))
            chart2.addAxis(axis_y2, Qt.AlignLeft)
            series2.attachAxis(axis_y2)

            chart_view3 = QChartView(chart2)
            chart_view3.setRenderHint(QPainter.Antialiasing)
            chart_view3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Create custom title label
            title_label3 = QLabel(graph_title)
            title_label3.setAlignment(Qt.AlignCenter)
            title_label3.setFont(QFont("Segoe UI", 11, QFont.Bold))
            title_label3.setStyleSheet("color: rgb(33, 55, 80); margin: 5px;")
            title_label3.setWordWrap(True)

            container3 = QWidget()
            container3_layout = QVBoxLayout()
            container3_layout.setContentsMargins(10, 10, 10, 10)
            container3_layout.addWidget(title_label3)
            container3_layout.addWidget(chart_view3)
            container3.setLayout(container3_layout)
            container3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.set_glassmorphism_style(container3)

            shadow3 = QGraphicsDropShadowEffect()
            shadow3.setBlurRadius(20)
            shadow3.setOffset(5, 5)
            shadow3.setColor(QColor(0, 0, 0, 70))
            container3.setGraphicsEffect(shadow3)

            layout3.addWidget(container3)

        self.data3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def create_no_data_widget(self, title, message):
        """Create a widget to display when no data is available for charts"""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # Title label
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: rgb(33, 55, 80); margin: 5px;")
        title_label.setWordWrap(True)

        # No data message area
        no_data_area = QWidget()
        no_data_layout = QVBoxLayout()
        no_data_layout.setAlignment(Qt.AlignCenter)
        no_data_layout.setSpacing(15)

        # Message label
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        message_label.setStyleSheet("color: rgb(100, 100, 100); margin: 10px;")
        message_label.setWordWrap(True)

        # Instruction label
        instruction_label = QLabel("Create and publish an exam to view analytics")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setFont(QFont("Segoe UI", 10))
        instruction_label.setStyleSheet("color: rgb(120, 120, 120); font-style: italic;")
        instruction_label.setWordWrap(True)

        no_data_layout.addWidget(message_label)
        no_data_layout.addWidget(instruction_label)
        no_data_area.setLayout(no_data_layout)

        layout.addWidget(title_label)
        layout.addWidget(no_data_area, 1)  # Give it stretch to center vertically
        container.setLayout(layout)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Apply the same styling as your charts
        self.set_glassmorphism_style(container)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(5, 5)
        shadow.setColor(QColor(0, 0, 0, 70))
        container.setGraphicsEffect(shadow)

        return container

    
    def show_class_page(self):
        if self.faculty_stacked:
            self.faculty_stacked.setCurrentIndex(2)

            self.load_class_table()
        
        self.dashboardbtn.setChecked(False)
        self.studentstatsbtn.setChecked(False)
        self.classbtn.setChecked(True)
        self.examinationbtn.setChecked(False)
            
    def load_class_table(self):
        try:
            # Get references to UI elements
            class_table = self.faculty_ui.findChild(QTableWidget, "class_table")
            class_search = self.faculty_ui.findChild(QLineEdit, "class_search")
            class_sort = self.faculty_ui.findChild(QComboBox, "class_sort")
            
            if not class_table or not class_search or not class_sort:
                print("Could not find required UI elements")
                return
            
            # Set up the table columns
            class_table.setColumnCount(5)
            class_table.setHorizontalHeaderLabels(["ID Number", "Full Name", "Sex", "Birthdate", "Email"])
            class_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Fetch student data from database
            self.all_students = self.fetch_student_data()
            
            # Setup search functionality
            class_search.textChanged.connect(self.filter_students)
            
            # Setup sort functionality
            if class_sort.count() == 0:  # Avoid duplicating items if the function is called multiple times
                class_sort.addItem("All Students")
                class_sort.addItem("Male")
                class_sort.addItem("Female")
                class_sort.addItem("Names A-Z")
                class_sort.addItem("Names Z-A")
            
            class_sort.currentTextChanged.connect(self.sort_students)
            class_sort.setCurrentText("All Students")  # Ensure "All Students" is selected by default

            # Sort by numeric part of ID by default
            def extract_id_number(student):
                match = re.search(r'(\d+)$', student['id'])  # Extract the trailing number from ID
                return int(match.group(1)) if match else float('inf')

            sorted_students = sorted(self.all_students, key=extract_id_number)
            self.display_students(sorted_students)

        except Exception as e:
            print(f"Error in load_class_table: {e}")

    def fetch_student_data(self):
        students = []
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                
                # Fetch only the necessary columns for the class_table
                query = """
                    SELECT user_id, first_name, middle_name, last_name, suffix, 
                        birthdate, sex, emailaddress
                    FROM user_account 
                    WHERE role = 'STUDENT' AND status = 'approved'
                    ORDER BY last_name, first_name
                """
                cursor.execute(query)
                students_data = cursor.fetchall()
                
                # Process each student record
                for student in students_data:
                    # Create full name
                    name_parts = []
                    if student['first_name']:
                        name_parts.append(student['first_name'])
                    if student['middle_name'] and student['middle_name'] != "None":
                        name_parts.append(student['middle_name'])
                    if student['last_name']:
                        name_parts.append(student['last_name'])
                    if student['suffix'] and student['suffix'] != "None":
                        name_parts.append(student['suffix'])
                    
                    full_name = " ".join(name_parts)
                    
                    # Format date for display - fix the isinstance issue
                    birthdate = student['birthdate']
                    if birthdate:
                        try:
                            # Convert to string in a readable format
                            birthdate_display = birthdate.strftime("%B %d, %Y") if hasattr(birthdate, 'strftime') else str(birthdate)
                        except:
                            birthdate_display = str(birthdate)
                    else:
                        birthdate_display = "N/A"
                    
                    # Add student to the list
                    students.append({
                        'id': student['user_id'],
                        'full_name': full_name,
                        'sex': student['sex'],
                        'birthdate': birthdate_display,
                        'email': student['emailaddress'] or "N/A"
                    })
                
                cursor.close()
                connection.close()
        except mysql.connector.Error as e:
            print(f"Database error in fetch_student_data: {e}")
        except Exception as e:
            print(f"Error in fetch_student_data: {e}")
        
        return students
    
    def display_students(self, students):
        try:
            class_table = self.faculty_ui.findChild(QTableWidget, "class_table")

            # Hide vertical row numbers (left column)
            class_table.verticalHeader().setVisible(False)

            if not students:
                class_table.clear()
                class_table.setRowCount(1)
                class_table.setColumnCount(1)
                class_table.setHorizontalHeaderLabels([""])
                class_table.horizontalHeader().setVisible(False)
                class_table.setShowGrid(False)

                item = QTableWidgetItem("No students found.")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(Qt.GlobalColor.gray)
                item.setFont(QFont("Arial", 10, italic=True))
                item.setFlags(Qt.ItemFlag.NoItemFlags)

                class_table.setItem(0, 0, item)
                class_table.setSpan(0, 0, 1, 5)
                class_table.setEnabled(False)

            else:
                class_table.setEnabled(True)
                class_table.clearSpans()
                class_table.setShowGrid(True)
                class_table.horizontalHeader().setVisible(True)

                class_table.setColumnCount(5)
                class_table.setHorizontalHeaderLabels(["ID Number", "Full Name", "Sex", "Birthdate", "Email"])
                class_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                class_table.setRowCount(len(students))

                for row, student in enumerate(students):
                    class_table.setItem(row, 0, QTableWidgetItem(student['id']))
                    class_table.setItem(row, 1, QTableWidgetItem(student['full_name']))
                    class_table.setItem(row, 2, QTableWidgetItem(student['sex']))
                    class_table.setItem(row, 3, QTableWidgetItem(student['birthdate']))
                    class_table.setItem(row, 4, QTableWidgetItem(student['email']))
        except Exception as e:
            print(f"Error in display_students: {e}")



    def filter_students(self):
        try:
            search_text = self.faculty_ui.findChild(QLineEdit, "class_search").text().lower()
            sort_option = self.faculty_ui.findChild(QComboBox, "class_sort").currentText()
            
            # Apply search filter first
            filtered_students = []
            for student in self.all_students:
                if (search_text in student['full_name'].lower() or 
                    search_text in student['id'].lower() or 
                    search_text in student['birthdate'].lower() or 
                    search_text in student['email'].lower()):
                    filtered_students.append(student)
            
            # Then apply sort filter
            self.apply_sort_filter(filtered_students, sort_option)
        except Exception as e:
            print(f"Error in filter_students: {e}")

    def sort_students(self):
        try:
            search_text = self.faculty_ui.findChild(QLineEdit, "class_search").text().lower()
            sort_option = self.faculty_ui.findChild(QComboBox, "class_sort").currentText()
            
            # Apply search filter first
            filtered_students = []
            for student in self.all_students:
                if (search_text in student['full_name'].lower() or 
                    search_text in student['email'].lower()):
                    filtered_students.append(student)
            
            # Then apply sort filter
            self.apply_sort_filter(filtered_students, sort_option)
        except Exception as e:
            print(f"Error in sort_students: {e}")

    def apply_sort_filter(self, students, sort_option):
        try:
            def extract_id_number(student):
                match = re.search(r'(\d+)$', student['id'])  # Extract trailing digits from ID
                return int(match.group(1)) if match else float('inf')

            if sort_option == "Male":
                filtered_students = [s for s in students if s['sex'] == 'Male']
                filtered_students = sorted(filtered_students, key=extract_id_number)
            elif sort_option == "Female":
                filtered_students = [s for s in students if s['sex'] == 'Female']
                filtered_students = sorted(filtered_students, key=extract_id_number)
            elif sort_option == "Names A-Z":
                filtered_students = sorted(students, key=lambda s: s['full_name'])
            elif sort_option == "Names Z-A":
                filtered_students = sorted(students, key=lambda s: s['full_name'], reverse=True)
            elif sort_option == "All Students":
                filtered_students = sorted(students, key=extract_id_number)
            else:
                filtered_students = students

            self.display_students(filtered_students)
        except Exception as e:
            print(f"Error in apply_sort_filter: {e}")

    def show_exams_page(self):
        if self.faculty_stacked:
            self.faculty_stacked.setCurrentIndex(3)
        
        self.dashboardbtn.setChecked(False)
        self.studentstatsbtn.setChecked(False)
        self.classbtn.setChecked(False)
        self.examinationbtn.setChecked(True)

    def show_createexam_page(self):
            if self.faculty_stacked:
                self.faculty_stacked.setCurrentIndex(4)
                self.reset_exam_form_visibility()
                # Force a complete refresh when showing the page
                QTimer.singleShot(100, self.refresh_all_comboboxes)
            

    def refresh_all_comboboxes(self):
        """Force refresh of all combo boxes in the correct sequence"""
        if self.semester.isVisible():
            self.update_subject_code_options()
        self.update_exam_type_options()
        self.update_exam_parts_visibility()
        QApplication.processEvents()

    def show_settings_page(self):
        if self.faculty_stacked:
            self.load_user_settings()
            self.faculty_stacked.setCurrentIndex(5)

    def show_reset_password_dialog(self):
        loader = QUiLoader()
        reset_password_ui = loader.load(resource_path("UI/reset_password.ui"), self)

        self.reset_dialog = QDialog(self)
        self.reset_dialog.setWindowTitle("Reset Password")
        self.reset_dialog.setModal(True)
        self.reset_dialog.setLayout(QVBoxLayout())
        self.reset_dialog.layout().addWidget(reset_password_ui)

        self.reset_stacked_widget = reset_password_ui.findChild(QStackedWidget, "reset_stackedWidget")

        self.show_blurred_overlay()

        self.enter_email = reset_password_ui.findChild(QLineEdit, "Enter_email")
        self.enter_id = reset_password_ui.findChild(QLineEdit, "enter_ID")
        self.enter_id.textChanged.connect(lambda text: self.enter_id.setText(text.upper()))
        self.enter_OTP = reset_password_ui.findChild(QLineEdit, "enter_OTP")
        self.otp_timer = reset_password_ui.findChild(QLabel, "otp_timer")
        self.old_pass = reset_password_ui.findChild(QLabel, "old_pass")
        self.enter_old = reset_password_ui.findChild(QLineEdit, "enter_old")  
        self.enter_new = reset_password_ui.findChild(QLineEdit, "enter_new")
        self.confirm_new = reset_password_ui.findChild(QLineEdit, "confirm_new")
        self.verify_btn = reset_password_ui.findChild(QPushButton, "verify")
        self.verify_btn.setDefault(True)
        self.verify_btn.clicked.connect(self.check_otp_input)
        self.resetpass_btn = reset_password_ui.findChild(QPushButton, "reset_pass") 
        self.resend_otp_btn = reset_password_ui.findChild(QPushButton, "resend_otp")
        self.cancel_btn2 = reset_password_ui.findChild(QPushButton, "cancel_2") 
        self.cancel_btn = reset_password_ui.findChild(QPushButton, "cancel") 
        self.send_otp_btn = reset_password_ui.findChild(QPushButton, "send_OTP")

        self.reset_dialog.finished.connect(self.hide_blurred_overlay)
        self.add_eye_icon(self.enter_old)
        self.add_eye_icon(self.enter_new)
        self.add_eye_icon(self.confirm_new)

        if self.send_otp_btn:
            self.send_otp_btn.clicked.connect(self.send_otp_for_password_reset)

        if self.verify_btn:
            self.verify_btn.clicked.connect(self.verify_otp)
            self.verify_btn.clicked.connect(self.check_otp_input)

        if self.send_otp_btn and self.verify_btn and self.resetpass_btn and self.reset_stacked_widget:
            def enter_pressed_trigger():
                idx = self.reset_stacked_widget.currentIndex()
                if idx == 0:
                    self.send_otp_btn.click()
                elif idx == 1:
                    self.verify_btn.click()
                elif idx == 2:
                    self.resetpass_btn.click()

            enter_shortcut_return = QShortcut(QKeySequence("Return"), reset_password_ui)
            enter_shortcut_return.activated.connect(enter_pressed_trigger)

            enter_shortcut_enter = QShortcut(QKeySequence("Enter"), reset_password_ui)
            enter_shortcut_enter.activated.connect(enter_pressed_trigger)

        if self.resend_otp_btn:
            self.resend_otp_btn.clicked.connect(self.resend_otp)

        if self.cancel_btn:
            self.cancel_btn.clicked.connect(self.close_reset_password_dialog)

        if self.cancel_btn2:
            self.cancel_btn2.clicked.connect(self.close_reset_password_dialog)

        if self.resetpass_btn:
            self.resetpass_btn.clicked.connect(self.verify_pass)

        self.reset_dialog.exec()

    def check_otp_input(self):
        if not self.enter_OTP.text().strip():
            QMessageBox.critical(self, "Error", "Please enter the OTP.")
        else:
            # Proceed with OTP verification
            print("OTP entered:", self.enter_OTP.text())

    def add_eye_icon(self, password_field):
        if password_field:
            show_password_action = QAction(self)
            show_password_action.setIcon(QIcon(r"UI/Resources/hidden.png"))
            
            password_field.addAction(show_password_action, QLineEdit.TrailingPosition)
            password_field.setEchoMode(QLineEdit.Password)
            
            show_password_action.triggered.connect(
                lambda checked=False, field=password_field, action=show_password_action: 
                self.toggle_password_visibility(field, action))

    def toggle_password_visibility(self, password_field, show_password_action):
        if password_field.echoMode() == QLineEdit.Password:
            password_field.setEchoMode(QLineEdit.Normal)
            show_password_action.setIcon(QIcon(r"UI/Resources/show.png"))
        else:
            password_field.setEchoMode(QLineEdit.Password)
            show_password_action.setIcon(QIcon(r"UI/Resources/hidden.png"))

    def show_otp_page(self):
        user_id = self.enter_id.text().strip()
        email = self.enter_email.text().strip()

        if not user_id or not email:
            QMessageBox.warning(self.reset_dialog, "Error", "User ID and Email cannot be empty.")
            return  
        
        self.reset_stacked_widget.setCurrentIndex(1)

    def show_changepass_page(self):
        if self.reset_stacked_widget:
            self.reset_stacked_widget.setCurrentIndex(2) 

    def verify_otp(self):
        entered_otp = self.enter_OTP.text().strip()

        if not self.otp_valid:
            QMessageBox.warning(self.reset_dialog, "OTP Expired", "The OTP has expired. Please request a new one.")
            return

        if not re.fullmatch(r"\d{6}", entered_otp):
            QMessageBox.warning(self.reset_dialog, "Invalid OTP", "OTP must be a 6-digit number.")
            return

        if entered_otp == getattr(self, "generated_otp", None):
            QMessageBox.information(self.reset_dialog, "Success", "OTP Verified!")
            self.countdown_timer.stop()
            self.show_changepass_page()
        else:
            QMessageBox.warning(self.reset_dialog, "Error", "Incorrect OTP. Please try again.")

    def resend_otp(self):
        email = self.enter_email.text().strip()

        if not email:
            QMessageBox.warning(self.reset_dialog, "Error", "Email address cannot be empty.")
            return

        otp = self.generate_otp()
        self.generated_otp = otp
        self.send_otp_email(email, otp)
        self.start_otp_timer()

        QMessageBox.information(self.reset_dialog, "OTP Resent", "A new OTP has been sent to your email.")

    def verify_pass(self):
        entered_old_pass = self.enter_old.text().strip()
        entered_new_pass = self.enter_new.text().strip()
        entered_confirm_pass = self.confirm_new.text().strip()

        if not entered_old_pass or not entered_new_pass or not entered_confirm_pass:
            QMessageBox.warning(self.reset_dialog, "Error", "All fields must be filled.")
            return

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            # Fetch the current hashed password from the database
            cursor.execute("SELECT password FROM user_account WHERE user_id = %s", (self.enter_id.text().strip(),))
            result = cursor.fetchone()

            if result:
                hashed_password = result[0]

                # Check if the entered old password matches the hashed password
                if not bcrypt.checkpw(entered_old_pass.encode('utf-8'), hashed_password.encode('utf-8')):
                    QMessageBox.warning(self.reset_dialog, "Error", "Old password is incorrect.")
                    return

                # Check if the new password matches the old password
                if entered_new_pass == entered_old_pass:
                    QMessageBox.warning(self.reset_dialog, "Error", "Please create a new password that is different from the old password.")
                    return

                # Proceed to check if new passwords match
                if entered_new_pass != entered_confirm_pass:
                    QMessageBox.warning(self.reset_dialog, "Error", "New passwords do not match.")
                    return

                if not self.is_strong_password(entered_new_pass):
                    QMessageBox.warning(self.reset_dialog, "Error", "Password must be at least 8 characters long, contain both upper and lowercase letters, and atleast one number.")
                    return

                # Hash the new password and update it in the database
                new_hashed_password = self.hash_password(entered_new_pass)
                cursor.execute("UPDATE user_account SET password = %s WHERE user_id = %s", (new_hashed_password, self.enter_id.text().strip()))
                connection.commit()

                QMessageBox.information(self.reset_dialog, "Success", "Password changed successfully!")
                self.reset_dialog.close()

            else:
                QMessageBox.warning(self.reset_dialog, "Error", "User  ID does not exist.")

        except mysql.connector.Error as e:
            QMessageBox.warning(self.reset_dialog, "Error", f"An error occurred while updating your password: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def is_strong_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):  
            return False
        if not re.search(r"[a-z]", password): 
            return False
        if not re.search(r"[0-9]", password):  
            return False
        return True

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password
    
    def start_otp_timer(self):
            self.remaining_time = 60
            self.otp_valid = True
            self.otp_timer.setText(f"OTP valid for: {self.remaining_time} seconds")

            self.resend_otp_btn.setVisible(False)  # 🔴 Hide the resend button during countdown

            if hasattr(self, "countdown_timer") and self.countdown_timer.isActive():
                self.countdown_timer.stop()

            self.countdown_timer = QTimer()
            self.countdown_timer.timeout.connect(self.update_otp_timer)
            self.countdown_timer.start(1000)

    def update_otp_timer(self):
            self.remaining_time -= 1
            if self.remaining_time <= 0:
                self.countdown_timer.stop()
                self.otp_valid = False
                self.otp_timer.setText("OTP expired.")
                self.resend_otp_btn.setVisible(True)

                if self.reset_dialog.isVisible():  # ✅ Only show the message box if dialog is still open
                    QMessageBox.information(self.reset_dialog, "OTP Expired", "The OTP has expired. Please request a new one.")
            else:
                self.otp_timer.setText(f"OTP valid for: {self.remaining_time} seconds")

    def get_db_connection(self):
        return mysql.connector.connect(
            host="localhost",  
            user="root",  
            password="TUPCcoet@23!",  
            database="axis"  
        )

    def send_otp_email(self, user_email, otp):
        try:
            sender_email = "axistupcems@gmail.com"
            password = "ajiu rivz ttgw lzka"

            message = MIMEMultipart("alternative")
            message["From"] = sender_email
            message["To"] = user_email
            message["Subject"] = "Password Reset Request"

            html_body = f"""\
            <html>
                <body>
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Please use the following One-Time Password (OTP) to proceed with the password reset process:</p>
                    <p style="font-size: 24px; color: red; font-weight: bold;">{otp}</p>
                    <p>This OTP is valid for <strong>1 minute only</strong>.</p>
                    <p>If you did not request this change, please ignore this email or contact support immediately.</p>
                    <p>Thank you,<br>Axis Support Team</p>
                </body>
            </html>
            """
            message.attach(MIMEText(html_body, "html"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, user_email, message.as_string())
            server.quit()

            print("OTP email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")


    def generate_otp(self):
        return str(random.randint(100000, 999999))  

    def send_otp_for_password_reset(self):
        user_id = self.enter_id.text().strip()
        email = self.enter_email.text().strip()

        if not user_id or not email:
            QMessageBox.warning(self.reset_dialog, "Error", "User ID and Email cannot be empty.")
            return

        if user_id != self.user_id_label.text().strip():
            QMessageBox.warning(self.reset_dialog, "Error", "User ID does not match your account.")
            return

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT emailaddress FROM user_account WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self.reset_dialog, "Error", "User ID does not exist in the database.")
                return

            db_email = result[0]
            if email != db_email:
                QMessageBox.warning(self.reset_dialog, "Error", "Email does not match the registered email for this User ID.")
                return

            # All checks passed — show loading dialog now
            loading_dialog = QProgressDialog("Sending OTP email...", None, 0, 0, self.reset_dialog)
            loading_dialog.setWindowTitle("Please Wait")
            loading_dialog.setWindowModality(Qt.ApplicationModal)
            loading_dialog.setCancelButton(None)
            loading_dialog.setMinimumDuration(0)  # Optional: ensure it's visible
            loading_dialog.show()
            QApplication.processEvents()

            otp = self.generate_otp()
            self.generated_otp = otp
            self.send_otp_email(email, otp)
            self.start_otp_timer()

            self.reset_stacked_widget.setCurrentIndex(1)
            loading_dialog.cancel()
            QMessageBox.information(self.reset_dialog, "OTP Sent", "An OTP has been sent to your email.")

        except mysql.connector.Error as e:
            QMessageBox.warning(self.reset_dialog, "Error", f"An error occurred while checking your account: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def close_reset_password_dialog(self):
        if hasattr(self, 'reset_dialog') and self.reset_dialog:
            self.reset_dialog.close()

    def open_exam_result(self, user_id, exam_id):
        self.exam_result_window = ExamResult(exam_id, user_id)
        self.exam_result_window.show()

    def logout(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Logout Confirmation")
        msg_box.setText("Are you sure you want to log out?")
        msg_box.setIcon(QMessageBox.Question)
        
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No) 

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            self.login_window = Login_Register()  
            self.login_window.show()
            self.hide() 


class ExamTemplate(QMainWindow):
    def __init__(self, major_type, time_limit, subject_code, semester, exam_parts, user_id, user_role="faculty", exam_id=None, faculty_loaded_data=None, student_loaded_data=None, parent=None, current_window=None):
        super().__init__(parent)
        self.user_id = user_id
        self.user_role = user_role  
        self.exam_id = exam_id
        self.exam_type = major_type  
        self.exam_parts = exam_parts
        self.faculty_loaded_data = faculty_loaded_data
        self.student_loaded_data = student_loaded_data
        self.current_window = current_window

        loader = QUiLoader()
        self.exam_template = loader.load(resource_path("UI/exam_template.ui"), self)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.exam_template)
        self.setCentralWidget(self.stacked_widget) 
        self.showMaximized()

        Icons(self.exam_template)

        self.exam_template_stacked = self.exam_template.findChild(QStackedWidget, "exam_template_stackedWidget")

        self.major_type = self.exam_template.findChild(QLabel, "major_type")
        self.date_taken = self.exam_template.findChild(QLabel, "date_taken")
        self.time_limit = self.exam_template.findChild(QLabel, "time_limit")
        self.scroll_area = self.exam_template.findChild(QScrollArea, "scrollArea")
        self.title = self.exam_template.findChild(QLabel, "title")
        self.publish = self.exam_template.findChild(QPushButton, "publish")
        self.save_draft = self.exam_template.findChild(QPushButton, "save_draft")
        self.backbtn = self.exam_template.findChild(QPushButton, "back")
        self.container = QWidget()  
        self.container_layout = QVBoxLayout(self.container)

        if self.user_role == "faculty":
            self.backbtn.clicked.connect(self.show_faculty_class_page)
            self.publish.clicked.connect(self.publish_exam)
            self.save_draft.clicked.connect(self.save_exam_as_draft)
            self.publish.setText("Publish")
            self.save_draft.setText("Save Draft")
        else: 
            self.backbtn.clicked.connect(self.show_student_dashboard)  
            self.publish.setText("Submit Exam")
            self.publish.clicked.connect(self.submit_exam) 
            self.save_draft.hide()  
        
        self.button_groups = []
        self.question_widgets = [] 

        self.major_type.setText(major_type)
        self.time_limit.setText(f"Time Limit: {time_limit}")
        self.title.setText(f"{subject_code} - {semester}")
        self.time_limit.hide()
        self.date_taken.hide()

        self.populate_exam_questions(exam_parts)

        if self.faculty_loaded_data:
            self.populate_questions_with_faculty_loaded_data()

        if self.student_loaded_data:
            self.populate_questions_with_student_loaded_data()
        
        if self.exam_id and not self.faculty_loaded_data and self.user_role == "faculty":
            self.load_exam_data_faculty()

        if self.exam_id and not self.student_loaded_data and self.user_role == "student":
            self.load_exam_data_student()

        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True)

            
    def populate_questions_with_faculty_loaded_data(self):
        part_instructions_dict = {}
        
        if "multiple_choice" in self.faculty_loaded_data and self.faculty_loaded_data["multiple_choice"]:
            mc_data = self.faculty_loaded_data["multiple_choice"]
            mc_question_widgets = self.get_question_widgets_by_type_faculty("MULTIPLE CHOICES")
            
            for question_data in mc_data:
                if "description" in question_data and question_data["description"]:
                    part_index = self.determine_question_part_index_faculty("MULTIPLE CHOICES", mc_data.index(question_data))
                    if part_index is not None and part_index not in part_instructions_dict:
                        part_instructions_dict[part_index] = question_data["description"]

            for i, question_data in enumerate(mc_data):
                if i < len(mc_question_widgets):
                    widget = mc_question_widgets[i]
                    widget.input_widgets["question"].setText(question_data["question"])
                    
                    widget.input_widgets["answers"]["options"]["A"].setText(question_data["option_a"])
                    widget.input_widgets["answers"]["options"]["B"].setText(question_data["option_b"])
                    widget.input_widgets["answers"]["options"]["C"].setText(question_data["option_c"])
                    widget.input_widgets["answers"]["options"]["D"].setText(question_data["option_d"])
 
                    widget.input_widgets["answers"]["correct"].setCurrentText(question_data["correct_answer"])
        
        if "true_false" in self.faculty_loaded_data and self.faculty_loaded_data["true_false"]:
            tf_data = self.faculty_loaded_data["true_false"]
            tf_question_widgets = self.get_question_widgets_by_type_faculty("TRUE OR FALSE")
            
            for question_data in tf_data:
                if "description" in question_data and question_data["description"]:
                    part_index = self.determine_question_part_index_faculty("TRUE OR FALSE", tf_data.index(question_data))
                    if part_index is not None and part_index not in part_instructions_dict:
                        part_instructions_dict[part_index] = question_data["description"]
            
            for i, question_data in enumerate(tf_data):
                if i < len(tf_question_widgets):
                    widget = tf_question_widgets[i]
                    widget.input_widgets["question"].setText(question_data["question"])
                    widget.input_widgets["answers"]["correct"].setCurrentText(question_data["correct_answer"])
        
        if "identification" in self.faculty_loaded_data and self.faculty_loaded_data["identification"]:
            id_data = self.faculty_loaded_data["identification"]
            id_question_widgets = self.get_question_widgets_by_type_faculty("IDENTIFICATION")
            
            for question_data in id_data:
                if "description" in question_data and question_data["description"]:
                    part_index = self.determine_question_part_index_faculty("IDENTIFICATION", id_data.index(question_data))
                    if part_index is not None and part_index not in part_instructions_dict:
                        part_instructions_dict[part_index] = question_data["description"]
            
            for i, question_data in enumerate(id_data):
                if i < len(id_question_widgets):
                    widget = id_question_widgets[i]
                    widget.input_widgets["question"].setText(question_data["question"])
                    widget.input_widgets["answers"]["correct"].setText(question_data["correct_answer"])

        for part_index, description in part_instructions_dict.items():
            if part_index < len(self.part_instructions):
                self.part_instructions[part_index].setText(description)

    def determine_question_part_index_faculty(self, question_type, question_index):
        count = 0
        part_index = 0
        
        for i, (exam_type, num_items) in enumerate(self.exam_parts):
            if exam_type == question_type:
                if count <= question_index < count + num_items:
                    return i  
                count += num_items
            part_index += 1
        
        return None  
    
    def get_question_widgets_by_type_faculty(self, exam_type):
        widgets = []
        for type_name, questions in self.question_widgets:
            if type_name == exam_type:
                widgets.extend(questions)
        return widgets
    
    def load_exam_data_faculty(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM multiple_choice_exam WHERE exam_id = %s", (self.exam_id,))
            mc_results = cursor.fetchall()
            for mc in mc_results:
                for exam_type, questions in self.question_widgets:
                    if exam_type == "MULTIPLE CHOICES":
                        for box in questions:
                            if box.part_num == mc['part'] and box.question_num == mc['question_num']:
                                widgets = box.input_widgets
                                widgets['question'].setPlainText(mc['question'])
                                widgets['answers']['options']['A'].setPlainText(mc['option_a'])
                                widgets['answers']['options']['B'].setPlainText(mc['option_b'])
                                widgets['answers']['options']['C'].setPlainText(mc['option_c'])
                                widgets['answers']['options']['D'].setPlainText(mc['option_d'])
                                widgets['answers']['correct'].setCurrentText(mc['correct_answer'])

            cursor.execute("SELECT * FROM true_false_exam WHERE exam_id = %s", (self.exam_id,))
            tf_results = cursor.fetchall()
            for tf in tf_results:
                for exam_type, questions in self.question_widgets:
                    if exam_type == "TRUE OR FALSE":
                        for box in questions:
                            if box.part_num == tf['part'] and box.question_num == tf['question_num']:
                                widgets = box.input_widgets
                                widgets['question'].setPlainText(tf['question'])
                                widgets['answers']['correct'].setCurrentText(tf['correct_answer'])

            cursor.execute("SELECT * FROM identification_exam WHERE exam_id = %s", (self.exam_id,))
            id_results = cursor.fetchall()
            for ident in id_results:
                for exam_type, questions in self.question_widgets:
                    if exam_type == "IDENTIFICATION":
                        for box in questions:
                            if box.part_num == ident['part'] and box.question_num == ident['question_num']:
                                widgets = box.input_widgets
                                widgets['question'].setPlainText(ident['question'])
                                widgets['answers']['correct'].setText(ident['correct_answer'])

            all_parts = mc_results + tf_results + id_results
            for part_index, instruction_box in enumerate(self.part_instructions):
                for row in all_parts:
                    if row["part"] == part_index + 1:
                        instruction_box.setText(row["description"])
                        break

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load exam data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def populate_exam_questions(self, exam_parts):
        self.part_instructions = []  
        part_count = 1
        
        for part_index, (exam_type, num_items) in enumerate(exam_parts, start=1):
            part_label = QLabel(f"Part {part_index}: {exam_type}")
            part_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.container_layout.addWidget(part_label)

            instruction_text = "Enter your instructions..."
            instruction_box = AutoResizeTextEdit(instruction_text)
            instruction_box.setFixedHeight(50)
            instruction_box.setObjectName(f"instruction_part_{part_index}")
            
            if self.user_role == "student":
                instruction_box.setReadOnly(True)
                instruction_box.setFocusPolicy(Qt.NoFocus)
                instruction_box.setStyleSheet("""
                    QTextEdit {
                        background-color: #f5f5f5;
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QTextEdit:focus {
                        border: 1px solid #cccccc;
                    }
                """)
                
            self.part_instructions.append(instruction_box)
            self.container_layout.addWidget(instruction_box)

            part_questions = [] 
            for i in range(1, num_items + 1):
                question_widget = self.create_question_widget(i, exam_type, part_count)
                part_questions.append(question_widget)
                self.container_layout.addWidget(question_widget)
            
            self.question_widgets.append((exam_type, part_questions))
            part_count += 1

        self.container.setLayout(self.container_layout)

    def create_question_widget(self, q_num, exam_type, part_num):
        question_box = QGroupBox(f"Question {q_num}")
        question_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3373B9;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #F9F9E0;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
                background-color: #3373B9;
                color: white;
                border-radius: 5px;
            }
        """)
        question_layout = QVBoxLayout()

        question_input = AutoResizeTextEdit(f"Enter Question {q_num}...")
        question_input.setObjectName(f"question_{part_num}_{q_num}")
        
        if self.user_role == "student":
            question_input.setReadOnly(True)
            question_input.setFocusPolicy(Qt.NoFocus)
            question_input.setStyleSheet("""
                QTextEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 5px;
                }
                QTextEdit:focus {
                    border: 1px solid #cccccc;
                }
            """)
        
        question_layout.addWidget(question_input)

        answer_widgets = {}  

        if exam_type == "MULTIPLE CHOICES":
            options_layout = QVBoxLayout()
            button_group = QButtonGroup(self)
            self.button_groups.append(button_group)

            option_inputs = {}
            for opt in ["A", "B", "C", "D"]:
                opt_layout = QHBoxLayout()
                
                radio_button = QRadioButton(opt)
                radio_button.setStyleSheet("background-color: transparent;")
                radio_button.setObjectName(f"option_{part_num}_{q_num}_{opt}")
                radio_button.setEnabled(self.user_role == "student")
                
                if self.user_role == "student":
                    radio_button.setCursor(Qt.PointingHandCursor)
                
                button_group.addButton(radio_button)
                
                answer_input = AutoResizeTextEdit(f"Choice {opt}")
                answer_input.setObjectName(f"choice_{part_num}_{q_num}_{opt}")
                
                if self.user_role == "student":
                    answer_input.setReadOnly(True)
                    answer_input.setFocusPolicy(Qt.NoFocus)
                    answer_input.setStyleSheet("""
                        QTextEdit {
                            background-color: #f5f5f5;
                            border: 1px solid #cccccc;
                            border-radius: 5px;
                            padding: 5px;
                        }
                        QTextEdit:focus {
                            border: 1px solid #cccccc;
                        }
                    """)
                
                option_inputs[opt] = answer_input
                opt_layout.addWidget(radio_button)
                opt_layout.addWidget(answer_input)
                options_layout.addLayout(opt_layout)

            answer_widgets["options"] = option_inputs
            question_layout.addLayout(options_layout)
            
            if self.user_role == "faculty":
                correct_layout = self.create_correct_answer_section(["A", "B", "C", "D"])
                answer_widgets["correct"] = correct_layout.itemAt(1).itemAt(0).widget()  
                question_layout.addLayout(correct_layout)

        elif exam_type == "TRUE OR FALSE":
            tf_layout = QHBoxLayout()
            button_group = QButtonGroup(self)
            self.button_groups.append(button_group)

            true_btn = QRadioButton("True")
            true_btn.setObjectName(f"true_btn_{part_num}_{q_num}")
            
            false_btn = QRadioButton("False")
            false_btn.setObjectName(f"false_btn_{part_num}_{q_num}")

            true_btn.setEnabled(self.user_role == "student")
            false_btn.setEnabled(self.user_role == "student")
            
            if self.user_role == "student":
                true_btn.setCursor(Qt.PointingHandCursor)
                false_btn.setCursor(Qt.PointingHandCursor)

            button_group.addButton(true_btn)
            button_group.addButton(false_btn)

            tf_layout.addWidget(true_btn)
            tf_layout.addWidget(false_btn)
            question_layout.addLayout(tf_layout)
            
            if self.user_role == "faculty":
                correct_layout = self.create_correct_answer_section(["True", "False"])
                answer_widgets["correct"] = correct_layout.itemAt(1).itemAt(0).widget() 
                question_layout.addLayout(correct_layout)

        elif exam_type == "IDENTIFICATION":
            student_answer_input = QLineEdit()
            student_answer_input.setObjectName(f"student_answer_{part_num}_{q_num}")
            student_answer_input.setPlaceholderText("Enter your answer here...")
            
            if self.user_role == "student":
                student_answer_input.setEnabled(True)
                student_answer_input.setReadOnly(False)
                student_answer_input.setCursor(Qt.IBeamCursor)
                student_answer_input.setStyleSheet("""
                    QLineEdit {
                        background-color: #ffffff;
                        border: 2px solid #cccccc;
                        border-radius: 8px;
                        padding: 6px;
                        font-size: 14px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #3373B9;
                    }
                """)
            else:
                student_answer_input.setEnabled(False)
                student_answer_input.setStyleSheet(
                    "border: 2px solid #ccc; border-radius: 8px; padding: 6px; font-size: 14px; background-color: #f0f0f0;"
                )

            question_layout.addWidget(student_answer_input)

            if self.user_role == "faculty":
                correct_layout = self.create_correct_answer_section(is_text=True)
                answer_widgets["correct"] = correct_layout.itemAt(1).itemAt(0).widget()  
                question_layout.addLayout(correct_layout)

        question_box.setLayout(question_layout)
        question_box.exam_type = exam_type
        question_box.question_num = q_num
        question_box.part_num = part_num
        question_box.input_widgets = {
            "question": question_input,
            "answers": answer_widgets
        }
        return question_box

    def create_correct_answer_section(self, options=None, is_text=False):
        correct_answer_layout = QVBoxLayout()
        correct_answer_label = QLabel("Correct Answer:")
        correct_answer_label.setStyleSheet("font-size: 15px; font-weight: bold; background-color: transparent;")
        correct_answer_layout.addWidget(correct_answer_label)

        answer_layout = QHBoxLayout()
        if is_text:
            correct_answer_input = QLineEdit()
            correct_answer_input.setPlaceholderText("Enter correct answer...")
            correct_answer_input.setStyleSheet("border: 2px solid #ccc; border-radius: 8px; padding: 6px; font-size: 14px;")
            answer_layout.addWidget(correct_answer_input)
        else:
            correct_answer_combo = QComboBox()
            correct_answer_combo.addItems(options)
            correct_answer_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    border: 1px solid #B8D5E7;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 15px;
                    color: #215988;
                    font-weight: bold;
                    selection-background-color: #FF5929;
                    transition: border-color 0.3s ease, box-shadow 0.3s ease;
                }
                QComboBox:focus {
                    border: 1px solid #00cc00;
                    box-shadow: 0px 0px 5px rgba(255, 89, 41, 0.3);
                    background-color: white;
                }
                QComboBox QAbstractItemView {
                    background: white;
                    border: 1px solid #B8D5E7;
                    selection-background-color: #00cc00;
                    color: #215988;
                }
            """)
            correct_answer_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            answer_layout.addWidget(correct_answer_combo)

        answer_layout.addStretch()
        correct_answer_layout.addLayout(answer_layout)
        return correct_answer_layout

    def collect_exam_data(self):
        exam_data = {
            "multiple_choice": [],
            "true_false": [],
            "identification": []
        }
        
        for part_index, (exam_type, questions) in enumerate(self.question_widgets):
            instruction = self.part_instructions[part_index].toPlainText()
            
            for question_box in questions:
                widgets = question_box.input_widgets
                question_text = widgets["question"].toPlainText()
                question_num = question_box.question_num
                part_num = question_box.part_num
                
                if exam_type == "MULTIPLE CHOICES":
                    options = {
                        'A': widgets["answers"]["options"]["A"].toPlainText(),
                        'B': widgets["answers"]["options"]["B"].toPlainText(),
                        'C': widgets["answers"]["options"]["C"].toPlainText(),
                        'D': widgets["answers"]["options"]["D"].toPlainText()
                    }
                    correct_answer = widgets["answers"]["correct"].currentText()
                    
                    exam_data["multiple_choice"].append({
                        "part": part_num,
                        "question_num": question_num,
                        "description": instruction,
                        "question": question_text,
                        "option_a": options['A'],
                        "option_b": options['B'],
                        "option_c": options['C'],
                        "option_d": options['D'],
                        "correct_answer": correct_answer
                    })
                    
                elif exam_type == "TRUE OR FALSE":
                    correct_answer = widgets["answers"]["correct"].currentText()
                    
                    exam_data["true_false"].append({
                        "part": part_num,
                        "question_num": question_num,
                        "description": instruction,
                        "question": question_text,
                        "correct_answer": correct_answer
                    })
                    
                elif exam_type == "IDENTIFICATION":
                    correct_answer = widgets["answers"]["correct"].text()
                    
                    exam_data["identification"].append({
                        "part": part_num,
                        "question_num": question_num,
                        "description": instruction,
                        "question": question_text,
                        "correct_answer": correct_answer
                    })
        
        return exam_data

    def set_exam_schedule(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Exam Schedule")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)

        date_label = QLabel("Select Exam Date:")
        date_picker = QDateEdit()
        date_picker.setCalendarPopup(True)
        date_picker.setDate(QDate.currentDate())

        start_time_label = QLabel("Start Time:")
        start_time_edit = QTimeEdit()
        start_time_edit.setDisplayFormat("hh:mm AP")
        start_time_edit.setTime(QTime.currentTime())

        end_time_label = QLabel("End Time:")
        end_time_edit = QTimeEdit()
        end_time_edit.setDisplayFormat("hh:mm AP")
        end_time_edit.setTime(QTime.currentTime().addSecs(3600))  # default +1 hour

        # Calculate minimum time limit
        total_items = sum(len(q_list) for _, q_list in self.question_widgets)
        min_minutes = total_items * 2  # 2 minutes per item
        min_hours = min_minutes // 60
        min_remaining_minutes = min_minutes % 60

        hour_label = QLabel("Time Limit (Hours):")
        hour_input = QSpinBox()
        hour_input.setRange(min_hours, 5)

        minute_label = QLabel("Time Limit (Minutes):")
        minute_input = QSpinBox()
        minute_input.setRange(0, 59)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(date_label)
        layout.addWidget(date_picker)
        layout.addWidget(start_time_label)
        layout.addWidget(start_time_edit)
        layout.addWidget(end_time_label)
        layout.addWidget(end_time_edit)
        layout.addWidget(hour_label)
        layout.addWidget(hour_input)
        layout.addWidget(minute_label)
        layout.addWidget(minute_input)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            selected_date = date_picker.date()
            selected_time = start_time_edit.time()
            datetime_combined = QDateTime(selected_date, selected_time)

            # Convert to Python datetime for comparison
            selected_start_datetime = datetime(
                selected_date.year(), selected_date.month(), selected_date.day(),
                start_time_edit.time().hour(), start_time_edit.time().minute()
            )
            current_datetime = datetime.now()
            current_datetime_rounded = current_datetime.replace(second=0, microsecond=0)
            if selected_start_datetime < current_datetime_rounded:
                QMessageBox.warning(self, "Invalid Schedule", "You cannot schedule an exam in the past.")
                return False

            start_dt = datetime(
                selected_date.year(), selected_date.month(), selected_date.day(),
                start_time_edit.time().hour(), start_time_edit.time().minute()
            )
            end_dt = datetime(
                selected_date.year(), selected_date.month(), selected_date.day(),
                end_time_edit.time().hour(), end_time_edit.time().minute()
            )
            allowed_duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
            entered_total_minutes = hour_input.value() * 60 + minute_input.value()

            if allowed_duration_minutes < min_minutes:
                QMessageBox.warning(
                    self,
                    "Invalid Schedule",
                    f"The selected time window is too short.\nYou need at least {min_minutes} minutes for {total_items} items."
                )
                return False

            # Restriction: Time limit must not exceed the exam time window
            if entered_total_minutes > allowed_duration_minutes:
                QMessageBox.warning(
                    self,
                    "Invalid Time Limit",
                    f"The entered time limit ({entered_total_minutes} min) exceeds the allowed duration "
                    f"between start and end time ({allowed_duration_minutes} min)."
                )
                return False

            # Restriction: Time limit must not be less than the minimum time per question
            if entered_total_minutes < min_minutes:
                QMessageBox.warning(
                    self,
                    "Invalid Time Limit",
                    f"The minimum time allowed for {total_items} items is {min_minutes} minutes."
                )
                return False

            # All good: Save values
            self.exam_date = datetime_combined.toString("yyyy-MM-dd hh:mm AP")
            self.exam_date_only = selected_date.toString("yyyy-MM-dd")
            self.exam_time_limit = (hour_input.value(), minute_input.value())

            start_12hr = start_time_edit.time().toString("hh:mm AP")
            end_12hr = end_time_edit.time().toString("hh:mm AP")
            self.exam_schedule_time = f"{start_12hr} - {end_12hr}"
            self.exam_schedule_display = self.exam_schedule_time

            QMessageBox.information(
                self,
                "Exam Scheduled",
                f"📅 Date: {self.exam_date}\n"
                f"⏳ Time Limit: {self.exam_time_limit[0]} hr {self.exam_time_limit[1]} min\n"
                f"🕒 Schedule: {self.exam_schedule_display}"
            )
            return True

        return False

  
    def save_to_database(self, exam_status=False):
        if not self.exam_id:
            QMessageBox.critical(self, "Error", "Missing exam ID. Cannot save to database.")
            return False
        
        try:
            if not hasattr(self, 'exam_date') or not self.exam_date:
                if exam_status:
                    self.exam_date = datetime.now().strftime("%Y-%m-%d")
                else:
                    self.exam_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            else:
                if exam_status and hasattr(self, 'exam_date_only'):
                    self.exam_date = self.exam_date_only

            if not hasattr(self, 'exam_schedule_time') or not self.exam_schedule_time:
                self.exam_schedule_time = ""  

            
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            
            if connection.is_connected():
                cursor = connection.cursor()

                try:
                    cursor.execute("DESCRIBE examination_form")
                    columns = cursor.fetchall()
                    exam_date_type = None
                    
                    for column in columns:
                        if column[0] == 'exam_date':
                            exam_date_type = column[1]
                            break
                    
                    if exam_date_type and ('varchar' not in exam_date_type.lower() and 'text' not in exam_date_type.lower()):
                        cursor.execute("ALTER TABLE examination_form MODIFY exam_date VARCHAR(50)")
                        connection.commit()
                except Exception as e:
                    pass
                
                cursor.execute("SELECT COUNT(*) FROM examination_form WHERE exam_id = %s", (self.exam_id,))
                exists = cursor.fetchone()[0] > 0
                
                if not exists:
                    insert_exam_query = """
                    INSERT INTO examination_form (exam_id, exam_status, exam_date, schedule_time) 
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_exam_query, (
                        self.exam_id, 
                        "Published" if exam_status else "Draft", 
                        self.exam_date, 
                        self.exam_schedule_time
                    ))
                else:
                    cursor.execute(""" 
                        UPDATE examination_form 
                        SET exam_status = %s, exam_date = %s, schedule_time = %s 
                        WHERE exam_id = %s
                    """, (
                        "Published" if exam_status else "Draft", 
                        self.exam_date, 
                        self.exam_schedule_time, 
                        self.exam_id
                    ))
                
                exam_data = self.collect_exam_data()

                # Delete existing questions for this exam
                cursor.execute("DELETE FROM multiple_choice_exam WHERE exam_id = %s", (self.exam_id,))
                cursor.execute("DELETE FROM true_false_exam WHERE exam_id = %s", (self.exam_id,))
                cursor.execute("DELETE FROM identification_exam WHERE exam_id = %s", (self.exam_id,))
                
                # Generate and assign unique IDs for multiple choice questions
                if exam_data["multiple_choice"]:
                    # Get the highest existing MC ID number
                    cursor.execute("SELECT MAX(CAST(SUBSTRING(id, 3) AS UNSIGNED)) FROM multiple_choice_exam WHERE id LIKE 'MC%'")
                    result = cursor.fetchone()
                    mc_next_num = 1 if result[0] is None else result[0] + 1
                    
                    multiple_choice_query = """
                    INSERT INTO multiple_choice_exam 
                    (id, exam_id, part, question_num, description, question, option_a, option_b, option_c, option_d, correct_answer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    for question in exam_data["multiple_choice"]:
                        question_id = f"MC{mc_next_num:03d}"
                        mc_next_num += 1
                        
                        data = (
                            question_id,
                            self.exam_id,
                            question["part"],
                            question["question_num"],
                            question["description"],
                            question["question"],
                            question["option_a"],
                            question["option_b"],
                            question["option_c"],
                            question["option_d"],
                            question["correct_answer"]
                        )
                        cursor.execute(multiple_choice_query, data)

                # Generate and assign unique IDs for true/false questions
                if exam_data["true_false"]:
                    # Get the highest existing TF ID number
                    cursor.execute("SELECT MAX(CAST(SUBSTRING(id, 3) AS UNSIGNED)) FROM true_false_exam WHERE id LIKE 'TF%'")
                    result = cursor.fetchone()
                    tf_next_num = 1 if result[0] is None else result[0] + 1
                    
                    true_false_query = """
                    INSERT INTO true_false_exam 
                    (id, exam_id, part, question_num, description, question, correct_answer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    for question in exam_data["true_false"]:
                        question_id = f"TF{tf_next_num:03d}"
                        tf_next_num += 1
                        
                        data = (
                            question_id,
                            self.exam_id,
                            question["part"],
                            question["question_num"],
                            question["description"],
                            question["question"],
                            question["correct_answer"]
                        )
                        cursor.execute(true_false_query, data)
                
                # Generate and assign unique IDs for identification questions
                if exam_data["identification"]:
                    # Get the highest existing IC ID number
                    cursor.execute("SELECT MAX(CAST(SUBSTRING(id, 3) AS UNSIGNED)) FROM identification_exam WHERE id LIKE 'IC%'")
                    result = cursor.fetchone()
                    ic_next_num = 1 if result[0] is None else result[0] + 1
                    
                    identification_query = """
                    INSERT INTO identification_exam 
                    (id, exam_id, part, question_num, description, question, correct_answer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    for question in exam_data["identification"]:
                        question_id = f"IC{ic_next_num:03d}"
                        ic_next_num += 1
                        
                        data = (
                            question_id,
                            self.exam_id,
                            question["part"],
                            question["question_num"],
                            question["description"],
                            question["question"],
                            question["correct_answer"]
                        )
                        cursor.execute(identification_query, data)

                status = "Published" if exam_status else "Draft"
                cursor.execute("""
                    UPDATE examination_form 
                    SET exam_status = %s, exam_date = %s, schedule_time = %s, time_limit = %s 
                    WHERE exam_id = %s
                """, (
                    status,
                    self.exam_date,
                    self.exam_schedule_time,
                    f"{self.exam_time_limit[0]:02d}:{self.exam_time_limit[1]:02d}" if hasattr(self, 'exam_time_limit') else None,
                    self.exam_id
                ))
                
                connection.commit()
                
                return True
                
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            return False
            
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def publish_exam(self):
        user_id = self.user_id 

        if not user_id:
            QMessageBox.critical(self, "Error", "Invalid user ID. Cannot publish exam.")
            return

        if not self.validate_exam_data():
            QMessageBox.warning(self, "Incomplete Data", "Please complete all required fields before publishing.")
            return

        if not self.set_exam_schedule():
            return

        if self.save_to_database(exam_status=True):
            QMessageBox.information(self, "Success", "Exam has been published successfully!")

            # Fetch instructor name
            instructor_name = self.get_instructor_fullname(user_id)
            semester, subject_code = self.get_exam_details(self.exam_id)
            exam_schedule = self.exam_schedule_time
            exam_date = self.exam_date

            # Create notification message
            message = (
                f"📢 A new exam (ID: {self.exam_id}) has been published.\n"
                f"📝 Instructor: {instructor_name}\n"
                f"📅 Semester: {semester}\n"
                f"📚 Subject Code: {subject_code}\n"
                f"📆 Exam Date: {exam_date}\n"
                f"⏰ Exam Scheduled for: {exam_schedule}\n\n"
                f"Check the exam schedule and prepare!"
            )

            # Send notification
            notification_manager = NotificationManager(parent=self)
            notification_manager.send_notification(
                sender_id=user_id,
                recipient_role='Student',
                message=message,
                recipient_id=None  # Send to all students
            )

            self.show_faculty_exam_page(user_id)

    def get_instructor_fullname(self, user_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT first_name, middle_name, last_name, suffix 
                FROM user_account 
                WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()
            if user:
                fullname = f"{user['first_name']} "
                if user['middle_name']:
                    fullname += f"{user['middle_name'][0]}. "
                fullname += f"{user['last_name']}"
                if user['suffix']:
                    fullname += f", {user['suffix']}"
                return fullname
            else:
                return "Unknown Instructor"
        except:
            return "Unknown Instructor"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_exam_details(self, exam_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT semester, subject_code 
                FROM examination_form 
                WHERE exam_id = %s 
                LIMIT 1
            """, (exam_id,))
            exam = cursor.fetchone()
            if exam:
                return exam['semester'], exam['subject_code']
            else:
                return "N/A", "N/A"
        except:
            return "N/A", "N/A"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def save_exam_as_draft(self):
        if self.save_to_database(exam_status=False):
            QMessageBox.information(self, "Success", "Exam has been saved as a draft.")
            self.show_faculty_exam_page(self.user_id)

    def validate_exam_data(self):
        exam_data = self.collect_exam_data()
        
        # Clear any previous highlighting
        self.clear_field_highlighting()
        
        all_valid = True
        # Track the first invalid field to scroll to
        first_invalid_field = None
        
        for exam_type, questions in exam_data.items():
            for question in questions:
                part_num = question["part"]
                question_num = question["question_num"]
                
                # Find the corresponding widget
                question_widget = self.find_question_widget(part_num, question_num, exam_type)
                
                if not question_widget:
                    continue
                    
                # Validate question text
                if question["question"] == f"Enter Question {question_num}..." or not question["question"].strip():
                    all_valid = False
                    self.highlight_field(question_widget.input_widgets["question"])
                    if not first_invalid_field:
                        first_invalid_field = question_widget.input_widgets["question"]
                
                # Validate correct answer for faculty
                if self.user_role == "faculty":
                    if exam_type == "multiple_choice":
                        # Check each option
                        for opt_key, option_letter in zip(["option_a", "option_b", "option_c", "option_d"], ["A", "B", "C", "D"]):
                            if not question[opt_key].strip() or question[opt_key] == f"Choice {option_letter}":
                                all_valid = False
                                self.highlight_field(question_widget.input_widgets["answers"]["options"][option_letter])
                                if not first_invalid_field:
                                    first_invalid_field = question_widget.input_widgets["answers"]["options"][option_letter]
                    
                    # Check correct answer field
                    if "correct_answer" in question:
                        if exam_type == "multiple_choice" or exam_type == "true_false":
                            # These have dropdown menus which are pre-filled, so no need to check them
                            pass
                        elif exam_type == "identification":
                            if not question["correct_answer"].strip() or question["correct_answer"] == "Enter correct answer...":
                                all_valid = False
                                self.highlight_field(question_widget.input_widgets["answers"]["correct"])
                                if not first_invalid_field:
                                    first_invalid_field = question_widget.input_widgets["answers"]["correct"]
                
                # Check part instructions
                part_idx = part_num - 1
                if part_idx < len(self.part_instructions):
                    instruction_text = self.part_instructions[part_idx].toPlainText()
                    if instruction_text == "Enter your instructions..." or not instruction_text.strip():
                        all_valid = False
                        self.highlight_field(self.part_instructions[part_idx])
                        if not first_invalid_field:
                            first_invalid_field = self.part_instructions[part_idx]
        
        # Scroll to the first invalid field if found
        if first_invalid_field:
            self.scroll_to_widget(first_invalid_field)
        
        return all_valid
    
    def highlight_field(self, widget):
        """Apply red border highlighting to a field"""
        if isinstance(widget, QTextEdit) or isinstance(widget, AutoResizeTextEdit):
            widget.setStyleSheet("""
                QTextEdit {
                    border: 2px solid #FF0000;
                    border-radius: 5px;
                    background-color: #FFEEEE;
                    padding: 5px;
                }
            """)
        elif isinstance(widget, QLineEdit):
            widget.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #FF0000;
                    border-radius: 8px;
                    background-color: #FFEEEE;
                    padding: 6px;
                    font-size: 14px;
                }
            """)
        elif isinstance(widget, QComboBox):
            widget.setStyleSheet("""
                QComboBox {
                    background-color: #FFEEEE;
                    border: 2px solid #FF0000;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 15px;
                    color: #215988;
                    font-weight: bold;
                    selection-background-color: #FF5929;
                }
            """)

    def clear_field_highlighting(self):
        """Remove all red border highlighting"""
        # Reset all part instructions
        for instruction in self.part_instructions:
            instruction.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
        
        # Reset all question fields
        for exam_type, questions in self.question_widgets:
            for question_box in questions:
                widgets = question_box.input_widgets
                
                # Reset question text
                widgets["question"].setStyleSheet("""
                    QTextEdit {
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        padding: 5px;
                    }
                """)
                
                # Reset answers based on type
                if exam_type == "MULTIPLE CHOICES":
                    for option_key in ["A", "B", "C", "D"]:
                        widgets["answers"]["options"][option_key].setStyleSheet("""
                            QTextEdit {
                                border: 1px solid #cccccc;
                                border-radius: 5px;
                                padding: 5px;
                            }
                        """)
                    
                    # Reset dropdown
                    if "correct" in widgets["answers"]:
                        widgets["answers"]["correct"].setStyleSheet("""
                            QComboBox {
                                background-color: white;
                                border: 1px solid #B8D5E7;
                                border-radius: 6px;
                                padding: 8px 12px;
                                font-size: 15px;
                                color: #215988;
                                font-weight: bold;
                                selection-background-color: #FF5929;
                                transition: border-color 0.3s ease, box-shadow 0.3s ease;
                            }
                        """)
                
                elif exam_type == "TRUE OR FALSE":
                    if "correct" in widgets["answers"]:
                        widgets["answers"]["correct"].setStyleSheet("""
                            QComboBox {
                                background-color: white;
                                border: 1px solid #B8D5E7;
                                border-radius: 6px;
                                padding: 8px 12px;
                                font-size: 15px;
                                color: #215988;
                                font-weight: bold;
                                selection-background-color: #FF5929;
                                transition: border-color 0.3s ease, box-shadow 0.3s ease;
                            }
                        """)
                
                elif exam_type == "IDENTIFICATION":
                    if "correct" in widgets["answers"]:
                        widgets["answers"]["correct"].setStyleSheet("""
                            QLineEdit {
                                border: 2px solid #ccc;
                                border-radius: 8px;
                                padding: 6px;
                                font-size: 14px;
                            }
                        """)

    def find_question_widget(self, part_num, question_num, exam_type):
        """Find a question widget by part number, question number and type"""
        exam_type_map = {
            "multiple_choice": "MULTIPLE CHOICES",
            "true_false": "TRUE OR FALSE",
            "identification": "IDENTIFICATION"
        }
        
        mapped_type = exam_type_map.get(exam_type)
        if not mapped_type:
            return None
        
        for type_name, questions in self.question_widgets:
            if type_name == mapped_type:
                for question_box in questions:
                    if question_box.part_num == part_num and question_box.question_num == question_num:
                        return question_box
        
        return None
    
    def scroll_to_widget(self, widget):
        """Scroll the view to make a widget visible"""
        if widget and hasattr(self, 'scroll_area'):
            self.scroll_area.ensureWidgetVisible(widget, xmargin=10, ymargin=10)


    def show_faculty_class_page(self, user_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to go back?\nYou can choose to save this exam as a draft before leaving.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            save_choice = QMessageBox.question(
                self,
                "Save Exam",
                "Do you want to save this exam as a draft before going back?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel
            )

            if save_choice == QMessageBox.Yes:
                self.save_exam_as_draft()
            elif save_choice == QMessageBox.Cancel:
                return 

        self.current_window = Faculty(user_id)
        self.current_window.faculty_stacked.setCurrentIndex(4)
        self.current_window.load_exam_lists()
        self.current_window.show()
        self.hide()
                
    
    def show_faculty_exam_page(self, user_id):  
        self.current_window = Faculty(user_id)
        self.current_window.faculty_stacked.setCurrentIndex(3)
        self.current_window.load_exam_lists()
        self.current_window.show()
        self.hide()


class ConductExam(QMainWindow):
    def __init__(self, major_type, time_limit, subject_code, semester, exam_parts, user_id, start_time, user_role="faculty", exam_id=None, faculty_loaded_data=None, student_loaded_data=None, parent=None, current_window=None, student_dashboard=None):
        super().__init__(parent)
        self.user_id = user_id
        self.user_role = user_role  
        self.exam_id = exam_id
        self.exam_type = major_type  
        self.exam_parts = exam_parts
        self.faculty_loaded_data = faculty_loaded_data
        self.student_loaded_data = student_loaded_data
        self.current_window = current_window
        self.start_time = start_time
        self.student_dashboard = student_dashboard 

        loader = QUiLoader()
        self.exam_template = loader.load(resource_path("UI/exam_template.ui"), self)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.exam_template)
        self.setCentralWidget(self.stacked_widget) 
        self.showMaximized()

        Icons(self.exam_template)

        self.notification_manager = NotificationManager(self)
        self.exam_template_stacked = self.exam_template.findChild(QStackedWidget, "exam_template_stackedWidget")

        self.major_type = self.exam_template.findChild(QLabel, "major_type")
        self.date_taken = self.exam_template.findChild(QLabel, "date_taken")
        self.time_limit = self.exam_template.findChild(QLabel, "time_limit")
        self.scroll_area = self.exam_template.findChild(QScrollArea, "scrollArea")
        self.title = self.exam_template.findChild(QLabel, "title")
        self.publish = self.exam_template.findChild(QPushButton, "publish")
        self.save_draft = self.exam_template.findChild(QPushButton, "save_draft")
        self.backbtn = self.exam_template.findChild(QPushButton, "back")
        self.container = QWidget()  
        self.container_layout = QVBoxLayout(self.container)

        self.exam_date = None
        self.exam_time_limit = (0, 0)  # (hours, minutes)
        self.remaining_time = 0  # in seconds

        self.set_exam_time_limit(time_limit)

        try:
            self.date_taken.setText(f"Date Taken: {datetime.now().strftime('%B %#d, %Y')}")  # For Windows
        except:
            self.date_taken.setText(f"Date Taken: {datetime.now().strftime('%B %-d, %Y')}")  # For Linux/macOS

        if self.user_role == "faculty":
            self.backbtn.clicked.connect(self.show_faculty_class_page)
            self.publish.clicked.connect(self.publish_exam)
            self.save_draft.clicked.connect(self.save_exam_as_draft)
            self.publish.setText("Publish")
            self.save_draft.setText("Save Draft")
        else:  
            self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.backbtn.clicked.connect(self.show_student_dashboard)  
            self.publish.setText("Submit Exam")
            self.publish.clicked.connect(self.submit_exam)  
            self.save_draft.hide() 
        
        self.button_groups = []
        self.question_widgets = [] 

        self.major_type.setText(major_type)
        self.time_limit.setText(f"Time Limit: {time_limit}")
        self.title.setText(f"{subject_code} - {semester}")

        self.populate_exam_questions(exam_parts)

        if self.faculty_loaded_data:
            self.populate_questions_with_faculty_loaded_data()

        if self.student_loaded_data:
            self.populate_questions_with_student_loaded_data()
        
        if self.exam_id and not self.faculty_loaded_data and self.user_role == "faculty":
            self.load_exam_data_faculty()

        if self.exam_id and not self.student_loaded_data and self.user_role == "student":
            self.load_exam_data_student()

        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # Update every second

    def get_creator(self, exam_id):
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="TUPCcoet@23!",
                    database="axis"
                )
                cursor = connection.cursor(dictionary=True)
                query = "SELECT created_by FROM examination_form WHERE exam_id = %s LIMIT 1"
                cursor.execute(query, (exam_id,))
                result = cursor.fetchone()
                return result['created_by'] if result else "Unknown Creator"
            except Exception as e:
                print(f"Error: {e}")
                return "Unknown Creator"
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def set_exam_time_limit(self, time_limit):
        parts = time_limit.strip().split(':')
        hours = int(parts[0]) if len(parts) > 0 else 0
        minutes = int(parts[1]) if len(parts) > 1 else 0
        seconds = int(parts[2]) if len(parts) > 2 else 0

        self.remaining_time = hours * 3600 + minutes * 60 + seconds
        # Set initial display of time limit in hh:mm:ss format
        self.update_time_limit_label()

    def update_timer(self):
        if self.user_role == "student" and self.backbtn.isVisible():
            self.backbtn.hide()

        if self.remaining_time <= 0:
            if self.exam_template.isVisible():
                self.time_limit.setText("00:00")
                self.timer.stop()
                self.submit_exam(auto_submit=True)
            else:
                print("Exam template is not visible. Auto-submit will not occur.")
            return

        self.remaining_time -= 1
        self.update_time_limit_label()

    def update_time_limit_label(self):
        # Format remaining time as mm:ss if less than 1 hour, else hh:mm:ss
        hours = self.remaining_time // 3600
        minutes = (self.remaining_time % 3600) // 60
        seconds = self.remaining_time % 60
        if hours > 0:
            time_str = f"{hours}:{minutes:02d}:{seconds:02d}"  # e.g. 1:30:00
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"  # e.g. 59:59
        self.time_limit.setText(f"Time Limit: {time_str}")

    def submit_exam(self, auto_submit=False):
        print("\n=== SUBMIT EXAM TRIGGERED ===")

        if not auto_submit:
            # Check for unanswered questions
            unanswered_questions = self.get_unanswered_questions()
            
            if unanswered_questions:
                # Show warning about unanswered questions
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Unanswered Questions")
                msg_box.setText(f"Are you sure you want to submit? There are still {len(unanswered_questions)} questions you haven't answered.")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.No)
                
                result = msg_box.exec()
                
                if result == QMessageBox.No:
                    print("User chose to review unanswered questions")
                    self.highlight_unanswered_questions(unanswered_questions)
                    self.scroll_to_first_unanswered(unanswered_questions)
                    return
                else:
                    print("User chose to submit despite unanswered questions")
            else:
                # All questions answered - show normal confirmation
                confirmation = QMessageBox.question(
                    self, "Submit Exam",
                    "Are you sure you want to submit your exam?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirmation != QMessageBox.Yes:
                    print("User cancelled submission")
                    return
        else:
            print("Auto-submit triggered due to time expiration")

        print("User confirmed submission")
        answers = self.collect_student_answers()
        print(f"Answers collected, proceeding to save")

        # Save answers and get result
        success, correct_answers, total_questions = self.save_student_answers_to_db(answers)
        print(f"Save result: success={success}, correct={correct_answers}, total={total_questions}")

        if success:
            self.correct_answers = correct_answers  # For SubmissionSuccessDialog
            self.total_questions = total_questions

            # Optional: update performance in the backend if needed
            self.update_student_performance(correct_answers, total_questions)

            # Notify faculty after successful submission
            student_name = self.get_student_full_name(self.user_id)
            semester = self.get_exam_semester(self.exam_id)
            subject_code = self.get_subject_code(self.exam_id)
            exam_type = self.exam_type
            exam_id = self.exam_id

            end_time = self.get_exam_end_time(self.exam_id, self.user_id)
            submitted_at = end_time.strftime("%B %d, %Y at %I:%M %p") if end_time else "an unknown time"

            message = (
                f"{student_name} just submitted their {exam_type}.\n"
                f"🆔 Student ID: {self.user_id}\n"
                f"📚 Subject: {subject_code} | {semester}\n"
                f"🕒 Submitted on: {submitted_at} | Exam ID: {exam_id}"
            )

            creator_id = self.get_creator(self.exam_id)

            self.notification_manager.send_notification(
                sender_id=self.user_id,
                recipient_role='Faculty',
                recipient_id=creator_id,
                message=message
            )

            self.timer.stop()

            # ✅ Refresh student performance if reference is available
            if hasattr(self, 'student_dashboard') and self.student_dashboard:
                self.student_dashboard.display_student_performance()

            # Show success dialog
            dialog = SubmissionSuccessDialog(self)
            if dialog.exec():
                if hasattr(self, 'current_window') and self.current_window:
                    self.current_window.show()
                self.close()

    def get_unanswered_questions(self):
        """Check for unanswered questions and return a list of them"""
        unanswered = []
        
        for exam_type, questions in self.question_widgets:
            for box in questions:
                question_answered = False
                
                if exam_type == "MULTIPLE CHOICES":
                    # Check if any radio button is selected
                    button_group = box.button_group
                    if button_group.checkedButton() is not None:
                        question_answered = True
                        
                elif exam_type == "TRUE OR FALSE":
                    # Check if any radio button is selected
                    button_group = box.button_group
                    if button_group.checkedButton() is not None:
                        question_answered = True
                        
                elif exam_type == "IDENTIFICATION":
                    # Check if the text field has content
                    answer_input = box.findChild(QLineEdit, f"student_answer_{box.part_num}_{box.question_num}")
                    if answer_input and answer_input.text().strip():
                        question_answered = True
                
                if not question_answered:
                    unanswered.append({
                        'box': box,
                        'type': exam_type,
                        'part': box.part_num,
                        'question': box.question_num
                    })
        
        return unanswered

    def highlight_unanswered_questions(self, unanswered_questions):
        """Highlight unanswered questions by changing their background color"""
        # First, clear any existing highlights
        self.clear_question_highlights()
        
        for item in unanswered_questions:
            box = item['box']
            # Add red border and background to highlight unanswered questions
            box.setStyleSheet("""
                QGroupBox {
                    border: 3px solid #FF0000;
                    border-radius: 8px;
                    margin-top: 10px;
                    background-color: #FFE6E6;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 5px;
                    background-color: #FF0000;
                    color: white;
                    border-radius: 5px;
                }
            """)
            
            # Store the box reference so we can clear highlights later
            if not hasattr(self, 'highlighted_boxes'):
                self.highlighted_boxes = []
            self.highlighted_boxes.append(box)

    def clear_question_highlights(self):
        """Clear highlights from all questions"""
        if hasattr(self, 'highlighted_boxes'):
            for box in self.highlighted_boxes:
                # Reset to normal styling
                box.setStyleSheet("""
                    QGroupBox {
                        border: 2px solid #3373B9;
                        border-radius: 8px;
                        margin-top: 10px;
                        background-color: #F9F9E0;
                        font-weight: bold;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 5px;
                        background-color: #3373B9;
                        color: white;
                        border-radius: 5px;
                    }
                """)
            self.highlighted_boxes = []

    def scroll_to_first_unanswered(self, unanswered_questions):
        """Scroll to the first unanswered question"""
        if unanswered_questions:
            first_unanswered = unanswered_questions[0]['box']
            
            # Get the position of the widget relative to the scroll area
            widget_pos = first_unanswered.pos()
            
            # Scroll to the widget position
            self.scroll_area.ensureWidgetVisible(first_unanswered)
            
            # Optionally, you can also scroll to a specific position
            # self.scroll_area.verticalScrollBar().setValue(widget_pos.y())
            
            print(f"Scrolled to first unanswered question: Part {first_unanswered.part_num}, Question {first_unanswered.question_num}")

    def collect_student_answers(self):
        """Enhanced collect_student_answers method that also clears highlights"""
        # Clear any existing highlights when collecting answers
        self.clear_question_highlights()
        
        answers = {
            "multiple_choice": [],
            "true_false": [],
            "identification": []
        }
        
        print("\n=== COLLECTING STUDENT ANSWERS ===")

        for exam_type, questions in self.question_widgets:
            print(f"Processing {exam_type} questions:")
            
            for box in questions:
                question_data = {
                    "part_num": box.part_num,
                    "question_num": box.question_num,
                    "question": box.input_widgets["question"].toPlainText()
                }
                
                print(f"  Question Part {box.part_num}, Num {box.question_num}: {question_data['question'][:20]}...")

                if exam_type == "MULTIPLE CHOICES":
                    selected_option = None
                    # Use the button group stored directly with the question box:
                    button_group = box.button_group
                    for btn in button_group.buttons():
                        if btn.isChecked():
                            selected_option = btn.text()
                            break
                    question_data["answer"] = selected_option
                    print(f"    Selected option: {selected_option}")
                    answers["multiple_choice"].append(question_data)

                elif exam_type == "TRUE OR FALSE":
                    selected_option = None
                    # Use the button group stored directly with the question box:
                    button_group = box.button_group
                    for btn in button_group.buttons():
                        if btn.isChecked():
                            selected_option = btn.text()
                            break
                    question_data["answer"] = selected_option
                    print(f"    Selected option: {selected_option}")
                    answers["true_false"].append(question_data)

                elif exam_type == "IDENTIFICATION":
                    # No changes needed for identification
                    answer_input = box.findChild(QLineEdit, f"student_answer_{box.part_num}_{box.question_num}")
                    if answer_input:
                        question_data["answer"] = answer_input.text()
                    else:
                        question_data["answer"] = ""
                    print(f"    Text answer: {question_data['answer']}")
                    answers["identification"].append(question_data)

        print(f"Collected answers: {answers}")
        print("=== COLLECTION COMPLETE ===\n")
        return answers


    def populate_questions_with_student_loaded_data(self):
        part_instructions_dict = {}
        
        if "multiple_choice" in self.student_loaded_data and self.student_loaded_data["multiple_choice"]:
            mc_data = self.student_loaded_data["multiple_choice"]
            mc_question_widgets = self.get_question_widgets_by_type_student("MULTIPLE CHOICES")
            
            for question_data in mc_data:
                if "description" in question_data and question_data["description"]:
                    part_index = self.determine_question_part_index_student("MULTIPLE CHOICES", mc_data.index(question_data))
                    if part_index is not None and part_index not in part_instructions_dict:
                        part_instructions_dict[part_index] = question_data["description"]

            for i, question_data in enumerate(mc_data):
                if i < len(mc_question_widgets):
                    widget = mc_question_widgets[i]
                    widget.input_widgets["question"].setText(question_data["question"])
                    
                    widget.input_widgets["answers"]["options"]["A"].setText(question_data["option_a"])
                    widget.input_widgets["answers"]["options"]["B"].setText(question_data["option_b"])
                    widget.input_widgets["answers"]["options"]["C"].setText(question_data["option_c"])
                    widget.input_widgets["answers"]["options"]["D"].setText(question_data["option_d"])
    
                    if self.user_role == "faculty" and "correct" in widget.input_widgets["answers"]:
                        widget.input_widgets["answers"]["correct"].setCurrentText(question_data["correct_answer"])
        
        if "true_false" in self.student_loaded_data and self.student_loaded_data["true_false"]:
            tf_data = self.student_loaded_data["true_false"]
            tf_question_widgets = self.get_question_widgets_by_type_student("TRUE OR FALSE")
            
            for question_data in tf_data:
                if "description" in question_data and question_data["description"]:
                    part_index = self.determine_question_part_index_student("TRUE OR FALSE", tf_data.index(question_data))
                    if part_index is not None and part_index not in part_instructions_dict:
                        part_instructions_dict[part_index] = question_data["description"]
            
            for i, question_data in enumerate(tf_data):
                if i < len(tf_question_widgets):
                    widget = tf_question_widgets[i]
                    widget.input_widgets["question"].setText(question_data["question"])
                    
                    if self.user_role == "faculty" and "correct" in widget.input_widgets["answers"]:
                        widget.input_widgets["answers"]["correct"].setCurrentText(question_data["correct_answer"])
        
        if "identification" in self.student_loaded_data and self.student_loaded_data["identification"]:
            id_data = self.student_loaded_data["identification"]
            id_question_widgets = self.get_question_widgets_by_type_student("IDENTIFICATION")
            
            for question_data in id_data:
                if "description" in question_data and question_data["description"]:
                    part_index = self.determine_question_part_index_student("IDENTIFICATION", id_data.index(question_data))
                    if part_index is not None and part_index not in part_instructions_dict:
                        part_instructions_dict[part_index] = question_data["description"]
            
            for i, question_data in enumerate(id_data):
                if i < len(id_question_widgets):
                    widget = id_question_widgets[i]
                    widget.input_widgets["question"].setText(question_data["question"])
                    
                    if self.user_role == "faculty" and "correct" in widget.input_widgets["answers"]:
                        widget.input_widgets["answers"]["correct"].setText(question_data["correct_answer"])

        for part_index, description in part_instructions_dict.items():
            if part_index < len(self.part_instructions):
                self.part_instructions[part_index].setText(description)

    def determine_question_part_index_student(self, question_type, question_index):
        count = 0
        part_index = 0
        
        for i, (exam_type, num_items) in enumerate(self.exam_parts):
            if exam_type == question_type:
                if count <= question_index < count + num_items:
                    return i  
                count += num_items
            part_index += 1
        
        return None  
    
    def get_question_widgets_by_type_student(self, exam_type):
        widgets = []
        for type_name, questions in self.question_widgets:
            if type_name == exam_type:
                widgets.extend(questions)
        return widgets
   
    def load_exam_data_student(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM multiple_choice_exam WHERE exam_id = %s", (self.exam_id,))
            mc_results = cursor.fetchall()
            for mc in mc_results:
                for exam_type, questions in self.question_widgets:
                    if exam_type == "MULTIPLE CHOICES":
                        for box in questions:
                            if box.part_num == mc['part'] and box.question_num == mc['question_num']:
                                widgets = box.input_widgets
                                widgets['question'].setPlainText(mc['question'])
                                widgets['answers']['options']['A'].setPlainText(mc['option_a'])
                                widgets['answers']['options']['B'].setPlainText(mc['option_b'])
                                widgets['answers']['options']['C'].setPlainText(mc['option_c'])
                                widgets['answers']['options']['D'].setPlainText(mc['option_d'])
          
                                if self.user_role == "faculty" and "correct" in widgets['answers']:
                                    widgets['answers']['correct'].setCurrentText(mc['correct_answer'])

            cursor.execute("SELECT * FROM true_false_exam WHERE exam_id = %s", (self.exam_id,))
            tf_results = cursor.fetchall()
            for tf in tf_results:
                for exam_type, questions in self.question_widgets:
                    if exam_type == "TRUE OR FALSE":
                        for box in questions:
                            if box.part_num == tf['part'] and box.question_num == tf['question_num']:
                                widgets = box.input_widgets
                                widgets['question'].setPlainText(tf['question'])
                                
                                if self.user_role == "faculty" and "correct" in widgets['answers']:
                                    widgets['answers']['correct'].setCurrentText(tf['correct_answer'])

            cursor.execute("SELECT * FROM identification_exam WHERE exam_id = %s", (self.exam_id,))
            id_results = cursor.fetchall()
            for ident in id_results:
                for exam_type, questions in self.question_widgets:
                    if exam_type == "IDENTIFICATION":
                        for box in questions:
                            if box.part_num == ident['part'] and box.question_num == ident['question_num']:
                                widgets = box.input_widgets
                                widgets['question'].setPlainText(ident['question'])
                                
                                if self.user_role == "faculty" and "correct" in widgets['answers']:
                                    widgets['answers']['correct'].setText(ident['correct_answer'])

            all_parts = mc_results + tf_results + id_results
            for part_index, instruction_box in enumerate(self.part_instructions):
                for row in all_parts:
                    if row["part"] == part_index + 1:
                        instruction_box.setText(row["description"])
                        break

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load exam data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def collect_student_answers(self):
        answers = {
            "multiple_choice": [],
            "true_false": [],
            "identification": []
        }
        
        print("\n=== COLLECTING STUDENT ANSWERS ===")

        for exam_type, questions in self.question_widgets:
            print(f"Processing {exam_type} questions:")
            
            for box in questions:
                question_data = {
                    "part_num": box.part_num,
                    "question_num": box.question_num,
                    "question": box.input_widgets["question"].toPlainText()
                }
                
                print(f"  Question Part {box.part_num}, Num {box.question_num}: {question_data['question'][:20]}...")

                if exam_type == "MULTIPLE CHOICES":
                    selected_option = None
                    # Use the button group stored directly with the question box:
                    button_group = box.button_group
                    for btn in button_group.buttons():
                        if btn.isChecked():
                            selected_option = btn.text()
                            break
                    question_data["answer"] = selected_option
                    print(f"    Selected option: {selected_option}")
                    answers["multiple_choice"].append(question_data)

                elif exam_type == "TRUE OR FALSE":
                    selected_option = None
                    # Use the button group stored directly with the question box:
                    button_group = box.button_group
                    for btn in button_group.buttons():
                        if btn.isChecked():
                            selected_option = btn.text()
                            break
                    question_data["answer"] = selected_option
                    print(f"    Selected option: {selected_option}")
                    answers["true_false"].append(question_data)

                elif exam_type == "IDENTIFICATION":
                    # No changes needed for identification
                    answer_input = box.findChild(QLineEdit, f"student_answer_{box.part_num}_{box.question_num}")
                    if answer_input:
                        question_data["answer"] = answer_input.text()
                    else:
                        question_data["answer"] = ""
                    print(f"    Text answer: {question_data['answer']}")
                    answers["identification"].append(question_data)

        print(f"Collected answers: {answers}")
        print("=== COLLECTION COMPLETE ===\n")
        return answers
        
    def save_student_answers_to_db(self, answers):
        connection = None
        cursor = None
        correct_answers = 0
        total_questions = 0

        print("\n=== STARTING ANSWER SUBMISSION PROCESS ===")
        print(f"User ID: {self.user_id}, Exam ID: {self.exam_id}")
        print(f"Answer data received: {answers}")

        try:
            print("Attempting database connection...")
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(buffered=True)
            connection.start_transaction()
            print("Database connection successful, transaction started")

            # Prevent duplicate submissions
            print("Checking for duplicate submissions...")
            cursor.execute(
                "SELECT * FROM student_answers WHERE student_id = %s AND exam_id = %s",
                (self.user_id, self.exam_id)
            )
            if cursor.fetchone():
                print("DUPLICATE SUBMISSION DETECTED!")
                QMessageBox.warning(self, "Already Submitted", "You have already submitted this exam.")
                return False, correct_answers, total_questions
            print("No duplicate submission found, continuing...")

            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"End time set to: {end_time}")

            # Handle true/false questions
            if answers["true_false"]:
                print(f"\nProcessing TRUE/FALSE questions: {len(answers['true_false'])} answers to save")
                # Get all true/false questions for this exam
                cursor.execute("SELECT id, part, question_num, question, correct_answer FROM true_false_exam WHERE exam_id = %s", (self.exam_id,))
                db_questions = cursor.fetchall()
                print(f"Retrieved {len(db_questions)} true/false questions from database")
                
                # Create a dictionary to easily look up questions by part and question number
                db_questions_dict = {(q[1], q[2]): (q[0], q[4]) for q in db_questions}
                print(f"Question dictionary created: {db_questions_dict}")
                
                # Process each student answer
                for answer in answers["true_false"]:
                    part_num = answer["part_num"]
                    question_num = answer["question_num"]
                    print(f"  Processing TF answer for part {part_num}, question {question_num}")
                    
                    # Find the matching question in our dictionary
                    if (part_num, question_num) in db_questions_dict:
                        question_id, correct_answer = db_questions_dict[(part_num, question_num)]
                        print(f"    Found matching question ID: {question_id}, correct answer: {correct_answer}")
                        
                        # Extract student's selected answer
                        student_answer = answer["answer"] if answer["answer"] else ""
                        print(f"    Student answer: '{student_answer}'")
                        
                        # Compare the student's answer with the correct answer
                        is_correct = int(student_answer.strip() == correct_answer.strip())
                        correct_answers += is_correct
                        total_questions += 1
                        print(f"    Is correct: {is_correct}, Running total: {correct_answers}/{total_questions}")
                        
                        query = """INSERT INTO student_answers 
                            (exam_id, student_id, major_exam_type, start_time, end_time, answer, question_id, is_correct, status) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Completed')"""
                        params = (
                            self.exam_id,
                            self.user_id,
                            self.exam_type,
                            self.start_time,
                            end_time,
                            student_answer,
                            question_id,
                            is_correct
                        )
                        print(f"    Executing query: {query}")
                        print(f"    With parameters: {params}")
                        cursor.execute(query, params)
                        print("    Query executed successfully")
                    else:
                        print(f"    WARNING: No matching question found for part {part_num}, question {question_num}")

            # Handle multiple choice questions - use same approach as above
            if answers["multiple_choice"]:
                print(f"\nProcessing MULTIPLE CHOICE questions: {len(answers['multiple_choice'])} answers to save")
                cursor.execute("SELECT id, part, question_num, question, correct_answer FROM multiple_choice_exam WHERE exam_id = %s", (self.exam_id,))
                db_questions = cursor.fetchall()
                print(f"Retrieved {len(db_questions)} multiple choice questions from database")
                
                db_questions_dict = {(q[1], q[2]): (q[0], q[4]) for q in db_questions}
                print(f"Question dictionary created: {db_questions_dict}")
                
                for answer in answers["multiple_choice"]:
                    part_num = answer["part_num"]
                    question_num = answer["question_num"]
                    print(f"  Processing MC answer for part {part_num}, question {question_num}")
                    
                    if (part_num, question_num) in db_questions_dict:
                        question_id, correct_answer = db_questions_dict[(part_num, question_num)]
                        print(f"    Found matching question ID: {question_id}, correct answer: {correct_answer}")
                        
                        student_answer = answer["answer"] if answer["answer"] else ""
                        print(f"    Student answer: '{student_answer}'")
                        
                        is_correct = int(student_answer.strip() == correct_answer.strip())
                        correct_answers += is_correct
                        total_questions += 1
                        print(f"    Is correct: {is_correct}, Running total: {correct_answers}/{total_questions}")
                        
                        query = """INSERT INTO student_answers 
                            (exam_id, student_id, major_exam_type, start_time, end_time, answer, question_id, is_correct, status) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Completed')"""
                        params = (
                            self.exam_id,
                            self.user_id,
                            self.exam_type,
                            self.start_time,
                            end_time,
                            student_answer,
                            question_id,
                            is_correct
                        )
                        print(f"    Executing query: {query}")
                        print(f"    With parameters: {params}")
                        cursor.execute(query, params)
                        print("    Query executed successfully")
                    else:
                        print(f"    WARNING: No matching question found for part {part_num}, question {question_num}")

            # Handle identification questions - same approach
            if answers["identification"]:
                print(f"\nProcessing IDENTIFICATION questions: {len(answers['identification'])} answers to save")
                cursor.execute("SELECT id, part, question_num, question, correct_answer FROM identification_exam WHERE exam_id = %s", (self.exam_id,))
                db_questions = cursor.fetchall()
                print(f"Retrieved {len(db_questions)} identification questions from database")
                
                db_questions_dict = {(q[1], q[2]): (q[0], q[4]) for q in db_questions}
                print(f"Question dictionary created: {db_questions_dict}")
                
                for answer in answers["identification"]:
                    part_num = answer["part_num"]
                    question_num = answer["question_num"]
                    print(f"  Processing ID answer for part {part_num}, question {question_num}")
                    
                    if (part_num, question_num) in db_questions_dict:
                        question_id, correct_answer = db_questions_dict[(part_num, question_num)]
                        print(f"    Found matching question ID: {question_id}, correct answer: {correct_answer}")
                        
                        student_answer = answer["answer"] if answer["answer"] else ""
                        print(f"    Student answer: '{student_answer}'")
                        
                        is_correct = int(student_answer.strip().lower() == correct_answer.strip().lower())
                        correct_answers += is_correct
                        total_questions += 1
                        print(f"    Is correct: {is_correct}, Running total: {correct_answers}/{total_questions}")
                        
                        query = """INSERT INTO student_answers 
                            (exam_id, student_id, major_exam_type, start_time, end_time, answer, question_id, is_correct, status) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Completed')"""
                        params = (
                            self.exam_id,
                            self.user_id,
                            self.exam_type,
                            self.start_time,
                            end_time,
                            student_answer,
                            question_id,
                            is_correct
                        )
                        print(f"    Executing query: {query}")
                        print(f"    With parameters: {params}")
                        cursor.execute(query, params)
                        print("    Query executed successfully")
                    else:
                        print(f"    WARNING: No matching question found for part {part_num}, question {question_num}")

            print("\nUpdating performance data...")
            # Get subject_code and exam_part to update performance
            cursor.execute(
                "SELECT subject_code, exam_part FROM examination_form WHERE exam_id = %s LIMIT 1",
                (self.exam_id,)
            )
            result = cursor.fetchone()
            if not result:
                print("ERROR: Exam metadata not found!")
                raise Exception("Exam metadata not found.")
            subject_code, exam_part = result
            print(f"Retrieved subject code: {subject_code}, exam part: {exam_part}")

            # Check if performance record exists
            cursor.execute(
                "SELECT id FROM student_performance WHERE student_id = %s AND subject_code = %s",
                (self.user_id, subject_code)
            )
            existing = cursor.fetchone()
            print(f"Existing performance record found: {existing is not None}")

            if existing:
                if exam_part == "Prelim":
                    print(f"Updating prelim score to {correct_answers}")
                    cursor.execute(
                        "UPDATE student_performance SET prelim_score = %s WHERE student_id = %s AND subject_code = %s",
                        (correct_answers, self.user_id, subject_code)
                    )
                elif exam_part == "Midterm":
                    print(f"Updating midterm score to {correct_answers}")
                    cursor.execute(
                        "UPDATE student_performance SET midterm_score = %s WHERE student_id = %s AND subject_code = %s",
                        (correct_answers, self.user_id, subject_code)
                    )
                elif exam_part == "Finals":
                    print(f"Updating finals score to {correct_answers}")
                    cursor.execute(
                        "UPDATE student_performance SET finals_score = %s WHERE student_id = %s AND subject_code = %s",
                        (correct_answers, self.user_id, subject_code)
                    )
            else:
                prelim = correct_answers if exam_part == "Prelim" else None
                midterm = correct_answers if exam_part == "Midterm" else None
                finals = correct_answers if exam_part == "Finals" else None
                print(f"Creating new performance record with prelim={prelim}, midterm={midterm}, finals={finals}")

                cursor.execute(
                    """INSERT INTO student_performance 
                    (student_id, subject_code, prelim_score, midterm_score, finals_score) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (self.user_id, subject_code, prelim, midterm, finals)
                )

            print("Committing transaction...")
            connection.commit()
            print("Transaction committed successfully!")
            return True, correct_answers, total_questions

        except mysql.connector.Error as e:
            print(f"DATABASE ERROR: {e}")
            if connection:
                print("Rolling back transaction...")
                connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to save exam: {e}")
            return False, correct_answers, total_questions
        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}")
            if connection:
                print("Rolling back transaction...")
                connection.rollback()
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return False, correct_answers, total_questions
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
            print("Database connection closed")
            print("=== SUBMISSION PROCESS COMPLETED ===\n")

    def update_student_performance(self, correct_answers, total_questions):
        raw_score = correct_answers if total_questions > 0 else 0

        cursor = None
        connection = None
        try:
            import mysql.connector
            from PySide6.QtWidgets import QMessageBox

            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(buffered=True)

            cursor.execute("SELECT subject_code, exam_part FROM examination_form WHERE exam_id = %s", (self.exam_id,))
            result = cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Missing Info", "Cannot find subject or exam part.")
                return
            subject_code, exam_part = result

            cursor.execute(
                "SELECT id FROM student_performance WHERE student_id = %s AND subject_code = %s",
                (self.user_id, subject_code)
            )
            existing = cursor.fetchone()

            if existing:
                if exam_part == "Prelim":
                    cursor.execute(
                        "UPDATE student_performance SET prelim_score = %s WHERE student_id = %s AND subject_code = %s",
                        (raw_score, self.user_id, subject_code)
                    )
                elif exam_part == "Midterm":
                    cursor.execute(
                        "UPDATE student_performance SET midterm_score = %s WHERE student_id = %s AND subject_code = %s",
                        (raw_score, self.user_id, subject_code)
                    )
                elif exam_part == "Finals":
                    cursor.execute(
                        "UPDATE student_performance SET finals_score = %s WHERE student_id = %s AND subject_code = %s",
                        (raw_score, self.user_id, subject_code)
                    )
            else:
                prelim = raw_score if exam_part == "Prelim" else None
                midterm = raw_score if exam_part == "Midterm" else None
                finals = raw_score if exam_part == "Finals" else None

                cursor.execute(
                    """INSERT INTO student_performance 
                    (student_id, subject_code, prelim_score, midterm_score, finals_score) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (self.user_id, subject_code, prelim, midterm, finals)
                )

            connection.commit()

        except mysql.connector.Error as e:
            if connection:
                connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to update performance: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()


    def get_student_full_name(self, user_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT first_name, middle_name, last_name, suffix 
                FROM user_account 
                WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()
            if user:
                fullname = f"{user['first_name']} "
                if user['middle_name']:
                    fullname += f"{user['middle_name'][0]}. "
                fullname += f"{user['last_name']}"
                if user['suffix']:
                    fullname += f", {user['suffix']}"
                return fullname
            else:
                return "Unknown Student"
        except Exception as e:
            print(f"Error: {e}")
            return "Unknown Student"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def get_exam_semester(self, exam_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            query = "SELECT semester FROM examination_form WHERE exam_id = %s LIMIT 1"
            cursor.execute(query, (exam_id,))
            result = cursor.fetchone()
            return result['semester'] if result else "Unknown Semester"
        except Exception as e:
            print(f"Error: {e}")
            return "Unknown Semester"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_subject_code(self, exam_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            query = "SELECT subject_code FROM examination_form WHERE exam_id = %s LIMIT 1"
            cursor.execute(query, (exam_id,))
            result = cursor.fetchone()
            return result['subject_code'] if result else "Unknown Subject"
        except Exception as e:
            print(f"Error: {e}")
            return "Unknown Subject"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_exam_end_time(self, exam_id, student_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            query = "SELECT end_time FROM student_answers WHERE exam_id = %s AND student_id = %s ORDER BY end_time DESC LIMIT 1"
            cursor.execute(query, (exam_id, student_id))
            result = cursor.fetchone()
            return result['end_time'] if result else None
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()



    def populate_exam_questions(self, exam_parts):
        self.part_instructions = []  
        part_count = 1
        
        for part_index, (exam_type, num_items) in enumerate(exam_parts, start=1):
            part_label = QLabel(f"Part {part_index}: {exam_type}")
            part_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.container_layout.addWidget(part_label)

            instruction_text = "Enter your instructions..."
            instruction_box = AutoResizeTextEdit(instruction_text)
            instruction_box.setFixedHeight(50)
            instruction_box.setObjectName(f"instruction_part_{part_index}")
            
            if self.user_role == "student":
                instruction_box.setReadOnly(True)
                instruction_box.setFocusPolicy(Qt.NoFocus)
                instruction_box.setStyleSheet("""
                    QTextEdit {
                        background-color: #f5f5f5;
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QTextEdit:focus {
                        border: 1px solid #cccccc;
                    }
                """)
                
            self.part_instructions.append(instruction_box)
            self.container_layout.addWidget(instruction_box)

            part_questions = [] 
            for i in range(1, num_items + 1):
                question_widget = self.create_question_widget(i, exam_type, part_count)
                part_questions.append(question_widget)
                self.container_layout.addWidget(question_widget)
            
            self.question_widgets.append((exam_type, part_questions))
            part_count += 1

        self.container.setLayout(self.container_layout)

    def create_question_widget(self, q_num, exam_type, part_num):
        question_box = QGroupBox(f"Question {q_num}")
        question_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3373B9;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #F9F9E0;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
                background-color: #3373B9;
                color: white;
                border-radius: 5px;
            }
        """)
        question_layout = QVBoxLayout()

        question_input = AutoResizeTextEdit(f"Enter Question {q_num}...")
        question_input.setObjectName(f"question_{part_num}_{q_num}")
        
        if self.user_role == "student":
            question_input.setReadOnly(True)
            question_input.setFocusPolicy(Qt.NoFocus)
            question_input.setStyleSheet("""
                QTextEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 5px;
                }
                QTextEdit:focus {
                    border: 1px solid #cccccc;
                }
            """)
        
        question_layout.addWidget(question_input)

        answer_widgets = {}  

        if exam_type == "MULTIPLE CHOICES":
            options_layout = QVBoxLayout()
            button_group = QButtonGroup(self)
            # Instead of appending to self.button_groups:
            question_box.button_group = button_group  

            option_inputs = {}
            for opt in ["A", "B", "C", "D"]:
                opt_layout = QHBoxLayout()
                
                radio_button = QRadioButton(opt)
                radio_button.setStyleSheet("background-color: transparent;")
                radio_button.setObjectName(f"option_{part_num}_{q_num}_{opt}")
                radio_button.setEnabled(self.user_role == "student")
                
                if self.user_role == "student":
                    radio_button.setCursor(Qt.PointingHandCursor)
                
                button_group.addButton(radio_button)
                
                answer_input = AutoResizeTextEdit(f"Choice {opt}")
                answer_input.setObjectName(f"choice_{part_num}_{q_num}_{opt}")

                if self.user_role == "student":
                    answer_input.setReadOnly(True)
                    answer_input.setFocusPolicy(Qt.NoFocus)
                    answer_input.setStyleSheet("""
                        QTextEdit {
                            background-color: #f5f5f5;
                            border: 1px solid #cccccc;
                            border-radius: 5px;
                            padding: 5px;
                        }
                        QTextEdit:focus {
                            border: 1px solid #cccccc;
                        }
                    """)
                
                option_inputs[opt] = answer_input
                opt_layout.addWidget(radio_button)
                opt_layout.addWidget(answer_input)
                options_layout.addLayout(opt_layout)

            answer_widgets["options"] = option_inputs
            question_layout.addLayout(options_layout)
            
            if self.user_role == "faculty":
                correct_layout = self.create_correct_answer_section(["A", "B", "C", "D"])
                answer_widgets["correct"] = correct_layout.itemAt(1).itemAt(0).widget()  
                question_layout.addLayout(correct_layout)
        
        elif exam_type == "TRUE OR FALSE":
            tf_layout = QHBoxLayout()
            button_group = QButtonGroup(self)
            # Instead of appending to self.button_groups:
            question_box.button_group = button_group 

            true_btn = QRadioButton("True")
            true_btn.setObjectName(f"true_btn_{part_num}_{q_num}")
            
            false_btn = QRadioButton("False")
            false_btn.setObjectName(f"false_btn_{part_num}_{q_num}")

            true_btn.setEnabled(self.user_role == "student")
            false_btn.setEnabled(self.user_role == "student")
            
            if self.user_role == "student":
                true_btn.setCursor(Qt.PointingHandCursor)
                false_btn.setCursor(Qt.PointingHandCursor)

            button_group.addButton(true_btn)
            button_group.addButton(false_btn)

            tf_layout.addWidget(true_btn)
            tf_layout.addWidget(false_btn)
            question_layout.addLayout(tf_layout)
            
            if self.user_role == "faculty":
                correct_layout = self.create_correct_answer_section(["True", "False"])
                answer_widgets["correct"] = correct_layout.itemAt(1).itemAt(0).widget() 
                question_layout.addLayout(correct_layout)

        elif exam_type == "IDENTIFICATION":
            student_answer_input = QLineEdit()
            student_answer_input.setObjectName(f"student_answer_{part_num}_{q_num}")
            student_answer_input.setPlaceholderText("Enter your answer here...")
            
            if self.user_role == "student":
                student_answer_input.setEnabled(True)
                student_answer_input.setReadOnly(False)
                student_answer_input.setCursor(Qt.IBeamCursor)
                student_answer_input.setStyleSheet("""
                    QLineEdit {
                        background-color: #ffffff;
                        border: 2px solid #cccccc;
                        border-radius: 8px;
                        padding: 6px;
                        font-size: 14px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #3373B9;
                    }
                """)
            else:
                student_answer_input.setEnabled(False)
                student_answer_input.setStyleSheet(
                    "border: 2px solid #ccc; border-radius: 8px; padding: 6px; font-size: 14px; background-color: #f0f0f0;"
                )

            question_layout.addWidget(student_answer_input)

            if self.user_role == "faculty":
                correct_layout = self.create_correct_answer_section(is_text=True)
                answer_widgets["correct"] = correct_layout.itemAt(1).itemAt(0).widget()  
                question_layout.addLayout(correct_layout)

        question_box.setLayout(question_layout)
        question_box.exam_type = exam_type
        question_box.question_num = q_num
        question_box.part_num = part_num
        question_box.input_widgets = {
            "question": question_input,
            "answers": answer_widgets
        }
        return question_box

    def create_correct_answer_section(self, options=None, is_text=False):
        correct_answer_layout = QVBoxLayout()
        correct_answer_label = QLabel("Correct Answer:")
        correct_answer_label.setStyleSheet("font-size: 15px; font-weight: bold; background-color: transparent;")
        correct_answer_layout.addWidget(correct_answer_label)

        answer_layout = QHBoxLayout()
        if is_text:
            correct_answer_input = QLineEdit()
            correct_answer_input.setPlaceholderText("Enter correct answer...")
            correct_answer_input.setStyleSheet("border: 2px solid #ccc; border-radius: 8px; padding: 6px; font-size: 14px;")
            answer_layout.addWidget(correct_answer_input)
        else:
            correct_answer_combo = QComboBox()
            correct_answer_combo.addItems(options)
            correct_answer_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    border: 1px solid #B8D5E7;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 15px;
                    color: #215988;
                    font-weight: bold;
                    selection-background-color: #FF5929;
                    transition: border-color 0.3s ease, box-shadow 0.3s ease;
                }
                QComboBox:focus {
                    border: 1px solid #00cc00;
                    box-shadow: 0px 0px 5px rgba(255, 89, 41, 0.3);
                    background-color: white;
                }
                QComboBox QAbstractItemView {
                    background: white;
                    border: 1px solid #B8D5E7;
                    selection-background-color: #00cc00;
                    color: #215988;
                }
            """)
            correct_answer_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            answer_layout.addWidget(correct_answer_combo)

        answer_layout.addStretch()
        correct_answer_layout.addLayout(answer_layout)
        return correct_answer_layout


    def collect_exam_data(self):
        exam_data = {
            "multiple_choice": [],
            "true_false": [],
            "identification": []
        }
        
        for part_index, (exam_type, questions) in enumerate(self.question_widgets):
            instruction = self.part_instructions[part_index].toPlainText()
            
            for question_box in questions:
                widgets = question_box.input_widgets
                question_text = widgets["question"].toPlainText()
                question_num = question_box.question_num
                part_num = question_box.part_num
                
                if exam_type == "MULTIPLE CHOICES":
                    options = {
                        'A': widgets["answers"]["options"]["A"].toPlainText(),
                        'B': widgets["answers"]["options"]["B"].toPlainText(),
                        'C': widgets["answers"]["options"]["C"].toPlainText(),
                        'D': widgets["answers"]["options"]["D"].toPlainText()
                    }
                    correct_answer = widgets["answers"]["correct"].currentText()
                    
                    exam_data["multiple_choice"].append({
                        "part": part_num,
                        "question_num": question_num,
                        "description": instruction,
                        "question": question_text,
                        "option_a": options['A'],
                        "option_b": options['B'],
                        "option_c": options['C'],
                        "option_d": options['D'],
                        "correct_answer": correct_answer
                    })
                    
                elif exam_type == "TRUE OR FALSE":
                    correct_answer = widgets["answers"]["correct"].currentText()
                    
                    exam_data["true_false"].append({
                        "part": part_num,
                        "question_num": question_num,
                        "description": instruction,
                        "question": question_text,
                        "correct_answer": correct_answer
                    })
                    
                elif exam_type == "IDENTIFICATION":
                    correct_answer = widgets["answers"]["correct"].text()
                    
                    exam_data["identification"].append({
                        "part": part_num,
                        "question_num": question_num,
                        "description": instruction,
                        "question": question_text,
                        "correct_answer": correct_answer
                    })
        
        return exam_data
    
    def show_student_dashboard(self):
        if self.current_window:
            self.current_window.show()

        self.close()


class AutoResizeTextEdit(QTextEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 2px solid #00cc00;
                outline: none;
            }
        """)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
        self.textChanged.connect(self.adjustHeight)  
        self.setFixedHeight(40) 

    def adjustHeight(self):
        doc_height = int(self.document().size().height()) + 10  
        self.setFixedHeight(min(max(40, doc_height), 150)) 

class ExamResult(QMainWindow):
    def __init__(self, exam_id, student_id, parent=None):
        super().__init__(parent)
        self.exam_id = exam_id
        self.student_id = student_id
        self.user_role = "student"  # Always view as student
        
        # Initialize UI
        self.setWindowTitle("Exam Response Details")
        
        # Load the UI template
        loader = QUiLoader()
        self.exam_template = loader.load(resource_path("UI/exam_template.ui"), self)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.exam_template)
        self.setCentralWidget(self.stacked_widget)
        self.showMaximized()
        
        # Set up icons
        Icons(self.exam_template)
        
        # Get UI components
        self.exam_template_stacked = self.exam_template.findChild(QStackedWidget, "exam_template_stackedWidget")
        self.major_type = self.exam_template.findChild(QLabel, "major_type")
        self.date_taken = self.exam_template.findChild(QLabel, "date_taken")
        self.time_limit = self.exam_template.findChild(QLabel, "time_limit")
        self.scroll_area = self.exam_template.findChild(QScrollArea, "scrollArea")
        self.title = self.exam_template.findChild(QLabel, "title")
        self.publish = self.exam_template.findChild(QPushButton, "publish")
        self.save_draft = self.exam_template.findChild(QPushButton, "save_draft")
        self.backbtn = self.exam_template.findChild(QPushButton, "back")
        
        # Set up container for exam content
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        
        self.publish.hide()  
        self.save_draft.hide()  
        self.backbtn.setText("")
        self.backbtn.clicked.connect(self.close)
        
        # Collections for button groups and question widgets
        self.button_groups = []
        self.question_widgets = []
        self.part_instructions = []
        
        # Load exam data and student responses
        self.load_exam_details()
        self.load_exam_content()
        self.load_student_responses()
        
        # Set scrolling area
        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True)
    
    def load_exam_details(self):
        """Load basic exam information such as title, type, and time limit."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            
            # Get exam details
            cursor.execute("""
                SELECT e.major_exam_type, e.time_limit, e.subject_code, e.semester, e.exam_id,
                    (SELECT end_time FROM student_answers WHERE exam_id = e.exam_id AND student_id = %s LIMIT 1) as date_taken,
                    (SELECT COUNT(*) FROM student_answers WHERE exam_id = e.exam_id AND student_id = %s) as total_questions,
                    (SELECT SUM(is_correct) FROM student_answers WHERE exam_id = e.exam_id AND student_id = %s) as correct_answers,
                    (SELECT first_name FROM user_account WHERE user_id = %s) as first_name,
                    (SELECT last_name FROM user_account WHERE user_id = %s) as last_name
                FROM examination_form e
                WHERE e.exam_id = %s
            """, (
                self.student_id, self.student_id, self.student_id,
                self.student_id, self.student_id,
                self.exam_id
            ))
            
            exam_details = cursor.fetchone()
            
            if exam_details:
                self.major_type.setText(exam_details['major_exam_type'])
                
                # Show time limit as before
                full_name = f"{exam_details['first_name']} {exam_details['last_name']}".strip()
                self.time_limit.setText(f"Name: {full_name}")
                
                # Change submitted date to score display
                total = exam_details['total_questions'] or 0
                correct = exam_details['correct_answers'] or 0
                self.date_taken.setText(f"Score: {correct}/{total}")
                
                self.title.setText(f"{exam_details['subject_code']} - {exam_details['semester']}")
                
            else:
                # Debug message if no exam details found
                print(f"No exam details found for exam_id: {self.exam_id}")
            
        except mysql.connector.Error as e:
            print(f"Database error in load_exam_details: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load exam details: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def load_exam_content(self):
        """Load the exam questions and structure."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            
            # Debug message
            print(f"Loading exam content for exam_id: {self.exam_id}")
            
            # Get the structure of the exam
            exam_parts = []
            
            # Get multiple choice questions
            cursor.execute("""
                SELECT 
                    COALESCE(part, 1) as part, 
                    COUNT(*) as count, 
                    COALESCE(description, '') as description
                FROM multiple_choice_exam
                WHERE exam_id = %s
                GROUP BY part, description
                ORDER BY part
            """, (self.exam_id,))
            mc_parts = cursor.fetchall()
            for part in mc_parts:
                exam_parts.append(("MULTIPLE CHOICES", part['count'], part['description'], part['part']))
                print(f"Found {part['count']} multiple choice questions in part {part['part']}")
            
            # Get true/false questions
            cursor.execute("""
                SELECT 
                    COALESCE(part, 1) as part, 
                    COUNT(*) as count, 
                    COALESCE(description, '') as description
                FROM true_false_exam
                WHERE exam_id = %s
                GROUP BY part, description
                ORDER BY part
            """, (self.exam_id,))
            tf_parts = cursor.fetchall()
            for part in tf_parts:
                exam_parts.append(("TRUE OR FALSE", part['count'], part['description'], part['part']))
                print(f"Found {part['count']} true/false questions in part {part['part']}")
            
            # Get identification questions
            cursor.execute("""
                SELECT 
                    COALESCE(part, 1) as part, 
                    COUNT(*) as count, 
                    COALESCE(description, '') as description
                FROM identification_exam
                WHERE exam_id = %s
                GROUP BY part, description
                ORDER BY part
            """, (self.exam_id,))
            id_parts = cursor.fetchall()
            for part in id_parts:
                exam_parts.append(("IDENTIFICATION", part['count'], part['description'], part['part']))
                print(f"Found {part['count']} identification questions in part {part['part']}")
            
            # Load the exam structure
            self.populate_exam_questions(exam_parts)
            
            # Load the actual questions for each type and store them with their IDs
            
            # Multiple choice questions
            cursor.execute("""
                SELECT 
                    id,
                    COALESCE(part, 1) as part, 
                    COALESCE(question_num, 1) as question_num,
                    question, 
                    option_a, 
                    option_b, 
                    option_c, 
                    option_d, 
                    correct_answer
                FROM multiple_choice_exam
                WHERE exam_id = %s
                ORDER BY part, question_num
            """, (self.exam_id,))
            mc_questions = cursor.fetchall()
            
            # Dictionary to track questions by part and position
            mc_question_index = {}
            for part_num in set(q['part'] for q in mc_questions):
                mc_question_index[part_num] = 0
                
            for question in mc_questions:
                part_num = question['part']
                
                # Find the appropriate section in question_widgets
                for i, (exam_type, questions, _, widget_part) in enumerate(self.question_widgets):
                    if exam_type == "MULTIPLE CHOICES" and widget_part == part_num:
                        # Get the next available question box for this part
                        if mc_question_index[part_num] < len(questions):
                            box = questions[mc_question_index[part_num]]
                            
                            # Set question and options
                            box.input_widgets['question'].setPlainText(question['question'])
                            
                            # Make sure the options text is set correctly 
                            if 'options' in box.input_widgets['answers']:
                                box.input_widgets['answers']['options']['A'].setPlainText(question['option_a'])
                                box.input_widgets['answers']['options']['B'].setPlainText(question['option_b'])
                                box.input_widgets['answers']['options']['C'].setPlainText(question['option_c'])
                                box.input_widgets['answers']['options']['D'].setPlainText(question['option_d'])
                            
                            box.correct_answer = question['correct_answer']
                            box.question_id = question['id']
                            
                            # Increment the index for this part
                            mc_question_index[part_num] += 1
                            break
            
            # True/False questions
            cursor.execute("""
                SELECT 
                    id,
                    COALESCE(part, 1) as part, 
                    COALESCE(question_num, 1) as question_num,
                    question,
                    correct_answer
                FROM true_false_exam
                WHERE exam_id = %s
                ORDER BY part, question_num
            """, (self.exam_id,))
            tf_questions = cursor.fetchall()
            
            # Dictionary to track questions by part and position
            tf_question_index = {}
            for part_num in set(q['part'] for q in tf_questions):
                tf_question_index[part_num] = 0
                
            for question in tf_questions:
                part_num = question['part']
                
                # Find the appropriate section in question_widgets
                for i, (exam_type, questions, _, widget_part) in enumerate(self.question_widgets):
                    if exam_type == "TRUE OR FALSE" and widget_part == part_num:
                        # Get the next available question box for this part
                        if tf_question_index[part_num] < len(questions):
                            box = questions[tf_question_index[part_num]]
                            
                            box.input_widgets['question'].setPlainText(question['question'])
                            box.correct_answer = question['correct_answer']
                            box.question_id = question['id']
                            
                            # Increment the index for this part
                            tf_question_index[part_num] += 1
                            break
            
            # Identification questions
            cursor.execute("""
                SELECT 
                    id,
                    COALESCE(part, 1) as part, 
                    COALESCE(question_num, 1) as question_num,
                    question,
                    correct_answer
                FROM identification_exam
                WHERE exam_id = %s
                ORDER BY part, question_num
            """, (self.exam_id,))
            id_questions = cursor.fetchall()
            
            # Dictionary to track questions by part and position
            id_question_index = {}
            for part_num in set(q['part'] for q in id_questions):
                id_question_index[part_num] = 0
                
            for question in id_questions:
                part_num = question['part']
                
                # Find the appropriate section in question_widgets
                for i, (exam_type, questions, _, widget_part) in enumerate(self.question_widgets):
                    if exam_type == "IDENTIFICATION" and widget_part == part_num:
                        # Get the next available question box for this part
                        if id_question_index[part_num] < len(questions):
                            box = questions[id_question_index[part_num]]
                            
                            box.input_widgets['question'].setPlainText(question['question'])
                            box.correct_answer = question['correct_answer']
                            box.question_id = question['id']
                            
                            # Increment the index for this part
                            id_question_index[part_num] += 1
                            break
            
            # Set part instructions
            for part_index, (exam_type, questions, description, _) in enumerate(self.question_widgets):
                if part_index < len(self.part_instructions):
                    self.part_instructions[part_index].setPlainText(description)
            
        except mysql.connector.Error as e:
            print(f"Database error in load_exam_content: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load exam content: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def load_student_responses(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            
            # Debug message
            print(f"Loading student responses for student_id: {self.student_id}, exam_id: {self.exam_id}")
            
            # Get student answers for this exam with all necessary details
            cursor.execute("""
                SELECT 
                    sa.answer, 
                    sa.is_correct, 
                    sa.question_id,
                    CASE 
                        WHEN mc.id IS NOT NULL THEN 'multiple_choice'
                        WHEN tf.id IS NOT NULL THEN 'true_false'
                        WHEN id.id IS NOT NULL THEN 'identification'
                    END as question_type,
                    COALESCE(mc.correct_answer, tf.correct_answer, id.correct_answer) as correct_answer,
                    COALESCE(mc.part, tf.part, id.part) as part_num,
                    COALESCE(mc.question_num, tf.question_num, id.question_num) as question_num
                FROM student_answers sa
                LEFT JOIN multiple_choice_exam mc ON sa.question_id = mc.id
                LEFT JOIN true_false_exam tf ON sa.question_id = tf.id
                LEFT JOIN identification_exam id ON sa.question_id = id.id
                WHERE sa.exam_id = %s AND sa.student_id = %s
            """, (self.exam_id, self.student_id))
            
            student_answers = cursor.fetchall()
            print(f"Found {len(student_answers)} student answers")
            
            # Create a mapping of question_id to question box
            question_box_map = {}
            for exam_type, questions, _, _ in self.question_widgets:
                for box in questions:
                    if hasattr(box, 'question_id') and box.question_id is not None:
                        question_box_map[box.question_id] = (box, exam_type)
            
            for answer in student_answers:
                question_id = answer['question_id']
                question_type = answer['question_type']
                student_answer = answer['answer']
                is_correct = answer['is_correct'] == 1  # Ensure boolean comparison
                correct_answer = answer['correct_answer']
                part_num = answer['part_num']
                question_num = answer['question_num']
                
                print(f"Processing answer: Type={question_type}, Q#{question_num}, Answer={student_answer}, Correct={is_correct}")
                
                # Find the corresponding question box using the question_id
                if question_id in question_box_map:
                    box, exam_type = question_box_map[question_id]
                    
                    # Apply border to the entire question box based on correctness
                    border_color = "green" if is_correct else "red"
                    box.setStyleSheet(f"""
                        QGroupBox {{
                            border: 2px solid {border_color};
                            border-radius: 8px;
                            margin-top: 10px;
                            background-color: #F9F9E0;
                            font-weight: bold;
                        }}
                        QGroupBox::title {{
                            subcontrol-origin: margin;
                            subcontrol-position: top left;
                            padding: 5px;
                            background-color: #3373B9;
                            color: white;
                            border-radius: 5px;
                        }}
                    """)
                    
                    # Mark the student's answer based on question type
                    if question_type == 'multiple_choice':
                        # Set the button as checked
                        for btn in box.findChildren(QRadioButton):
                            if btn.text() == student_answer:
                                btn.setChecked(True)
                                btn.setStyleSheet(f"""
                                    QRadioButton {{
                                        min-height: 30px;
                                        padding: 5px;
                                        border: 2px solid {border_color};
                                        border-radius: 5px;
                                        background-color: #E0E0E0;
                                    }}
                                """)
                    
                    elif question_type == 'true_false':
                        # Set true/false button as checked
                        for btn in box.findChildren(QRadioButton):
                            if btn.text().lower() == student_answer.lower():
                                btn.setChecked(True)
                                btn.setStyleSheet(f"""
                                    QRadioButton {{
                                        min-height: 30px;
                                        padding: 5px;
                                        border: 2px solid {border_color};
                                        border-radius: 5px;
                                        background-color: #E0E0E0;
                                    }}
                                """)
                    
                    elif question_type == 'identification':
                        # Set identification answer text
                        answer_input = box.findChild(QLineEdit)
                        if answer_input:
                            answer_input.setText(student_answer)  # This sets the actual text of the answer
                            answer_input.setPlaceholderText("")  # Clear placeholder
                            answer_input.setStyleSheet(f"""
                                QLineEdit {{
                                    border: 2px solid {border_color};
                                    background-color: #f0f0f0;
                                    border-radius: 8px;
                                    padding: 6px;
                                    font-size: 14px;
                                    min-height: 30px;
                                }}
                            """)
                    
                    # Add feedback label
                    feedback_label = QLabel()
                    if is_correct:
                        feedback_label.setText("✓ Correct")
                        feedback_label.setStyleSheet("color: green; font-weight: bold; margin-top: 5px; font-size: 14px;")
                    else:
                        feedback_label.setText(f"✗ Incorrect (Correct answer: {correct_answer})")
                        feedback_label.setStyleSheet("color: red; font-weight: bold; margin-top: 5px; font-size: 14px;")
                    
                    # Add the feedback label to the question box layout
                    box_layout = box.layout()
                    # Check if feedback label already exists
                    exists = False
                    for i in range(box_layout.count()):
                        item = box_layout.itemAt(i)
                        if item.widget() and isinstance(item.widget(), QLabel) and ("Correct" in item.widget().text() or "Incorrect" in item.widget().text()):
                            exists = True
                            break
                    
                    if not exists:
                        box_layout.addWidget(feedback_label)
                
        except mysql.connector.Error as e:
            print(f"Database error in load_student_responses: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load student responses: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def populate_exam_questions(self, exam_parts):
        """Create the exam structure with questions."""
        part_count = 1
        
        for part_index, (exam_type, num_items, description, part_num) in enumerate(exam_parts, start=1):
            part_label = QLabel(f"Part {part_index}: {exam_type}")
            part_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.container_layout.addWidget(part_label)

            instruction_box = AutoResizeTextEdit(description if description else "No instructions provided.")
            instruction_box.setFixedHeight(50)
            instruction_box.setObjectName(f"instruction_part_{part_index}")
            instruction_box.setReadOnly(True)
            instruction_box.setFocusPolicy(Qt.NoFocus)
            instruction_box.setStyleSheet("""
                QTextEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
                
            self.part_instructions.append(instruction_box)
            self.container_layout.addWidget(instruction_box)

            part_questions = [] 
            for i in range(1, num_items + 1):
                question_widget = self.create_question_widget(i, exam_type, part_num)
                part_questions.append(question_widget)
                self.container_layout.addWidget(question_widget)
            
            self.question_widgets.append((exam_type, part_questions, description, part_num))
            part_count += 1

        # Add a summary section
        self.add_summary_section()
        
        self.container.setLayout(self.container_layout)
        
    def create_question_widget(self, q_num, exam_type, part_num):
        """Create a question widget for the exam."""
        question_box = QGroupBox(f"Question {q_num}")
        question_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3373B9;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #F9F9E0;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
                background-color: #3373B9;
                color: white;
                border-radius: 5px;
            }
        """)
        question_layout = QVBoxLayout()

        question_input = AutoResizeTextEdit("Loading question...")
        question_input.setObjectName(f"question_{part_num}_{q_num}")
        question_input.setReadOnly(True)
        question_input.setFocusPolicy(Qt.NoFocus)
        question_input.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        question_layout.addWidget(question_input)

        answer_widgets = {}

        if exam_type == "MULTIPLE CHOICES":
            options_layout = QVBoxLayout()
            button_group = QButtonGroup(self)
            self.button_groups.append(button_group)

            option_inputs = {}
            for opt in ["A", "B", "C", "D"]:
                opt_layout = QHBoxLayout()
                
                radio_button = QRadioButton(opt)
                radio_button.setStyleSheet("background-color: transparent;")
                radio_button.setObjectName(f"option_{part_num}_{q_num}_{opt}")
                radio_button.setEnabled(False)  # Read-only
                
                button_group.addButton(radio_button)
                
                answer_input = AutoResizeTextEdit(f"Choice {opt}")
                answer_input.setObjectName(f"choice_{part_num}_{q_num}_{opt}")
                answer_input.setReadOnly(True)
                answer_input.setFocusPolicy(Qt.NoFocus)
                answer_input.setStyleSheet("""
                    QTextEdit {
                        background-color: #f5f5f5;
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        padding: 5px;
                    }
                """)
                
                option_inputs[opt] = answer_input
                opt_layout.addWidget(radio_button)
                opt_layout.addWidget(answer_input)
                options_layout.addLayout(opt_layout)

            answer_widgets["options"] = option_inputs
            question_layout.addLayout(options_layout)
        
        elif exam_type == "TRUE OR FALSE":
            tf_layout = QHBoxLayout()
            button_group = QButtonGroup(self)
            button_group.setObjectName(f"tf_group_{part_num}_{q_num}")
            self.button_groups.append(button_group)

            # Common style for both radio buttons to ensure consistent height
            radio_style = """
                QRadioButton {
                    min-height: 40px;
                    padding: 8px;
                    border-radius: 5px;
                }
                QRadioButton:checked {
                    background-color: rgba(200, 200, 200, 0.3);
                }
            """

            true_btn = QRadioButton("True")
            true_btn.setObjectName(f"true_btn_{part_num}_{q_num}")
            true_btn.setEnabled(False)  # Read-only
            true_btn.setStyleSheet(radio_style)
            
            false_btn = QRadioButton("False")
            false_btn.setObjectName(f"false_btn_{part_num}_{q_num}")
            false_btn.setEnabled(False)  # Read-only
            false_btn.setStyleSheet(radio_style)

            button_group.addButton(true_btn)
            button_group.addButton(false_btn)

            # Use a fixed-width layout to ensure consistent sizing
            tf_layout.addWidget(true_btn, 1)  # Use stretch factor for equal sizing
            tf_layout.addWidget(false_btn, 1)
            question_layout.addLayout(tf_layout)

        elif exam_type == "IDENTIFICATION":
            student_answer_input = QLineEdit()
            student_answer_input.setObjectName(f"student_answer_{part_num}_{q_num}")
            student_answer_input.setPlaceholderText("Student answer will be shown here")
            student_answer_input.setReadOnly(True)
            student_answer_input.setStyleSheet("""
                QLineEdit {
                    background-color: #f5f5f5;
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 14px;
                }
            """)

            question_layout.addWidget(student_answer_input)

        question_box.setLayout(question_layout)
        question_box.exam_type = exam_type
        question_box.question_num = q_num
        question_box.part_num = part_num
        question_box.input_widgets = {
            "question": question_input,
            "answers": answer_widgets
        }
        
        # Initialize properties to store correct answer and question ID
        question_box.correct_answer = ""
        question_box.question_id = None
        
        return question_box
    
    def add_summary_section(self):
        """Add a summary section with the student's score."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor(dictionary=True)
            
            # Get the student's score for this exam
            cursor.execute("""
                SELECT COUNT(*) as total, SUM(is_correct) as correct
                FROM student_answers
                WHERE exam_id = %s AND student_id = %s
            """, (self.exam_id, self.student_id))
            
            score = cursor.fetchone()
            
            if score:
                # Debug message
                print(f"Student score: {score['correct']}/{score['total']}")
                
                summary_frame = QFrame()
                summary_frame.setStyleSheet("""
                    QFrame {
                        background-color: #E8F4F8;
                        border: 2px solid #3373B9;
                        border-radius: 8px;
                        margin-top: 20px;
                        padding: 15px;
                    }
                """)
                summary_layout = QVBoxLayout()
                
                summary_title = QLabel("Exam Summary")
                summary_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #3373B9;")
                summary_layout.addWidget(summary_title)
                
                # Calculate score
                correct = score['correct'] if score['correct'] is not None else 0
                total = score['total'] if score['total'] is not None else 0
                
                score_text = f"Your Score: {correct}/{total}"
                if total > 0:
                    percentage = (correct / total) * 100
                    score_text += f" ({percentage:.1f}%)"
                    
                    # Add visual grade indicator
                    if percentage >= 90:
                        grade = "A"
                        color = "#4CAF50"  # Green
                    elif percentage >= 80:
                        grade = "B"
                        color = "#8BC34A"  # Light green
                    elif percentage >= 70:
                        grade = "C"
                        color = "#FFC107"  # Amber
                    elif percentage >= 60:
                        grade = "D"
                        color = "#FF9800"  # Orange
                    else:
                        grade = "F"
                        color = "#F44336"  # Red
                        
                    grade_label = QLabel(f"Grade: {grade}")
                    grade_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; margin-top: 5px;")
                    
                score_label = QLabel(score_text)
                score_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
                summary_layout.addWidget(score_label)
                
                if total > 0:
                    summary_layout.addWidget(grade_label)
                
                summary_frame.setLayout(summary_layout)
                self.container_layout.addWidget(summary_frame)
            else:
                # Debug message
                print("No score information found")
                
        except mysql.connector.Error as e:
            print(f"Database error in add_summary_section: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load score summary: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    
    def generate_pdf_report(self):
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'TUPCcoet@23!',
            'database': 'axis'
        }

        report = PDFReport(
            exam_id=self.exam_id,
            student_id=self.student_id,
            title=self.title.text(),
            major_type=self.major_type.text(),
            time_limit=self.time_limit.text(),
            question_widgets=self.question_widgets,
            db_config=db_config
        )
        report.generate_pdf()

class PDFReport:
    def __init__(self, exam_id, student_id, title, major_type, time_limit, question_widgets, db_config):
        self.exam_id = exam_id
        self.student_id = student_id
        self.title = title
        self.major_type = major_type
        self.time_limit = time_limit
        self.question_widgets = question_widgets
        self.db_config = db_config

        self.student_name = self.fetch_user_full_name(self.student_id)
        self.professor_name = self.fetch_professor_name()
        self.answers, self.date_taken, self.score_display = self.fetch_student_answers_and_compute_score()

    def fetch_user_full_name(self, user_id):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT first_name, middle_name, last_name, suffix 
            FROM user_account WHERE user_id = %s
        """, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        if row:
            parts = [row["first_name"]]
            if row["middle_name"]:
                parts.append(row["middle_name"][0] + ".")
            parts.append(row["last_name"])
            if row["suffix"]:
                parts.append(row["suffix"])
            return " ".join(parts)
        return "Unknown"

    def fetch_professor_name(self):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT created_by FROM examination_form WHERE exam_id = %s LIMIT 1", (self.exam_id,))
        row = cursor.fetchone()
        if not row or not row["created_by"]:
            cursor.close()
            connection.close()
            return "Unknown"
        professor_id = row["created_by"]
        cursor.execute("""
            SELECT first_name, middle_name, last_name, suffix 
            FROM user_account WHERE user_id = %s
        """, (professor_id,))
        prof_row = cursor.fetchone()
        cursor.close()
        connection.close()
        if prof_row:
            parts = [prof_row["first_name"]]
            if prof_row["middle_name"]:
                parts.append(prof_row["middle_name"][0] + ".")
            parts.append(prof_row["last_name"])
            if prof_row["suffix"]:
                parts.append(prof_row["suffix"])
            return " ".join(parts)
        return "Unknown"

    def fetch_student_answers_and_compute_score(self):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT question_id, answer, is_correct, start_time
            FROM student_answers
            WHERE exam_id = %s AND student_id = %s
        """, (self.exam_id, self.student_id))
        rows = cursor.fetchall()
        answers = {row["question_id"]: row for row in rows}
        
        correct = sum(1 for row in rows if row.get("is_correct"))
        
        total_questions = sum(
            1 for _, part_questions, _, _ in self.question_widgets for _ in part_questions
        )
        
        date_taken = "Examination Missed"
        if rows and isinstance(rows[0].get("start_time"), datetime):
            date_taken = rows[0]["start_time"].strftime("%Y-%m-%d")

        score_display = f"{correct}/{total_questions}" if total_questions > 0 else "0/0"

        cursor.close()
        connection.close()
        return answers, date_taken, score_display
    
    def generate_pdf(self):
        filename = f"exam_response_{self.exam_id}_{self.student_id}.pdf"
        filepath = os.path.join(os.getcwd(), filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', fontSize=20, leading=24, fontName='Helvetica-Bold',
                                    alignment=TA_CENTER, textColor=colors.HexColor("#0B3954"), spaceAfter=14)
        subtitle_style = ParagraphStyle(name='Subtitle', fontSize=14, leading=18, fontName='Helvetica-Oblique',
                                        alignment=TA_CENTER, textColor=colors.HexColor("#537895"), spaceAfter=18)
        section_title_style = ParagraphStyle(name='SectionTitle', fontSize=12, textColor=colors.HexColor("#1E3D59"),
                                            fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=8)
        summary_style = ParagraphStyle(name='Summary', fontSize=11, leading=14,
                                    spaceBefore=20, spaceAfter=10, fontName='Helvetica-Bold', alignment=TA_CENTER)
        wrap_style = ParagraphStyle(name='Wrap', fontSize=8, leading=10, fontName='Helvetica')

        story = []

        # Title
        story.append(Paragraph("AXIS: Examination Management System", title_style))
        story.append(Paragraph("Student Assessment Report", subtitle_style))
        story.append(Spacer(1, 10))

        # Header Table
        header_data = [
            ["Exam Title", f"{self.major_type.upper()} - {self.title}"],
            ["Student Name", self.student_name],
            ["Student ID", self.student_id],
            ["Professor", self.professor_name],
            ["Exam ID", self.exam_id],
            ["Date Taken", self.date_taken],
            ["Score", self.score_display]
        ]
        header_data_wrapped = [[Paragraph(str(key), wrap_style), Paragraph(str(value), wrap_style)] for key, value in header_data]
        header_table = Table(header_data_wrapped, colWidths=[100, 380])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 16))

        # Question Table
        table_data = [["#", "Question", "Student Answer", "Correct Answer", "Choices", "Result"]]
        question_index = 1
        for exam_type, part_questions, description, part_num in self.question_widgets:
            for q_widget in part_questions:
                q_id = getattr(q_widget, "question_id", None)
                question_text = q_widget.input_widgets["question"].toPlainText().strip()
                student_data = self.answers.get(q_id, {})
                student_answer = student_data.get("answer", "").strip()
                is_correct = student_data.get("is_correct", 0)
                correct_answer = getattr(q_widget, "correct_answer", "").strip()
                result_text = "✓ Correct" if is_correct else "✗ Incorrect"

                # Handle Choices
                if exam_type.upper() == "MULTIPLE CHOICES":
                    options = q_widget.input_widgets["answers"]["options"]
                    choices_str = "<br/>".join([
                        f"{k}. {options[k].toPlainText().strip()}"
                        for k in sorted(options.keys())
                    ])
                elif exam_type.upper() == "TRUE OR FALSE":
                    choices_str = "True / False"
                else:
                    choices_str = "-"

                # Wrap all text using Paragraph
                row = [
                    Paragraph(str(question_index), wrap_style),
                    Paragraph(question_text, wrap_style),
                    Paragraph(student_answer or "Not Answered", wrap_style),
                    Paragraph(correct_answer or "-", wrap_style),
                    Paragraph(choices_str.strip(), wrap_style),
                    Paragraph(result_text, wrap_style)
                ]
                table_data.append(row)
                question_index += 1

        # Add Table to Story
        col_widths = [25, 170, 85, 85, 100, 50]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.darkgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        story.append(Paragraph("Assessment Details", section_title_style))
        story.append(table)
        story.append(Spacer(1, 20))

        # Summary
        total_questions = len(self.answers)
        correct_answers = sum(1 for ans in self.answers.values() if ans.get("is_correct"))
        percentage = (correct_answers / total_questions * 100) if total_questions else 0

        if percentage >= 90:
            remarks = "Excellent performance."
        elif percentage >= 75:
            remarks = "Good performance."
        elif percentage >= 50:
            remarks = "Satisfactory performance."
        else:
            remarks = "Needs improvement."

        summary_text = (
            f"Total Questions: {total_questions}<br/>"
            f"Correct Answers: {correct_answers}<br/>"
            f"Score Percentage: {percentage:.2f}%<br/>"
            f"Remarks: {remarks}"
        )
        story.append(Paragraph("Summary", section_title_style))
        story.append(Paragraph(summary_text, summary_style))

        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("© 2025 AXIS: Examination Management System. All rights reserved.",
                            ParagraphStyle(name="Footer", fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))

        doc.build(story)
        print(f"PDF generated: {filepath}")
        os.startfile(filepath)


class SubmissionSuccessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exam Submitted")
        self.setMinimumWidth(400)
        
        # Get exam_id and student_id from parent if available
        if hasattr(parent, 'exam_id') and hasattr(parent, 'user_id'):
            self.exam_id = parent.exam_id
            self.student_id = parent.user_id
        else:
            self.exam_id = None
            self.student_id = None
        
        self.parent_window = parent
        
        # Layout
        layout = QVBoxLayout()
        
        # Success icon and message
        message_layout = QHBoxLayout()
        
        success_icon = QLabel("✓")
        success_icon.setStyleSheet("font-size: 48px; color: green;")
        message_layout.addWidget(success_icon)
        
        message_label = QLabel("Your exam has been submitted successfully!")
        message_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        
        layout.addLayout(message_layout)
        
        # Additional information
        info_label = QLabel("Thank you for completing the exam. Your responses have been recorded.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #555;")
        layout.addWidget(info_label)
        
        # Show score if available
        if hasattr(parent, 'correct_answers') and hasattr(parent, 'total_questions'):
            score_text = f"Your Score: {parent.correct_answers}/{parent.total_questions}"
            if parent.total_questions > 0:
                percentage = (parent.correct_answers / parent.total_questions) * 100
                score_text += f" ({percentage:.1f}%)"
            
            score_label = QLabel(score_text)
            score_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #3373B9; margin: 10px 0;")
            layout.addWidget(score_label)
        
        # View responses button
        self.view_responses_btn = QPushButton("View My Responses")
        self.view_responses_btn.setStyleSheet("""
            QPushButton {
                background-color: #3373B9;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2C639D;
            }
        """)
        self.view_responses_btn.clicked.connect(self.show_responses)
        
        # OK button
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        self.ok_btn.clicked.connect(self.accept)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.view_responses_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def show_responses(self):
        if self.exam_id and self.student_id:
            exam_result_dialog = ExamResult(self.exam_id, self.student_id, self)
            exam_result_dialog.show()  # Use show() instead of exec()
        else:
            QMessageBox.warning(self, "Error", "Unable to load exam responses. Missing exam or student information.")

    def closeEvent(self, event):
        self.accept()  # Same behavior as clicking OK
        event.accept()

class Guardian(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        if not isinstance(user_id, str) or not user_id.startswith("TUPC-S"):
            raise ValueError("Invalid user_id provided to Guardian class")

        self.user_id = user_id
        self.current_user_id = self.user_id

        loader = QUiLoader()
        self.guardian_ui = loader.load(resource_path("UI/Parent.ui"), self)  # Ensure Parent.ui is a QWidget
        Icons(self.guardian_ui)  # Assuming Icons() is defined elsewhere and modifies guardian_ui

        # Set the loaded UI directly as the central widget
        self.setCentralWidget(self.guardian_ui)
        self.showMaximized()

        # Find UI components
        self.studentperfbtn = self.guardian_ui.findChild(QPushButton, "sp_btn")
        self.notifbtn = self.guardian_ui.findChild(QPushButton, "notif_btn")
        self.logoutbtn = self.guardian_ui.findChild(QPushButton, "logout_btn")
        self.prelim_chart = self.guardian_ui.findChild(QCheckBox, "prelim_chart")
        self.midterm_chart = self.guardian_ui.findChild(QCheckBox, "midterm_chart")
        self.finals_chart = self.guardian_ui.findChild(QCheckBox, "finals_chart")
        self.sem_sp = self.guardian_ui.findChild(QComboBox, "sem_sp")
        self.sp_table = self.guardian_ui.findChild(QTableWidget, "sp_table")
        self.sp_graph = self.guardian_ui.findChild(QFrame, "sp_graph")
        self.sp_pie = self.guardian_ui.findChild(QFrame, "sp_pie")
        self.perf_message = self.guardian_ui.findChild(QLabel, "sp_comment")
        self.child_name = self.guardian_ui.findChild(QLabel, "child_name")
        self.icon_label = self.guardian_ui.findChild(QLabel, "congrats_s")

        # Connect checkboxes to filter function
        self.prelim_chart.stateChanged.connect(self.update_bar_graph)
        self.midterm_chart.stateChanged.connect(self.update_bar_graph)
        self.finals_chart.stateChanged.connect(self.update_bar_graph)
        self.sem_sp.currentIndexChanged.connect(self.update_bar_graph)
        self.sem_sp.currentTextChanged.connect(self.update_bar_graph)

        # Connect logout button
        self.logoutbtn.clicked.connect(self.logout)

        # Load student data
        self.fetch_student_data()

    def fetch_student_data(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            cursor = connection.cursor()

            name_query = """
            SELECT first_name, last_name
            FROM user_account
            WHERE user_id = %s
            """
            cursor.execute(name_query, (self.user_id,))
            name_result = cursor.fetchone()

            if name_result:
                first_name, last_name = name_result
                full_name = f"{first_name} {last_name}".strip()
                
                # Possessive form logic
                if full_name[-1].lower() == 's':
                    display_name = f"{full_name}' OVERALL PERFORMANCE"
                else:
                    display_name = f"{full_name}'s OVERALL PERFORMANCE"
                
                self.child_name.setText(display_name.upper())
            else:
                self.child_name.setText("UNKNOWN STUDENT - OVERALL PERFORMANCE")

            query = """
            SELECT 
                ef.exam_id,
                ef.subject_code AS Course, 
                sa.major_exam_type AS "Major Exam Type",
                ef.semester AS Semester, 
                (
                    SELECT SUM(number_of_items) 
                    FROM examination_form 
                    WHERE exam_id = ef.exam_id
                ) AS Total_Items, 
                (
                    SELECT COUNT(DISTINCT sa_sub.question_id)
                    FROM student_answers sa_sub
                    WHERE sa_sub.exam_id = ef.exam_id
                    AND sa_sub.student_id = sa.student_id
                    AND sa_sub.status = 'Completed'
                    AND sa_sub.is_correct = 1
                ) AS Correct_Answers
            FROM student_answers sa
            JOIN examination_form ef ON sa.exam_id = ef.exam_id
            WHERE sa.student_id = %s AND sa.status = 'Completed'
            GROUP BY ef.exam_id, ef.subject_code, sa.major_exam_type, ef.semester, sa.student_id
            ORDER BY ef.subject_code, sa.major_exam_type;
            """

            cursor.execute(query, (self.user_id,))
            results = cursor.fetchall()

            self.sp_table.setRowCount(0)
            self.sp_table.setColumnCount(5)
            self.sp_table.setHorizontalHeaderLabels(["Exam ID", "Course", "Major Exam Type", "Semester", "Result"])
            self.exam_data_for_graph = []  # Store for graph updates

            if not results:
                self.update_bar_graph()
                return

            for row_index, (exam_id, course, exam_type, semester, total_items, correct_answers) in enumerate(results):
                self.sp_table.insertRow(row_index)

                percentage = (correct_answers / total_items * 100) if total_items else 0
                result_str = f"{correct_answers}/{total_items}"
                result_item = QTableWidgetItem(result_str)
                result_item.setTextAlignment(Qt.AlignCenter)
                result_item.setForeground(QBrush(QColor('red' if percentage < 75 else 'green')))

                exam_id_item = QTableWidgetItem(str(exam_id))
                font = QFont()
                font.setUnderline(True)
                exam_id_item.setFont(font)
                exam_id_item.setForeground(QBrush(QColor('blue')))
                exam_id_item.setTextAlignment(Qt.AlignCenter)

                items = [
                    exam_id_item,
                    QTableWidgetItem(course),
                    QTableWidgetItem(exam_type),
                    QTableWidgetItem(semester),
                    result_item
                ]

                for col_index, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    self.sp_table.setItem(row_index, col_index, item)

                self.exam_data_for_graph.append((exam_id, course, exam_type, semester, total_items, correct_answers))

            self.sp_table.resizeColumnsToContents()
            self.sp_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            cursor.close()
            connection.close()

            self.update_bar_graph()
            self.update_pie_gauge()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")

    def update_bar_graph(self):
        selected_semester = self.sem_sp.currentText() if self.sem_sp else "All"

        filtered_results = []
        for exam_id, course, exam_type, semester, total_items, correct_answers in self.exam_data_for_graph:
            if self.filter_by_exam_type(exam_type):
                if selected_semester == "All" or selected_semester.lower() == semester.lower():
                    filtered_results.append((exam_id, course, exam_type, semester, total_items, correct_answers))

        layout = self.sp_graph.layout()
        if layout is None:
            layout = QVBoxLayout(self.sp_graph)
            self.sp_graph.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        if not filtered_results:
            message_label = QLabel("No existing data as of the moment.")
            message_label.setAlignment(Qt.AlignCenter)
            message_label.setStyleSheet("font-size: 16px; color: lightgray;")
            layout.addWidget(message_label)
            return

        courses = [result[1] for result in filtered_results]
        correct_answers = [result[5] for result in filtered_results]
        total_items = [result[4] for result in filtered_results]
        percentages = [(ca / ti * 100) if ti else 0 for ca, ti in zip(correct_answers, total_items)]

        bar_set = QBarSet("Performance")
        bar_set.append(percentages)
        bar_set.setColor(QColor("#004953"))  # Midnight green for bars

        bar_series = QBarSeries()
        bar_series.append(bar_set)

        # Apply Cerulean Blue Theme
        chart = QChart()
        chart.setTheme(QChart.ChartThemeBlueCerulean)  # Cerulean Blue Theme
        chart.addSeries(bar_series)
        chart.setTitle(f"Student Exam Performance - {selected_semester}")
        chart.setAnimationOptions(QChart.AllAnimations)

        # Axis X
        axis_x = QBarCategoryAxis()
        axis_x.append(courses)
        axis_x.setLabelsBrush(QColor("white"))  # White labels for contrast
        chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)

        # Axis Y
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTitleText("Percentage (%)")
        axis_y.setTitleBrush(QColor("white"))  # White title for contrast
        axis_y.setLabelsBrush(QColor("white"))  # White labels for contrast
        chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(chart_view)

    def update_pie_gauge(self):
        if not hasattr(self, 'exam_data_for_graph') or not self.exam_data_for_graph:
            return

        # Step 1: Aggregate performance per semester
        semester_totals = {}
        for _, _, _, semester, total_items, correct_answers in self.exam_data_for_graph:
            if semester not in semester_totals:
                semester_totals[semester] = {'correct': 0, 'total': 0}
            semester_totals[semester]['correct'] += correct_answers
            semester_totals[semester]['total'] += total_items

        # Step 2: Clear old charts from sp_pie layout
        layout = self.sp_pie.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        else:
            layout = QHBoxLayout(self.sp_pie)
            self.sp_pie.setLayout(layout)

        # Step 3: Create pie chart per semester
        for semester, score in semester_totals.items():
            correct = score['correct']
            total = score['total']
            percentage = int((correct / total) * 100) if total else 0

            # Create pie (donut) series
            series = QPieSeries()
            series.append("Achieved", percentage)
            series.append("Remaining", 100 - percentage)

            # Style the slices
            achieved_slice = series.slices()[0]
            remaining_slice = series.slices()[1]

            achieved_slice.setColor(QColor("green" if percentage >= 75 else "red"))
            achieved_slice.setLabelVisible(False)

            remaining_slice.setColor(QColor("#e0e0e0"))
            remaining_slice.setLabelVisible(False)

            series.setHoleSize(0.6)

            # Create chart
            chart = QChart()
            chart.setTheme(QChart.ChartThemeBlueCerulean)  # Apply Cerulean Blue Theme
            chart.addSeries(series)
            chart.setTitle(f"{semester} - {percentage}%")
            chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.legend().hide()
            chart.setBackgroundVisible(True)
            chart.setContentsMargins(0, 0, 0, 0)
            chart.setMargins(QMargins(0, 0, 0, 0))

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumWidth(200)  # optional, for spacing
            chart_view.setMaximumWidth(300)

            layout.addWidget(chart_view)

        percentages = []
        for semester, score in semester_totals.items():
            correct = score['correct']
            total = score['total']
            percentage = int((correct / total) * 100) if total else 0
            percentages.append(percentage)

        if len(percentages) == 2:
            if all(p >= 75 for p in percentages):
                self.perf_message.setText("Great job! Your child is performing well in most of their exams. Slay!")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/20.png"))
            elif any(p >= 75 for p in percentages):
                self.perf_message.setText("Your child is making progress! One semester went well—encourage them to improve the other.")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/21.png"))
            else:
                self.perf_message.setText("There’s room for improvement. Consider offering more support and motivation for their next exams.")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/22.png"))
        elif len(percentages) == 1:
            if percentages[0] >= 75:
                self.perf_message.setText("Strong start! Your child is off to a great performance this semester. Keep encouraging them!")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/23.png"))
            else:
                self.perf_message.setText("Your child has begun their semester—now’s a good time to help them aim higher in their exams.")
                self.icon_label.setPixmap(QPixmap(r"UI/Resources/24.png"))
        else:
            self.perf_message.setText("No exam performance data is available yet. Stay tuned for updates on your child's progress.")
            self.icon_label.setPixmap(QPixmap(r"UI/Resources/25.png"))

    def filter_by_exam_type(self, exam_type):
        # Check which checkboxes are selected and filter accordingly
        if self.prelim_chart.isChecked() and "PRELIM" in exam_type:
            return True
        if self.midterm_chart.isChecked() and "MIDTERM" in exam_type:
            return True
        if self.finals_chart.isChecked() and "FINAL" in exam_type:
            return True
        return False
    
    def logout(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Logout Confirmation")
        msg_box.setText("Are you sure you want to log out?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            self.login_window = Login_Register()
            self.login_window.show()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login_Register()
    window.setWindowTitle("Examination Management System")
    window.resize(800, 600)  
    window.show()
    sys.exit(app.exec())
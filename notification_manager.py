from PySide6.QtWidgets import *
from PySide6.QtUiTools import *
from PySide6.QtCore import *
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class NotificationManager:
    def __init__(self, parent=None):
        self.parent = parent
        print(f"NotificationManager initialized with parent: {type(self.parent)}")

        loader = QUiLoader()
        ui_path = resource_path("UI/notification.ui")  # Use resource_path here
        ui_file = QFile(ui_path)
        if not ui_file.open(QFile.ReadOnly):
            print(f"Failed to open UI file: {ui_path}")
            return

        self.ui = loader.load(ui_file)
        ui_file.close()

        self.notif_content = self.ui.findChild(QListWidget, "notif_content")
        self.notif_count = self.ui.findChild(QLabel, "notif_count")
        self.notifications = []

        self.notif_content.itemClicked.connect(self.handle_notification_click)

        # Wrap the UI in a QDialog
        self.dialog = QDialog(parent)
        self.dialog.setWindowTitle("Notifications")
        layout = QVBoxLayout(self.dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def send_notification(self, sender_id, recipient_role, message, recipient_id=None):
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
                    INSERT INTO notifications (sender_id, recipient_role, recipient_id, message, is_read, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    sender_id,
                    recipient_role,
                    recipient_id,
                    message,
                    False,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                cursor.execute(insert_query, values)
                connection.commit()
        except Error as e:
            print(f"Notification Error: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def load_notifications(self, role, user_id=None):
        self.notif_content.clear()
        self.notifications.clear()
        print(f"[DEBUG] load_notifications() called with role='{role}', user_id='{user_id}'")

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                if user_id:
                    user_id = user_id.strip()
                    print(f"[DEBUG] Loading notifications for both role='{role}' and user_id='{user_id}'")
                    query = """
                        SELECT message, is_read, created_at 
                        FROM notifications 
                        WHERE recipient_role = %s AND (recipient_id IS NULL OR recipient_id = %s)
                        ORDER BY created_at DESC
                    """
                    cursor.execute(query, (role, user_id))
                else:
                    print(f"[DEBUG] Loading notifications for role only: '{role}'")
                    query = """
                        SELECT message, is_read, created_at 
                        FROM notifications 
                        WHERE recipient_role = %s
                        ORDER BY created_at DESC
                    """
                    cursor.execute(query, (role,))

                results = cursor.fetchall()
                print(f"[DEBUG] Fetched {len(results)} notifications")

                current_group = None
                for row in results:
                    timestamp = row["created_at"]
                    message = row["message"]
                    is_read = row["is_read"]

                    group_label = self.get_group_label(timestamp)
                    if group_label != current_group:
                        current_group = group_label
                        header_item = QListWidgetItem(f"📅 {group_label}")
                        header_item.setFlags(Qt.ItemIsEnabled)
                        header_item.setForeground(Qt.darkGray)
                        header_item.setTextAlignment(Qt.AlignCenter)
                        self.notif_content.addItem(header_item)

                    self.add_notification(message, is_read, timestamp)

        except Error as e:
            print(f"[ERROR] Load Notification Error: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_group_label(self, timestamp):
        today = datetime.today().date()
        created_date = timestamp.date()

        if created_date == today:
            return "Today"
        elif created_date == today - timedelta(days=1):
            return "Yesterday"
        else:
            return created_date.strftime("%b %d, %Y")
        
    def handle_notification_click(self, item):
        import re
        print("Notification clicked:", item.text())
        message = item.text()

        # ADMIN: New user registration
        if "📋 New user registration submitted for approval:" in message:
            lines = message.split("\n")
            notif_time_str = ""

            for line in lines:
                if line.startswith("[") and "]" in line:
                    notif_time_str = line.split("]")[0].strip("[ ]")

            if notif_time_str:
                if hasattr(self.parent, "open_registration_details"):
                    self.dialog.close()
                    self.parent.show_pendingaccs_page()
                    QTimer.singleShot(300, lambda: self.parent.open_registration_details(notif_time_str))
                else:
                    QMessageBox.warning(self.parent, "Error", "Parent does not have open_registration_details method.")
                return  # Done handling admin notification


        if "just submitted their" in message and "Student ID:" in message and "Submitted on:" in message and "Exam ID:" in message:
            student_id_match = re.search(r"Student ID:\s*(TUPC-S-\d{4})", message)
            submitted_match = re.search(r"Submitted on:\s*(.*?)\s*\|\s*Exam ID:\s*(EX\d{3})", message)

            if not all([student_id_match, submitted_match]):
                print("Regex does not match.")
                QMessageBox.warning(self.parent, "Notification Error", "Could not extract complete submission details.")
                return

            submission_details = {
                "user_id": student_id_match.group(1).strip(),
                "exam_id": submitted_match.group(2).strip()
            }

            if hasattr(self.parent, "open_exam_result"):
                self.dialog.close()
                self.parent.open_exam_result(submission_details["user_id"], submission_details["exam_id"])
            else:
                QMessageBox.warning(self.parent, "Error", "Parent does not support viewing exam results.")
            return

        # STUDENT: Exam published notification
        semester_match = re.search(r'Semester: (.+)', message)
        subject_code_match = re.search(r'Subject Code: (.+)', message)
        exam_date_match = re.search(r'Exam Date: (.+)', message)
        exam_sched_match = re.search(r'Exam Scheduled for: (.+)', message)

        if not all([semester_match, subject_code_match, exam_date_match, exam_sched_match]):
            QMessageBox.warning(self.parent, "Notification Error", "Could not extract complete exam details from notification.")
            return

        exam_details = {
            "semester": semester_match.group(1).strip(),
            "subject_code": subject_code_match.group(1).strip(),
            "exam_date": exam_date_match.group(1).strip(),
            "exam_schedule": exam_sched_match.group(1).strip()
        }

        if hasattr(self.parent, "open_exam_details"):
            self.dialog.close()
            self.parent.open_exam_details(exam_details)
        else:
            QMessageBox.warning(self.parent, "Error", "Parent does not support exam handling.")


    def add_notification(self, message: str, read: bool = False, timestamp: datetime = None):
        time_str = timestamp.strftime("[%I:%M:%S %p]") if timestamp else ""
        full_message = f"{time_str} - {message}"

        item = QListWidgetItem(full_message)
        if not read:
            item.setForeground(Qt.red)  # Unread notifications in red
            self.notifications.append(message)
        else:
            item.setForeground(Qt.green)  # Read notifications in green
        self.notif_content.addItem(item)

        # Color-code group labels differently
        if 'Today' in full_message:
            item.setBackground(Qt.lightGray)  # Light gray for "Today"
        elif 'Yesterday' in full_message:
            item.setBackground(Qt.yellow)  # Yellow for "Yesterday"

        self.update_count()

    def update_count(self):
        count = len(self.notifications)
        self.notif_count.setText(str(count))

    def mark_all_as_read(self, role, user_id=None):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TUPCcoet@23!",
                database="axis"
            )
            if connection.is_connected():
                cursor = connection.cursor()

                if user_id:
                    update_query = """
                        UPDATE notifications
                        SET is_read = TRUE
                        WHERE recipient_role = %s AND (recipient_id IS NULL OR recipient_id = %s)
                    """
                    cursor.execute(update_query, (role, user_id))
                else:
                    update_query = """
                        UPDATE notifications
                        SET is_read = TRUE
                        WHERE recipient_role = %s
                    """
                    cursor.execute(update_query, (role,))

                connection.commit()
        except Error as e:
            print(f"Error marking notifications as read: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

            self.notifications.clear()
            self.update_count()

    def show_dialog(self):
        self.dialog.exec_()

    def close_dialog(self):
        self.dialog.close()  # Non-blocking show, Admin handles exec_()

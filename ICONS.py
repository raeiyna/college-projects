from PySide6.QtWidgets import QLabel, QPushButton
from PySide6.QtGui import QPixmap, QIcon

class Icons:
    def __init__(self, ui):
        self.ui = ui
        self.set_icons()

    def set_icons(self):
        # ADMIN
        self.set_icon("logo", r"UI/Resources/LOGO.png")
        self.set_icon("dashboard_a", r"UI/Resources/dashboard-black.png")
        self.set_icon("pending_a", r"UI/Resources/pending (2).png")
        self.set_icon("clock_a", r"UI/Resources/pending.png")
        self.set_icon("student_a", r"UI/Resources/students.png")
        self.set_icon("faculty_a", r"UI/Resources/faculty.png")
        self.set_icon("approval_a", r"UI/Resources/pending_blk.png")
        self.set_icon("userma_a", r"UI/Resources/users.png")

        self.set_button_icon("notif_btn", r"UI/Resources/notification.png")
        self.set_button_icon("dashboard_btn", r"UI/Resources/dashboard.png")
        self.set_button_icon("pendingaccs_btn", r"UI/Resources/pending.png")
        self.set_button_icon("usermanagement_btn", r"UI/Resources/pending (2).png")
        self.set_button_icon("logout_btn", r"UI/Resources/logout.png")

        # FACULTY
        self.set_icon("logo_f", r"UI/Resources/LOGO.png")
        self.set_icon("dashboard_f", r"UI/Resources/dashboard-black.png")
        self.set_icon("totals_f", r"UI/Resources/students.png")
        self.set_icon("studp_a", r"UI/Resources/stud_performance-blk.png")
        self.set_icon("class_a", r"UI/Resources/users.png")
        self.set_icon("exams_a", r"UI/Resources/exam.png")
        self.set_icon("createe", r"UI/Resources/exam.png")

        self.set_button_icon("settings_btn", r"UI/Resources/settings.png")
        self.set_button_icon("studentstats_btn", r"UI/Resources/stud_performance.png")
        self.set_button_icon("class_btn", r"UI/Resources/pending (2).png")
        self.set_button_icon("examination_btn", r"UI/Resources/exam (1).png")

        #STUDENT
        self.set_icon("logo_s", r"UI/Resources/LOGO.png")
        self.set_icon("dashboard_s", r"UI/Resources/dashboard-black.png") 
        self.set_icon("myperf_s", r"UI/Resources/stud_performance-blk.png") 
        self.set_icon("congrats_s", r"UI/Resources/congrats.png") 
        self.set_icon("takee_s", r"UI/Resources/exam.png") 

        self.set_button_icon("notif_btn", r"UI/Resources/notification.png") 
        self.set_button_icon("settings_btn", r"UI/Resources/settings.png") 
        self.set_button_icon("dashboard_btn", r"UI/Resources/dashboard.png")
        self.set_button_icon("myperformance_btn", r"UI/Resources/stud_performance.png")
        self.set_button_icon("takeexam_btn", r"UI/Resources/exam (1).png")
        self.set_button_icon("logout_btn", r"UI/Resources/logout.png") 

        #GUARDIAN
        self.set_icon("logo_g", r"UI/Resources/LOGO.png")
        self.set_icon("myperf_g", r"UI/Resources/stud_performance-blk.png")
        self.set_icon("congrats_g", r"UI/Resources/congrats.png")

        self.set_button_icon("sp_btn", r"UI/Resources/stud_performance.png")

        # GUARDIAN
        self.set_button_icon("back", r"UI/Resources/back_bnt.png")

        #USER INFORMATION
        self.set_icon("register_info", r"UI/Resources/registration (1).png")
        self.set_icon("personal_info", r"UI/Resources/personal.png")
        self.set_icon("academic_info", r"UI/Resources/acad.png")
        self.set_icon("contact_info", r"UI/Resources/contact.png")

    def set_icon(self, label_name, image_path):
        """Set icon for QLabel"""
        label = self.ui.findChild(QLabel, label_name)
        if label:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                label.setPixmap(pixmap)
            else:
                print(f"Failed to load QLabel image: {image_path}")
        else:
            print(f"QLabel '{label_name}' not found!")

    def set_button_icon(self, button_name, image_path):
        """Set icon for QPushButton"""
        button = self.ui.findChild(QPushButton, button_name)
        if button:
            icon = QIcon(image_path)
            button.setIcon(icon)
        else:
            print(f"QPushButton '{button_name}' not found!")

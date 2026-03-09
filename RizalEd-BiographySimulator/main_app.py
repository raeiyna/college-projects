# MIDTERM PROJECT: RizalEd: Beyond The Pages
# SANTOS, Reyna Marie E.
# PALACIOS, Dona Flor Saachi V.
# CARILLO, Lee Jansey

import sys
import os
import pygame
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPainterPath, QRegion, QIcon, QFont
from PyQt5.QtWidgets import QLabel, QWidget, QMessageBox, QVBoxLayout, QMainWindow, QListWidgetItem, QMessageBox, QPushButton
from PyQt5.QtCore import QRectF, Qt, QPoint
from PyQt5.uic import loadUi


pygame.init()
pygame.mixer.init()


BG_MUSIC = r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\rizaledbgmusic.mp3"
pygame.mixer.music.load(BG_MUSIC)
pygame.mixer.music.play(-1)

BUTTON_SOUND = r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\click.mp3"
BUTTON_SOUND = pygame.mixer.Sound(BUTTON_SOUND)

class UIUtils:
    @staticmethod
    def apply_rounded_corners(widget: QtWidgets.QWidget, radius: int = 15):
        path = QPainterPath()
        rect = QRectF(0, 0, widget.width(), widget.height())
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        widget.setMask(region)

    @staticmethod
    def remove_window_header(window):
        window.setWindowFlags(Qt.FramelessWindowHint)
        window.setAttribute(Qt.WA_TranslucentBackground)

    @staticmethod
    def setup_window_drag(window):
        window.oldPos = None

        def mousePressEvent(event):
            window.oldPos = event.globalPos()

        def mouseMoveEvent(event):
            if window.oldPos:
                delta = event.globalPos() - window.oldPos
                window.move(window.x() + delta.x(), window.y() + delta.y())
                window.oldPos = event.globalPos()

        window.mousePressEvent = mousePressEvent
        window.mouseMoveEvent = mouseMoveEvent




class RizalEDMessageBox:
    def __init__(self):
        self.message_box_stylesheet = """
            QMessageBox {
                background-color: #FFF9E6; 
                color: #4b2e2e; 
                font-family: "Times New Roman", serif;
                border: 2px solid #8b4513; 
                border-radius: 10px;
                padding: 10px;
            }

            QPushButton {
                background-color: #8b4513; 
                color: #ffffff; 
                font-family: "Times New Roman", serif;
                font-size: 12pt;
                border-radius: 5px;
                padding: 5px 10px;
            }

            QPushButton:hover {
                background-color: #a0522d; 
            }
        """ 
        
         





class CustomTooltip(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.ToolTip)
        
        self.setStyleSheet("""
            background-color: #664229;
            color: #E5D3B3;
            border-radius: 20px;  
            font-family: 'Times New Roman', serif;
            font-weight: bold;
        """)

        layout = QVBoxLayout(self)
        self.label = QLabel(text, self)

        self.label.setStyleSheet("""
            font-size: 12px;
            padding: 5px;
        """)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def show_tooltip(self, pos):
        self.move(pos)  
        self.show()

    def hide_tooltip(self):
        self.hide()





global_is_muted = False 

class Main_Menu(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'front.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("") 
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        book_button = self.findChild(QtWidgets.QPushButton, 'bookbutton')
        book_button.clicked.connect(self.play_click_sound)
        book_button.clicked.connect(self.switch_landingpage)

        miultimo = self.findChild(QtWidgets.QPushButton, 'miultimobutton')
        miultimo.clicked.connect(self.play_click_sound)
        miultimo.clicked.connect(self.switch_miultimo)

        miultimo2 = self.findChild(QtWidgets.QPushButton, 'miultimo2button')
        miultimo2.clicked.connect(self.play_click_sound)
        miultimo2.clicked.connect(self.switch_miultimo)

        miultimo3 = self.findChild(QtWidgets.QPushButton, 'miultimo3button')
        miultimo3.clicked.connect(self.play_click_sound)
        miultimo3.clicked.connect(self.switch_miultimo)

        #RIZAL
        self.tooltip_rizal = CustomTooltip("José Rizal", self)
        self.rizal_label = self.findChild(QLabel, 'rizal')
        self.rizal_label.setMouseTracking(True)
        self.rizal_label.enterEvent = self.show_tooltip_rizal
        self.rizal_label.leaveEvent = self.hide_tooltip_rizal
        self.rizal_label.setStyleSheet("QLabel { border: none; }")  

        #TIME
        self.tooltip_time = CustomTooltip(
            "Dr. José Rizal was executed on December 30, 1896, at\n"
            "7:03 a.m., in Bagumbayan (now Rizal Park), Manila.",
            self
        )
        self.time_label = self.findChild(QLabel, 'time')
        self.time_label.setMouseTracking(True)
        self.time_label.enterEvent = self.show_tooltip_time
        self.time_label.leaveEvent = self.hide_tooltip_time
        self.time_label.setStyleSheet("QLabel { border: none; }")  

        # NOLI
        self.tooltip_noli = CustomTooltip(
            "José Rizal's revolutionary novel, Noli Me Tangere, unveiled\n"
            "the injustices of Spanish colonial rule and inspired Filipinos\n"
            "to fight for their rights and freedom.",
            self
        )
        self.noli_label = self.findChild(QLabel, 'noli')  
        self.noli_label.setMouseTracking(True)
        self.noli_label.enterEvent = self.show_tooltip_noli  
        self.noli_label.leaveEvent = self.hide_tooltip_noli  
        self.noli_label.setStyleSheet("QLabel { border: none; }")

        # MI ULTIMO ADIOS BUTTON
        self.tooltip_miultimobutton = CustomTooltip(
            "José Rizal's farewell poem, Mi Último Adiós, written before\n"
            "his execution, reflects his love for the Philippines and his\n"
            "sacrifices for freedom and justice.",
            self
        )
        self.miultimobutton = self.findChild(QPushButton, 'miultimobutton')  
        self.miultimobutton.setMouseTracking(True)
        self.miultimobutton.enterEvent = self.show_tooltip_miultimobutton  
        self.miultimobutton.leaveEvent = self.hide_tooltip_miultimobutton  
        self.miultimobutton.setStyleSheet("QPushButton { border: none; }")
        #2
        self.tooltip_miultimobutton = CustomTooltip(
            "José Rizal's farewell poem, Mi Último Adiós, written before\n"
            "his execution, reflects his love for the Philippines and his\n"
            "sacrifices for freedom and justice.",
            self
        )
        self.miultimobutton = self.findChild(QPushButton, 'miultimo2button')  
        self.miultimobutton.setMouseTracking(True)
        self.miultimobutton.enterEvent = self.show_tooltip_miultimobutton  
        self.miultimobutton.leaveEvent = self.hide_tooltip_miultimobutton  
        self.miultimobutton.setStyleSheet("QPushButton { border: none; }")
        #3
        self.tooltip_miultimobutton = CustomTooltip(
            "José Rizal's farewell poem, Mi Último Adiós, written before\n"
            "his execution, reflects his love for the Philippines and his\n"
            "sacrifices for freedom and justice.",
            self
        )
        self.miultimobutton = self.findChild(QPushButton, 'miultimo3button')  
        self.miultimobutton.setMouseTracking(True)
        self.miultimobutton.enterEvent = self.show_tooltip_miultimobutton  
        self.miultimobutton.leaveEvent = self.hide_tooltip_miultimobutton  
        self.miultimobutton.setStyleSheet("QPushButton { border: none; }")

    #RIZAL
    def show_tooltip_rizal(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_rizal.show_tooltip(tooltip_pos)
        self.rizal_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_rizal(self, event):
        self.rizal_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_rizal.hide_tooltip()

    #TIME
    def show_tooltip_time(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_time.show_tooltip(tooltip_pos)
        self.time_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_time(self, event):
        self.time_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_time.hide_tooltip()

    # NOLI
    def show_tooltip_noli(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_noli.show_tooltip(tooltip_pos)
        self.noli_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

   
    def hide_tooltip_noli(self, event):
        self.noli_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_noli.hide_tooltip()

    #MI ULTIMO
    def show_tooltip_miultimobutton(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_miultimobutton.show_tooltip(tooltip_pos)
        self.miultimobutton.setStyleSheet("QPushButton { border: none; text-decoration: underline; }")

    def hide_tooltip_miultimobutton(self, event):
        self.miultimobutton.setStyleSheet("QPushButton { border: none; }")
        self.tooltip_miultimobutton.hide_tooltip()




    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volumebutton.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volumebutton.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volumebutton.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_miultimo(self):
        self.switch_window(MiUltimoAdios11)

    def switch_landingpage(self):
        self.switch_window(LandingPage)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()






class MiUltimoAdios11(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'miultimo1.1.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        miultimo12 = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        miultimo12.clicked.connect(self.play_click_sound)
        miultimo12.clicked.connect(self.switch_miultimo12)

        exit = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        exit.clicked.connect(self.play_click_sound)
        exit.clicked.connect(self.switch_main_menu)


    def play_click_sound(self):
        BUTTON_SOUND.play()

    def switch_main_menu(self):
        self.switch_window(Main_Menu)

    def switch_miultimo12(self):
        self.switch_window(MiUltimoAdios12)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class MiUltimoAdios12(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'miultimo1.2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        miultimo13 = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        miultimo13.clicked.connect(self.play_click_sound)
        miultimo13.clicked.connect(self.switch_miultimo13)

        miultimo11 = self.findChild(QtWidgets.QPushButton, 'backbutton')
        miultimo11.clicked.connect(self.play_click_sound)
        miultimo11.clicked.connect(self.switch_miultimo11)

        exit = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        exit.clicked.connect(self.play_click_sound)
        exit.clicked.connect(self.switch_main_menu)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def switch_main_menu(self):
        self.switch_window(Main_Menu)

    def switch_miultimo11(self):
        self.switch_window(MiUltimoAdios11)

    def switch_miultimo13(self):
        self.switch_window(MiUltimoAdios13)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

        

class MiUltimoAdios13(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'miultimo1.3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        miultimo11 = self.findChild(QtWidgets.QPushButton, 'backbutton')
        miultimo11.clicked.connect(self.play_click_sound)
        miultimo11.clicked.connect(self.switch_miultimo12)

        exit = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        exit.clicked.connect(self.play_click_sound)
        exit.clicked.connect(self.switch_main_menu)


    def play_click_sound(self):
        BUTTON_SOUND.play()

    def switch_main_menu(self):
        self.switch_window(Main_Menu)

    def switch_miultimo12(self):
        self.switch_window(MiUltimoAdios12)


    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()





class LandingPage(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'landingpage.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 
        
        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("") 
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit) 

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.play_click_sound)
        nextbutton.clicked.connect(self.switch_about)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_main)
        backbutton.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0) 
            self.volumebutton.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png")) 
            self.volumebutton.repaint()  
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)  
            self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volumebutton.repaint() 
            global_is_muted = False

    def switch_about(self):
        self.switch_window(About)

    def switch_main(self):
        self.switch_window(Main_Menu)

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()





class About(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'about.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.play_click_sound)
        backbutton.clicked.connect(self.switch_landingpage)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.play_click_sound)
        nextbutton.clicked.connect(self.switch_table)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volumebutton.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volumebutton.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volumebutton.repaint()
            global_is_muted = False

    def switch_landingpage(self):
        self.switch_window(LandingPage)

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()






class TableofContent(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'tableofcontent.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_about)
        backbutton.clicked.connect(self.play_click_sound)

        prologuebutton = self.findChild(QtWidgets.QPushButton, 'prologuebutton')
        prologuebutton.clicked.connect(self.switch_prologue)
        prologuebutton.clicked.connect(self.play_click_sound)

        epiloguebutton = self.findChild(QtWidgets.QPushButton, 'epiloguebutton')
        epiloguebutton.clicked.connect(self.switch_epilogue)
        epiloguebutton.clicked.connect(self.play_click_sound)

        chapter1button = self.findChild(QtWidgets.QPushButton, 'chapter1button')
        chapter1button.clicked.connect(self.switch_chapter1)
        chapter1button.clicked.connect(self.play_click_sound)

        chapter2button = self.findChild(QtWidgets.QPushButton, 'chapter2button')
        chapter2button.clicked.connect(self.switch_chapter2)
        chapter2button.clicked.connect(self.play_click_sound)

        chapter3button = self.findChild(QtWidgets.QPushButton, 'chapter3button')
        chapter3button.clicked.connect(self.switch_chapter3)
        chapter3button.clicked.connect(self.play_click_sound)

        chapter4button = self.findChild(QtWidgets.QPushButton, 'chapter4button')
        chapter4button.clicked.connect(self.switch_chapter4)
        chapter4button.clicked.connect(self.play_click_sound)

        chapter5button = self.findChild(QtWidgets.QPushButton, 'chapter5button')
        chapter5button.clicked.connect(self.switch_chapter5)
        chapter5button.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_dedication)
        nextbutton.clicked.connect(self.play_click_sound)

        searchbutton = self.findChild(QtWidgets.QPushButton, 'searchbutton')
        searchbutton.clicked.connect(self.switch_search)

        self.search_button = self.findChild(QtWidgets.QPushButton, 'searchbutton')
        self.search_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\search.png"))
        self.search_button.setIconSize(QtCore.QSize(50, 50))
        self.search_button.setText("")
        self.search_button.clicked.connect(self.play_click_sound)


        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volumebutton.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volumebutton.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volumebutton.setIcon(QIcon("C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volumebutton.repaint()
            global_is_muted = False

    def switch_dedication(self):
        self.switch_window(DedicationPage)

    def switch_prologue(self):
        self.switch_window(Prologue)

    def switch_chapter1(self):
        self.switch_window(Chapter1)

    def switch_chapter2(self):
        self.switch_window(Chapter2)

    def switch_chapter3(self):
        self.switch_window(Chapter3)

    def switch_chapter4(self):
        self.switch_window(Chapter4)

    def switch_chapter5(self):
        self.switch_window(Chapter5)

    def switch_epilogue(self):
        self.switch_window(Epilogue)

    def switch_about(self):
        self.switch_window(About)

    def switch_search(self):
        self.switch_window2(SearchApp)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def switch_window2(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass





class SearchApp(QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'search.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.searchbutton.clicked.connect(self.perform_search)

        self.list.itemClicked.connect(self.show_details)

        self.backbutton.clicked.connect(self.close)

        self.data = {
            "Jose Rizal": "Full Name: José Protacio Rizal Mercado y Alonzo Realonda",
            "Calamba": "José Rizal's birthplace, located in Laguna, Philippines.",
            "National Hero": "José Rizal is considered the national hero of the Philippines for his role\n"
            "in inspiring the country's fight for independence through his writings and actions.",
            "1861": "In 1861, José Rizal was born on June 19.",
            "Medicine":"Medicine focuses on the science of diagnosing,\n"
            "treating, and preventing illnesses in the human body",
            "Philosophy":"Philosophy, on the other hand, explores fundamental questions\n"
            "about existence, knowledge, ethics, and reasoning",
            "Nationalism": "Nationalism is the belief in the importance of\n"
            "one's nation, promoting its independence and unity.",
            "Rizal's Mother": "Teodora Alonso Realonda is José Rizal's mother, known for her intelligence\n"
            "and strong influence on his education and values.",
            "Rizal's Father": "Francisco Mercado is José Rizal's father, a prosperous farmer, and\n"
            "a respected member of the Calamba community.",
            "Noli Me Tangere": "A novel by José Rizal that exposes the social injustices\n"
                    "during Spanish colonial rule in the Philippines.",
            "El Filibusterismo": "A novel by José Rizal that exposes the social injustices\n"
                    "during Spanish colonial rule in the Philippines.",
            "Sa Aking Mga Kabata": "At 11 years old, José Rizal wrote his first poem titled\n"
            "Sa Aking Mga Kabata, expressing love for his native\n"
            "language and promoting patriotism.",
            "Maestro Justiniano Aquino Cruz": "José Rizal's third teacher, who taught him\n"
            "the basics of reading and writing in Calamba.",
            "Escuela Pia": "Currently Ateneo Municipal de Manila ",
            "Revolution": "A fight for independence from Spanish rule.",
            "Sedition": "Act of inciting rebellion against authority or government.",
            "Treason": "Crime of betraying one’s country, often by aiding enemies",
            "Rebellion":  "An armed resistance against a government or authority.",
            "Composure": "State of being calm and in control of oneself",
            "Bravery": "Quality of facing danger or challenges with courage.",
            "National": "Freedom of a nation to govern itself without external control.",
            "Philippine Reform Movement": "The Philippine Reform Movement (late 19th century) sought\n"
            "political and social reforms under Spanish rule, led by Ilustrados like José Rizal through\n"
            "works like La Solidaridad.",
            "Spanish Colonial Rule": "Period of Spanish control over the Philippines (1565–1898).",
            "Literature": "Filipino writers, like Rizal, used writing to push for reforms.",
            "Activism": "The Ilustrados led peaceful movements for change.",
            "Philosophy" : "Advocated Enlightenment ideas like liberty and equality.",
            "Social Change": "Focused on equality, education, and ending exploitation.",
            "Liberalism" : "Political ideology promoting individual rights,\n" 
            "democracy, and limited government control.",
            "Expatriates": " Filipinos who lived abroad, often advocating\n"
            "for reform and independence.",
            "Monopoly": "Exclusive control by a single entity or group, often referring to\n"
            "Spanish control over trade and resources in the Philippines.",
            "Spanish Friars" : "Catholic religious leaders who held significant political\n"
            "and social power during Spanish rule.",
            "Justice": "The pursuit of fairness, often linked to the fight against colonial oppression.",
            "Equality": "The belief in equal rights for all, regardless of race or class.",
            "Freedom": "The desire for independence from colonial rule and for basic civil rights.",
            "Independence": "The goal of self-rule and freedom from Spanish colonial control.",
            "Revolution": " Armed struggle against colonial oppression, aiming for independence.",
            "Social Reform": "Efforts to improve societal conditions, advocating for rights, equality, and justice.",
            "Rebellion": "Armed resistance against colonial rule, aiming for independence or change.",
            "Corruption": "Abuse of power for personal gain, often seen in the Spanish colonial government and clergy.",
            "Dapitan": "A town in Mindanao where José Rizal\n"
            "was exiled by the Spanish from 1892 to 1896.",
            "Community Leader": "Rizal became a leader in Dapitan,\n"
            "organizing community projects and improving local life.",
            "Physician": "Rizal practiced medicine in Dapitan,\n"
            "treating patients and providing healthcare to the poor.",
            "Teacher": "Rizal taught local children,\n"
            "emphasizing education and critical thinking.",
            "Scientist": "Rizal conducted scientific studies in fields like biology, anthropology, and engineering.",
            "Farmer": "Rizal engaged in agriculture, developing land and promoting farming techniques in Dapitan.",
            "Botany": "The study of plants, a field that José Rizal explored during his exile in Dapitan.",
            "Zoology": "The study of animals, another area of scientific interest for Rizal during his time in Dapitan.",
            "Reformist": "An individual advocating for gradual change and reform, like Rizal, who sought reforms\n"
            "under Spanish rule rather than revolution.",
            "Katipunan": "A secret revolutionary society founded by Andres Bonifacio to fight for Philippine\n"
            "independence from Spanish rule.",
            "Andres Bonifacio": " Leader of the Katipunan and a key figure in the Philippine Revolution, known for his bravery\n"
            "and advocacy for independence.",
            "Martyr": "A person who suffers or dies for a cause, like José Rizal, whose execution sparked\n"
            "greater resistance against Spanish rule.",
            "Philippine Revolution": "The 1896-1898 uprising against Spanish colonial rule, led by the Katipunan\n"
            "And figures like Bonifacio and Aguinaldo, aiming for independence."
        }

    def perform_search(self):
        self.list.clear()
        
        query = self.searchline.text().lower()
        
        results = {key: value for key, value in self.data.items() if query in key.lower()}
        
        if results:
            for item in results.keys():
                self.list.addItem(QListWidgetItem(item))
        else:
            self.show_no_results_message()

    def show_no_results_message(self):
        custom_message_box = RizalEDMessageBox()
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)  
        message_box.setWindowTitle("No Results")
        message_box.setText("No results found for your search.")
        font = QFont("Times New Roman", 15)  
        message_box.exec_()

    def show_details(self, item):
        custom_message_box = RizalEDMessageBox()
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint) 
        item_name = item.text()

        info = self.data.get(item_name, "No details available.")
        
        message_box.setTextFormat(QtCore.Qt.RichText)
        message_box.setWindowTitle("Details")
        message_box.setText(f"""
        <p style="font-family: 'Times New Roman', serif; font-size: 14pt; color: #4b2e2e;">
            <b>{item_name}:</b>
        </p>
        <p style="font-family: 'Times New Roman', serif; font-size: 12pt; color: #4b2e2e;">
            {info}
        </p>
        """)
        message_box.exec_()





class DedicationPage(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'dedicationpage.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.play_click_sound)
        backbutton.clicked.connect(self.switch_table)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()





class Prologue(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'prologue.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.play_click_sound)
        bmbutton.clicked.connect(self.switch_table)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.play_click_sound)
        nextbutton.clicked.connect(self.switch_chapter1p)
        
        #JOSERIZAL
        self.tooltip = CustomTooltip("Full Name: José Protacio Rizal Mercado y Alonzo Realonda", self)
        self.joserizal_label = self.findChild(QLabel, 'joserizal')
        self.joserizal_label.setMouseTracking(True)
        self.joserizal_label.enterEvent = self.show_tooltip
        self.joserizal_label.leaveEvent = self.hide_tooltip
        self.joserizal_label.setStyleSheet("QLabel { border: none; }")  

        #CALAMBA
        self.tooltip_calamba = CustomTooltip("José Rizal's birthplace, located in Laguna, Philippines.", self)
        self.calamba_label = self.findChild(QLabel, 'calamba')
        self.calamba_label.setMouseTracking(True)
        self.calamba_label.enterEvent = self.show_tooltip_calamba
        self.calamba_label.leaveEvent = self.hide_tooltip_calamba
        self.calamba_label.setStyleSheet("QLabel { border: none; }")  

        #NATIONALHERO
        self.tooltip_nationalhero = CustomTooltip(
        "José Rizal is considered the national hero of the Philippines for his role\n"
        "in inspiring the country's fight for independence through his writings and actions.",
        self
        )
        self.nationalhero_label = self.findChild(QLabel, 'nationalhero')
        self.nationalhero_label.setMouseTracking(True)
        self.nationalhero_label.enterEvent = self.show_tooltip_nationalhero
        self.nationalhero_label.leaveEvent = self.hide_tooltip_nationalhero
        self.nationalhero_label.setStyleSheet("QLabel { border: none; }")  

        #YEAR
        self.tooltip_year = CustomTooltip("In 1861, José Rizal was born on June 19.", self)
        self.year_label = self.findChild(QLabel, 'year')
        self.year_label.setMouseTracking(True)
        self.year_label.enterEvent = self.show_tooltip_year
        self.year_label.leaveEvent = self.hide_tooltip_year
        self.year_label.setStyleSheet("QLabel { border: none; }") 

        #MEDICINE
        self.tooltip_medicine = CustomTooltip(
            "Medicine focuses on the science of diagnosing,\n"
            "treating, and preventing illnesses in the human body",
            self
        )
        self.medicine_label = self.findChild(QLabel, 'medicine')
        self.medicine_label.setMouseTracking(True)
        self.medicine_label.enterEvent = self.show_tooltip_medicine
        self.medicine_label.leaveEvent = self.hide_tooltip_medicine
        self.medicine_label.setStyleSheet("QLabel { border: none; }")

        #PHILOSOPHY
        self.tooltip_philosophy = CustomTooltip(
            "Philosophy, on the other hand, explores fundamental questions\n"
            "about existence, knowledge, ethics, and reasoning",
            self
        )
        self.philosophy_label = self.findChild(QLabel, 'philosophy')
        self.philosophy_label.setMouseTracking(True)
        self.philosophy_label.enterEvent = self.show_tooltip_philosophy
        self.philosophy_label.leaveEvent = self.hide_tooltip_philosophy
        self.philosophy_label.setStyleSheet("QLabel { border: none; }")

        #NATIONALISM
        self.tooltip_nationalism = CustomTooltip(
            "Nationalism is the belief in the importance of\n"
            "one's nation, promoting its independence and unity.",
            self
        )
        self.nationalism_label = self.findChild(QLabel, 'nationalism')
        self.nationalism_label.setMouseTracking(True)
        self.nationalism_label.enterEvent = self.show_tooltip_nationalism
        self.nationalism_label.leaveEvent = self.hide_tooltip_nationalism
        self.nationalism_label.setStyleSheet("QLabel { border: none; }")




    #JOSERIZAL
    def show_tooltip(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip.show_tooltip(tooltip_pos)
        self.joserizal_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip(self, event):
        self.joserizal_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip.hide_tooltip()

    #CALAMBA
    def show_tooltip_calamba(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_calamba.show_tooltip(tooltip_pos)
        self.calamba_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_calamba(self, event):
        self.calamba_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_calamba.hide_tooltip()

    #NATIONALHERO
    def show_tooltip_nationalhero(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_nationalhero.show_tooltip(tooltip_pos)
        self.nationalhero_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_nationalhero(self, event):
        self.nationalhero_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_nationalhero.hide_tooltip()

    #YEAR
    def show_tooltip_year(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_year.show_tooltip(tooltip_pos)
        self.year_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_year(self, event):
        self.year_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_year.hide_tooltip()

     #MEDICINE
    def show_tooltip_medicine(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_medicine.show_tooltip(tooltip_pos)
        self.medicine_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_medicine(self, event):
        self.medicine_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_medicine.hide_tooltip()

    #PHILOSOPHY
    def show_tooltip_philosophy(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_philosophy.show_tooltip(tooltip_pos)
        self.philosophy_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_philosophy(self, event):
        self.philosophy_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_philosophy.hide_tooltip()

    #NATIONALISM
    def show_tooltip_nationalism(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_nationalism.show_tooltip(tooltip_pos)
        self.nationalism_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_nationalism(self, event):
        self.nationalism_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_nationalism.hide_tooltip()


    def play_click_sound(self):
         BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter1p(self):
        self.switch_window(Chapter1)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()






class Chapter1(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter1page.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter1p2)
        nextbutton.clicked.connect(self.play_click_sound)

        #FATHER
        self.tooltip_father = CustomTooltip(
            "José Rizal's father, a prosperous farmer, and\n"
            "a respected member of the Calamba community.",
            self
        )
        self.father_label = self.findChild(QLabel, 'father')
        self.father_label.setMouseTracking(True)
        self.father_label.enterEvent = self.show_tooltip_father
        self.father_label.leaveEvent = self.hide_tooltip_father
        self.father_label.setStyleSheet("QLabel { border: none; }")

        #MOTHER
        self.tooltip_mother = CustomTooltip(
            "José Rizal's mother, known for her intelligence\n"
            "and strong influence on his education and values.",
            self
        )
        self.mother_label = self.findChild(QLabel, 'mother')  
        self.mother_label.setMouseTracking(True)
        self.mother_label.enterEvent = self.show_tooltip_mother  
        self.mother_label.leaveEvent = self.hide_tooltip_mother  
        self.mother_label.setStyleSheet("QLabel { border: none; }")

    #FATHER
    def show_tooltip_father(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_father.show_tooltip(tooltip_pos)
        self.father_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_father(self, event):
        self.father_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_father.hide_tooltip()

    #MOTHER
    def show_tooltip_mother(self, event):  
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_mother.show_tooltip(tooltip_pos) 
        self.mother_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")  

    def hide_tooltip_mother(self, event):  
        self.mother_label.setStyleSheet("QLabel { border: none; }")  
        self.tooltip_mother.hide_tooltip() 

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter1p2(self):
        self.switch_window(Chapter1P2)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class Chapter1P2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter1page2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter1)
        backbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter1p3)
        nextbutton.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter1(self):
        self.switch_window(Chapter1)

    def switch_chapter1p3(self):
        self.switch_window(Chapter1P3)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class Chapter1P3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter1page3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter1p2)
        backbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter2)
        nextbutton.clicked.connect(self.play_click_sound)


        #NOLIME
        self.tooltip_nolime = CustomTooltip(
                    "A novel by José Rizal that exposes the social injustices\n"
                    "during Spanish colonial rule in the Philippines.",
                    self
                )
                
        self.tooltip_tangere = CustomTooltip(
                    "A novel by José Rizal that exposes the social injustices\n"
                    "during Spanish colonial rule in the Philippines.",
                    self
                )

        self.nolime_label = self.findChild(QLabel, 'noli') 
        self.nolime_label.setMouseTracking(True)
        self.nolime_label.enterEvent = self.show_tooltip_nolime
        self.nolime_label.leaveEvent = self.hide_tooltip_nolime
        self.nolime_label.setStyleSheet("QLabel { border: none; }")

        self.tangere_label = self.findChild(QLabel, 'tangere')  
        self.tangere_label.setMouseTracking(True)
        self.tangere_label.enterEvent = self.show_tooltip_tangere
        self.tangere_label.leaveEvent = self.hide_tooltip_tangere
        self.tangere_label.setStyleSheet("QLabel { border: none; }")

    #ELFILI
        self.tooltip_elfili = CustomTooltip(
            "José Rizal's sequel to Noli Me Tangere, highlighting the\n"
            "struggle for reform and revolution against Spanish oppression.",
            self
        )
        self.elfili_label = self.findChild(QLabel, 'elfili')  
        self.elfili_label.setMouseTracking(True)
        self.elfili_label.enterEvent = self.show_tooltip_elfili 
        self.elfili_label.leaveEvent = self.hide_tooltip_elfili 
        self.elfili_label.setStyleSheet("QLabel { border: none; }")

    #ELFILI
    def show_tooltip_elfili(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_elfili.show_tooltip(tooltip_pos)
        self.elfili_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    #ELFILI
    def hide_tooltip_elfili(self, event):
        self.elfili_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_elfili.hide_tooltip()

    #NOLI
    def show_tooltip(self, event, label, tooltip):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        tooltip.show_tooltip(tooltip_pos)
        label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip(self, event, label, tooltip):
        label.setStyleSheet("QLabel { border: none; }")
        tooltip.hide_tooltip()

    def show_tooltip_nolime(self, event):
        self.show_tooltip(event, self.nolime_label, self.tooltip_nolime)

    def hide_tooltip_nolime(self, event):
        self.hide_tooltip(event, self.nolime_label, self.tooltip_nolime)

    def show_tooltip_tangere(self, event):
        self.show_tooltip(event, self.tangere_label, self.tooltip_tangere)

    def hide_tooltip_tangere(self, event):
        self.hide_tooltip(event, self.tangere_label, self.tooltip_tangere)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter1p2(self):
        self.switch_window(Chapter1P2)

    def switch_chapter2(self):
        self.switch_window(Chapter2) 

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()




class Chapter2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter2page.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("")

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter2p2)
        nextbutton.clicked.connect(self.play_click_sound)


        # ELEVEN
        self.tooltip_eleven = CustomTooltip(
            "At 11 years old, José Rizal wrote his first poem titled\n"
            "Sa Aking Mga Kabata, expressing love for his native\n"
            "language and promoting patriotism.",
            self
        )
        self.eleven_label = self.findChild(QLabel, 'eleven')  
        self.eleven_label.setMouseTracking(True)
        self.eleven_label.enterEvent = self.show_tooltip_eleven 
        self.eleven_label.leaveEvent = self.hide_tooltip_eleven
        self.eleven_label.setStyleSheet("QLabel { border: none; }")

        # CRUZ
        self.tooltip_cruz = CustomTooltip(
            "José Rizal's third teacher, who taught him\n"
            "the basics of reading and writing in Calamba.",
            self
        )
        self.cruz_label = self.findChild(QLabel, 'cruz')  
        self.cruz_label.setMouseTracking(True)
        self.cruz_label.enterEvent = self.show_tooltip_cruz  
        self.cruz_label.leaveEvent = self.hide_tooltip_cruz 
        self.cruz_label.setStyleSheet("QLabel { border: none; }")

        # CRUZ2
        self.tooltip_cruz = CustomTooltip(
            "José Rizal's first teacher, who taught him\n"
            "the basics of reading and writing in Calamba.",
            self
        )
        self.cruz2_label = self.findChild(QLabel, 'cruz2')  
        self.cruz2_label.setMouseTracking(True)
        self.cruz2_label.enterEvent = self.show_tooltip_cruz
        self.cruz2_label.leaveEvent = self.hide_tooltip_cruz 
        self.cruz2_label.setStyleSheet("QLabel { border: none; }")

        # ESCUELA
        self.tooltip_escuela = CustomTooltip(
            "formerly known as Escuela Pia.",
            self
        )
        self.escuela_label = self.findChild(QLabel, 'escuela')  
        self.escuela_label.setMouseTracking(True)
        self.escuela_label.enterEvent = self.show_tooltip_escuela  
        self.escuela_label.leaveEvent = self.hide_tooltip_escuela
        self.escuela_label.setStyleSheet("QLabel { border: none; }")

        # ESCUELA2
        self.tooltip_escuela = CustomTooltip(
            "formerly known as Escuela Pia.",
            self
        )
        self.escuela2_label = self.findChild(QLabel, 'escuela2')  
        self.escuela2_label.setMouseTracking(True)
        self.escuela2_label.enterEvent = self.show_tooltip_escuela  
        self.escuela2_label.leaveEvent = self.hide_tooltip_escuela
        self.escuela2_label.setStyleSheet("QLabel { border: none; }")

    
    #CRUZ_2
    def show_tooltip_cruz(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_cruz.show_tooltip(tooltip_pos)
        self.cruz_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_cruz(self, event):
        self.cruz_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_cruz.hide_tooltip()

    #ESCUELA_2
    def show_tooltip_escuela(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_escuela.show_tooltip(tooltip_pos)
        self.escuela_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_escuela(self, event):
        self.escuela_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_escuela.hide_tooltip()

    # ELEVEN
    def show_tooltip_eleven(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_eleven.show_tooltip(tooltip_pos)
        self.eleven_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_eleven(self, event):
        self.eleven_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_eleven.hide_tooltip()

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter2p2(self):
        self.switch_window(Chapter2P2)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

        
class Chapter2P2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter2page2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter1)
        backbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter2p3)
        nextbutton.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter1(self):
        self.switch_window(Chapter2)

    def switch_chapter2p3(self):
        self.switch_window(Chapter2P3)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class Chapter2P3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter2page3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png"))
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter1p2)

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter2)
        nextbutton.clicked.connect(self.play_click_sound)


    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter1p2(self):
        self.switch_window(Chapter1P2)

    def switch_chapter2(self):
        self.switch_window(Chapter3) 

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()





class Chapter3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter3page.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.initialize_tooltips()

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter3p2)
        nextbutton.clicked.connect(self.play_click_sound)


    def initialize_tooltips(self):
        #PHILLIPINE REFORM MOVEMENT
        self.tooltip_reform = CustomTooltip(
            "The Philippine Reform Movement (late 19th century) sought political and social reforms\n"
            "under Spanish rule, led by Ilustrados like José Rizal through works like La Solidaridad.",
            self
        )

        self.reform_label = self.findChild(QLabel, 'reform')
        self.reform_label.setMouseTracking(True)
        self.reform_label.enterEvent = self.show_tooltip_reform
        self.reform_label.leaveEvent = self.hide_tooltip_reform
        self.reform_label.setStyleSheet("QLabel { border: none; }")

        #SPANISH COLONIAL RULE
        self.tooltip_colonial = CustomTooltip(
            "Period of Spanish control over the Philippines (1565–1898).",
            self
        )
        self.colonial_label = self.findChild(QLabel, 'colonial')  
        self.colonial_label.setMouseTracking(True)
        self.colonial_label.enterEvent = self.show_tooltip_colonial
        self.colonial_label.leaveEvent = self.hide_tooltip_colonial
        self.colonial_label.setStyleSheet("QLabel { border: none; }")

        #LITERATURE
        self.tooltip_literature= CustomTooltip(
            "Filipino writers, like Rizal, used writing to push for reforms.",self
        )

        self.literature_label = self.findChild(QLabel, 'literature')
        self.literature_label.setMouseTracking(True)
        self.literature_label.enterEvent = self.show_tooltip_literature
        self.literature_label.leaveEvent = self.hide_tooltip_literature
        self.literature_label.setStyleSheet("QLabel { border: none; }")

        #ACTIVISM
        self.tooltip_activism= CustomTooltip(
            "The Ilustrados led peaceful movements for change.",self
        )

        self.activism_label = self.findChild(QLabel, 'activism')
        self.activism_label.setMouseTracking(True)
        self.activism_label.enterEvent = self.show_tooltip_activism
        self.activism_label.leaveEvent = self.hide_tooltip_activism
        self.activism_label.setStyleSheet("QLabel { border: none; }")

        #PHILOSPHY
        self.tooltip_philosophy= CustomTooltip(
            "Advocated Enlightenment ideas like liberty and equality.",self
        )

        self.philosophy_label = self.findChild(QLabel, 'philosophy')
        self.philosophy_label.setMouseTracking(True)
        self.philosophy_label.enterEvent = self.show_tooltip_philosophy
        self.philosophy_label.leaveEvent = self.hide_tooltip_philosophy
        self.philosophy_label.setStyleSheet("QLabel { border: none; }")

        #SOCIAL CHANGE
        self.tooltip_socchange= CustomTooltip(
            "Focused on equality, education, and ending exploitation.",self
        )

        self.socchange_label = self.findChild(QLabel, 'socchange')
        self.socchange_label.setMouseTracking(True)
        self.socchange_label.enterEvent = self.show_tooltip_socchange
        self.socchange_label.leaveEvent = self.hide_tooltip_socchange
        self.socchange_label.setStyleSheet("QLabel { border: none; }")

    #PHILIPPINE REFORM MOVEMENT
    def show_tooltip_reform(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_reform.show_tooltip(tooltip_pos)
        self.reform_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_reform(self, event):
        self.reform_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_reform.hide_tooltip()

    #SPANISH COLONIAL RULE
    def show_tooltip_colonial(self, event):  
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_colonial.show_tooltip(tooltip_pos) 
        self.colonial_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")  

    def hide_tooltip_colonial(self, event):  
        self.colonial_label.setStyleSheet("QLabel { border: none; }")  
        self.tooltip_colonial.hide_tooltip()

    #LITERATURE
    def show_tooltip_literature(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_literature.show_tooltip(tooltip_pos) 
        self.literature_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_literature(self, event):
        self.literature_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_literature.hide_tooltip()

    #ACTIVISM
    def show_tooltip_activism(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_activism.show_tooltip(tooltip_pos) 
        self.activism_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_activism(self, event):
        self.activism_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_activism.hide_tooltip()

    #PHILOSOPHY
    def show_tooltip_philosophy(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_philosophy.show_tooltip(tooltip_pos) 
        self.philosophy_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_philosophy(self, event):
        self.philosophy_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_philosophy.hide_tooltip()

    #SOCIAL CHANGE
    def show_tooltip_socchange(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_socchange.show_tooltip(tooltip_pos) 
        self.socchange_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_socchange(self, event):
        self.socchange_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_socchange.hide_tooltip()

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter3p2(self):
        self.switch_window(Chapter3P2)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()







        
class Chapter3P2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter3page2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.initialize_tooltips()

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("")  

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter3)
        backbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter3p3)
        nextbutton.clicked.connect(self.play_click_sound)


    def initialize_tooltips(self):

        #LIBERALISM
        self.tooltip_l = CustomTooltip(
            " Political ideology promoting individual rights, democracy,\n"
            "and limited government control.",
            self
        )

        self.l_label = self.findChild(QLabel, 'l')
        self.l_label.setMouseTracking(True)
        self.l_label.enterEvent = self.show_tooltip_l
        self.l_label.leaveEvent = self.hide_tooltip_l
        self.l_label.setStyleSheet("QLabel { border: none; }")

        #Expatriates
        self.tooltip_e = CustomTooltip(
            "Filipinos who lived abroad, often advocating for reform and independence.",
            self
        )
        self.e_label = self.findChild(QLabel, 'e')  
        self.e_label.setMouseTracking(True)
        self.e_label.enterEvent = self.show_tooltip_e
        self.e_label.leaveEvent = self.hide_tooltip_e
        self.e_label.setStyleSheet("QLabel { border: none; }")

        #MONOPOLY
        self.tooltip_m= CustomTooltip(
            "Exclusive control by a single entity or group, often referring to\n"
            "Spanish control over trade and resources in the Philippines.",self
        )

        self.m_label = self.findChild(QLabel, 'm')
        self.m_label.setMouseTracking(True)
        self.m_label.enterEvent = self.show_tooltip_m
        self.m_label.leaveEvent = self.hide_tooltip_m
        self.m_label.setStyleSheet("QLabel { border: none; }")

        #SPANISH FRIARS
        self.tooltip_friars= CustomTooltip(
            "Catholic religious leaders who held significant political\n"
            "and social power during Spanish rule.",self
        )

        self.friars_label = self.findChild(QLabel, 'friars')
        self.friars_label.setMouseTracking(True)
        self.friars_label.enterEvent = self.show_tooltip_friars
        self.friars_label.leaveEvent = self.hide_tooltip_friars
        self.friars_label.setStyleSheet("QLabel { border: none; }")

        #JUSTICE
        self.tooltip_justice= CustomTooltip(
            "The pursuit of fairness, often linked to the fight against colonial oppression.",self
        )

        self.justice_label = self.findChild(QLabel, 'justice')
        self.justice_label.setMouseTracking(True)
        self.justice_label.enterEvent = self.show_tooltip_justice
        self.justice_label.leaveEvent = self.hide_tooltip_justice
        self.justice_label.setStyleSheet("QLabel { border: none; }")

        #EQUALITY
        self.tooltip_equality= CustomTooltip(
            "The belief in equal rights for all, regardless of race or class.",self
        )

        self.equality_label = self.findChild(QLabel, 'equality')
        self.equality_label.setMouseTracking(True)
        self.equality_label.enterEvent = self.show_tooltip_equality
        self.equality_label.leaveEvent = self.hide_tooltip_equality
        self.equality_label.setStyleSheet("QLabel { border: none; }")

        #FREEDOM
        self.tooltip_freedom= CustomTooltip(
            "The desire for independence from colonial rule and for basic civil rights.",self
        )

        self.freedom_label = self.findChild(QLabel, 'freedom')
        self.freedom_label.setMouseTracking(True)
        self.freedom_label.enterEvent = self.show_tooltip_freedom
        self.freedom_label.leaveEvent = self.hide_tooltip_freedom
        self.freedom_label.setStyleSheet("QLabel { border: none; }")

        #INDEPENDENCE
        self.tooltip_i= CustomTooltip(
            "The goal of self-rule and freedom from Spanish colonial control.",self
        )

        self.i_label = self.findChild(QLabel, 'i')
        self.i_label.setMouseTracking(True)
        self.i_label.enterEvent = self.show_tooltip_i
        self.i_label.leaveEvent = self.hide_tooltip_i
        self.i_label.setStyleSheet("QLabel { border: none; }")

        #REVOLUTION
        self.tooltip_r= CustomTooltip(
            "Armed struggle against colonial oppression, aiming for independence",self
        )

        self.r_label = self.findChild(QLabel, 'r')
        self.r_label.setMouseTracking(True)
        self.r_label.enterEvent = self.show_tooltip_r
        self.r_label.leaveEvent = self.hide_tooltip_r
        self.r_label.setStyleSheet("QLabel { border: none; }")






    #LIBERALISM
    def show_tooltip_l(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_l.show_tooltip(tooltip_pos)
        self.l_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_l(self, event):
        self.l_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_l.hide_tooltip()

    #EXPATRIATES
    def show_tooltip_e(self, event):  
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_e.show_tooltip(tooltip_pos) 
        self.e_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")  

    def hide_tooltip_e(self, event):  
        self.e_label.setStyleSheet("QLabel { border: none; }")  
        self.tooltip_e.hide_tooltip()

    #MONOPOLY
    def show_tooltip_m(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_m.show_tooltip(tooltip_pos) 
        self.m_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_m(self, event):
        self.m_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_m.hide_tooltip()

    #SPANISH FRIARS
    def show_tooltip_friars(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_friars.show_tooltip(tooltip_pos) 
        self.friars_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_friars(self, event):
        self.friars_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_friars.hide_tooltip()

    #JUSTICE
    def show_tooltip_justice(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_justice.show_tooltip(tooltip_pos) 
        self.justice_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_justice(self, event):
        self.justice_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_justice.hide_tooltip()

    #EQUALITY
    def show_tooltip_equality(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_equality.show_tooltip(tooltip_pos) 
        self.equality_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_equality(self, event):
        self.equality_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_equality.hide_tooltip()

    #FREEDOM
    def show_tooltip_freedom(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_freedom.show_tooltip(tooltip_pos) 
        self.freedom_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_freedom(self, event):
        self.freedom_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_freedom.hide_tooltip()

    #INDEPENDENCE
    def show_tooltip_i(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_i.show_tooltip(tooltip_pos) 
        self.i_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_i(self, event):
        self.i_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_i.hide_tooltip()

    #REVOLUTION
    def show_tooltip_r(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_r.show_tooltip(tooltip_pos) 
        self.r_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_r(self, event):
        self.r_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_r.hide_tooltip()

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter3(self):
        self.switch_window(Chapter3)

    def switch_chapter3p3(self):
        self.switch_window(Chapter3P3)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class Chapter3P3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter3page3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.initialize_tooltips()

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter3p2)
        backbutton.clicked.connect(self.play_click_sound)

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter4)
        nextbutton.clicked.connect(self.play_click_sound)


    def initialize_tooltips(self):

        #SOCIAL REFORM
        self.tooltip_social = CustomTooltip(
            "Efforts to improve societal conditions, advocating for rights, equality, and justice.",
            self
        )

        self.social_label = self.findChild(QLabel, 'social')
        self.social_label.setMouseTracking(True)
        self.social_label.enterEvent = self.show_tooltip_social
        self.social_label.leaveEvent = self.hide_tooltip_social
        self.social_label.setStyleSheet("QLabel { border: none; }")

        #REBELLION
        self.tooltip_rebel = CustomTooltip(
            "Armed resistance against colonial rule, aiming for independence or change.",
            self
        )
        self.rebel_label = self.findChild(QLabel, 'rebel')  
        self.rebel_label.setMouseTracking(True)
        self.rebel_label.enterEvent = self.show_tooltip_rebel
        self.rebel_label.leaveEvent = self.hide_tooltip_rebel
        self.rebel_label.setStyleSheet("QLabel { border: none; }")

        #CORRUPTION
        self.tooltip_corruption= CustomTooltip(
            "Abuse of power for personal gain, often seen in the\n"
            "Spanish colonial government and clergy.",self
        )

        self.corruption_label = self.findChild(QLabel, 'corruption')
        self.corruption_label.setMouseTracking(True)
        self.corruption_label.enterEvent = self.show_tooltip_corruption
        self.corruption_label.leaveEvent = self.hide_tooltip_corruption
        self.corruption_label.setStyleSheet("QLabel { border: none; }")



        #SOCIAL REFORM
    def show_tooltip_social(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_social.show_tooltip(tooltip_pos) 
        self.social_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_social(self, event):
        self.social_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_social.hide_tooltip()

    #REBELLION
    def show_tooltip_rebel(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_rebel.show_tooltip(tooltip_pos) 
        self.rebel_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_rebel(self, event):
        self.rebel_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_rebel.hide_tooltip()

    #CORRUPTION
    def show_tooltip_corruption(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_corruption.show_tooltip(tooltip_pos) 
        self.corruption_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_corruption(self, event):
        self.corruption_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_corruption.hide_tooltip()

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter3p2(self):
        self.switch_window(Chapter3P2)

    def switch_chapter4(self):
        self.switch_window(Chapter4) 

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()





class Chapter4(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter4page.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.initialize_tooltips()

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter4p2)
        nextbutton.clicked.connect(self.play_click_sound)


    def initialize_tooltips(self):
        # DAPITAN
        self.tooltip_dapitan = CustomTooltip(
            "A town in Mindanao where José Rizal was exiled\n"
            "by the Spanish from 1892 to 1896.",
            self
        )

        self.dapitan_label = self.findChild(QLabel, 'dapitan')
        self.dapitan_label.setMouseTracking(True)
        self.dapitan_label.enterEvent = self.show_tooltip_dapitan
        self.dapitan_label.leaveEvent = self.hide_tooltip_dapitan
        self.dapitan_label.setStyleSheet("QLabel { border: none; }")

        # COMLEADER
        self.tooltip_comleader = CustomTooltip(
            "Rizal became a leader in Dapitan, organizing\n"
            "community projects and improving local life.",
            self
        )
        self.comleader_label = self.findChild(QLabel, 'comleader')  
        self.comleader_label.setMouseTracking(True)
        self.comleader_label.enterEvent = self.show_tooltip_comleader
        self.comleader_label.leaveEvent = self.hide_tooltip_comleader
        self.comleader_label.setStyleSheet("QLabel { border: none; }")

        # PHYSICIAN
        self.tooltip_physician= CustomTooltip(
            "Rizal practiced medicine in Dapitan, treating patients\n"
            "and providing healthcare to the poor.",self
        )

        self.physician_label = self.findChild(QLabel, 'physician')
        self.physician_label.setMouseTracking(True)
        self.physician_label.enterEvent = self.show_tooltip_physician
        self.physician_label.leaveEvent = self.hide_tooltip_physician
        self.physician_label.setStyleSheet("QLabel { border: none; }")

        # TEACHER
        self.tooltip_teacher= CustomTooltip(
            "Rizal taught local children, emphasizing education\n"
            "and critical thinking.",self
        )

        self.teacher_label = self.findChild(QLabel, 'teacher')
        self.teacher_label.setMouseTracking(True)
        self.teacher_label.enterEvent = self.show_tooltip_teacher
        self.teacher_label.leaveEvent = self.hide_tooltip_teacher
        self.teacher_label.setStyleSheet("QLabel { border: none; }")

        # SCIENTIST
        self.tooltip_scientist= CustomTooltip(
            "Rizal engaged in agriculture, developing land\n"
            "and promoting farming techniques in Dapitan.",self
        )

        self.scientist_label = self.findChild(QLabel, 'scientist')
        self.scientist_label.setMouseTracking(True)
        self.scientist_label.enterEvent = self.show_tooltip_scientist
        self.scientist_label.leaveEvent = self.hide_tooltip_scientist
        self.scientist_label.setStyleSheet("QLabel { border: none; }")

        # FARMER
        self.tooltip_farmer = CustomTooltip(
            "Rizal conducted scientific studies in fields\n"
            "like biology, anthropology, and engineering.",self
        )

        self.farmer_label = self.findChild(QLabel, 'farmer')  
        self.farmer_label.setMouseTracking(True)
        self.farmer_label.enterEvent = self.show_tooltip_farmer  
        self.farmer_label.leaveEvent = self.hide_tooltip_farmer
        self.farmer_label.setStyleSheet("QLabel { border: none; }")








    # DAPITAN
    def show_tooltip_dapitan(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_dapitan.show_tooltip(tooltip_pos)
        self.dapitan_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_dapitan(self, event):
        self.dapitan_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_dapitan.hide_tooltip()

    # COMLEADER
    def show_tooltip_comleader(self, event):  
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_comleader.show_tooltip(tooltip_pos) 
        self.comleader_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")  

    def hide_tooltip_comleader(self, event):  
        self.comleader_label.setStyleSheet("QLabel { border: none; }")  
        self.tooltip_comleader.hide_tooltip()

    # PHYSICIAN
    def show_tooltip_physician(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_physician.show_tooltip(tooltip_pos) 
        self.physician_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_physician(self, event):
        self.physician_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_physician.hide_tooltip()

    # TEACHER
    def show_tooltip_teacher(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_teacher.show_tooltip(tooltip_pos) 
        self.teacher_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_teacher(self, event):
        self.teacher_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_teacher.hide_tooltip()

    # SCIENTIST
    def show_tooltip_scientist(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_scientist.show_tooltip(tooltip_pos) 
        self.scientist_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_scientist(self, event):
        self.scientist_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_scientist.hide_tooltip()

    # FARMER
    def show_tooltip_farmer(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_farmer.show_tooltip(tooltip_pos)
        self.farmer_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_farmer(self, event):
        self.farmer_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_farmer.hide_tooltip()

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter4p2(self):
        self.switch_window(Chapter4P2)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class Chapter4P2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter4page2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.initialize_tooltips()

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.settings_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.settings_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.settings_button.setIconSize(QtCore.QSize(50, 50))  
        self.settings_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter4)
        backbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter5)
        nextbutton.clicked.connect(self.play_click_sound)


    def initialize_tooltips(self):

        #BOTANY
        self.tooltip_botany = CustomTooltip(
            "The study of plants, a field that José Rizal\n"
            "explored during his exile in Dapitan.",
            self
        )

        self.botany_label = self.findChild(QLabel, 'botany')
        self.botany_label.setMouseTracking(True)
        self.botany_label.enterEvent = self.show_tooltip_botany
        self.botany_label.leaveEvent = self.hide_tooltip_botany
        self.botany_label.setStyleSheet("QLabel { border: none; }")

        #ZOOLOGY
        self.tooltip_zoology = CustomTooltip(
            "The study of animals, another area of scientific interest\n"
            "for Rizal during his time in Dapitan.",
            self
        )
        self.zoology_label = self.findChild(QLabel, 'zoology')  
        self.zoology_label.setMouseTracking(True)
        self.zoology_label.enterEvent = self.show_tooltip_zoology
        self.zoology_label.leaveEvent = self.hide_tooltip_zoology
        self.zoology_label.setStyleSheet("QLabel { border: none; }")

        #REFORMIST
        self.tooltip_reformist= CustomTooltip(
            " An individual advocating for gradual change and reform,\n"
            "like Rizal, who sought reforms under Spanish rule rather than revolution.",self
        )

        self.reformist_label = self.findChild(QLabel, 'reformist')
        self.reformist_label.setMouseTracking(True)
        self.reformist_label.enterEvent = self.show_tooltip_reformist
        self.reformist_label.leaveEvent = self.hide_tooltip_reformist
        self.reformist_label.setStyleSheet("QLabel { border: none; }")

        #KATIPUNAN
        self.tooltip_katipunan= CustomTooltip(
            " A secret revolutionary society founded by Andres Bonifacio\n"
            "to fight for Philippine independence from Spanish rule.",self
        )

        self.katipunan_label = self.findChild(QLabel, 'katipunan')
        self.katipunan_label.setMouseTracking(True)
        self.katipunan_label.enterEvent = self.show_tooltip_katipunan
        self.katipunan_label.leaveEvent = self.hide_tooltip_katipunan
        self.katipunan_label.setStyleSheet("QLabel { border: none; }")

        #ANDRES BONIFACIO
        self.tooltip_andresb= CustomTooltip(
            "Leader of the Katipunan and a key figure in the Philippine Revolution,\n"
            "known for his bravery and advocacy for independence.",self
        )

        self.andresb_label = self.findChild(QLabel, 'andresb')
        self.andresb_label.setMouseTracking(True)
        self.andresb_label.enterEvent = self.show_tooltip_andresb
        self.andresb_label.leaveEvent = self.hide_tooltip_andresb
        self.andresb_label.setStyleSheet("QLabel { border: none; }")

        #MARTYR
        self.tooltip_martyr= CustomTooltip(
            "A person who suffers or dies for a cause, like José Rizal,\n"
            "whose execution sparked greater resistance against Spanish rule.",self
        )

        self.martyr_label = self.findChild(QLabel, 'martyr')
        self.martyr_label.setMouseTracking(True)
        self.martyr_label.enterEvent = self.show_tooltip_martyr
        self.martyr_label.leaveEvent = self.hide_tooltip_martyr
        self.martyr_label.setStyleSheet("QLabel { border: none; }")

        #PHILIPPINE REVOLUTION
        self.tooltip_ph_rev= CustomTooltip(
            "The 1896-1898 uprising against Spanish colonial rule, led by the Katipunan and\n"
            "figures like Bonifacio and Aguinaldo, aiming for independence.",self
        )

        self.ph_rev_label = self.findChild(QLabel, 'ph_rev')
        self.ph_rev_label.setMouseTracking(True)
        self.ph_rev_label.enterEvent = self.show_tooltip_ph_rev
        self.ph_rev_label.leaveEvent = self.hide_tooltip_ph_rev
        self.ph_rev_label.setStyleSheet("QLabel { border: none; }")



        #BOTANY
    def show_tooltip_botany(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_botany.show_tooltip(tooltip_pos)
        self.botany_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_botany(self, event):
        self.botany_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_botany.hide_tooltip()

    #ZOOLOGY
    def show_tooltip_zoology(self, event):  
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_zoology.show_tooltip(tooltip_pos) 
        self.zoology_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")  

    def hide_tooltip_zoology(self, event):  
        self.zoology_label.setStyleSheet("QLabel { border: none; }")  
        self.tooltip_zoology.hide_tooltip()

    #REFORMIST
    def show_tooltip_reformist(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_reformist.show_tooltip(tooltip_pos) 
        self.reformist_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_reformist(self, event):
        self.reformist_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_reformist.hide_tooltip()

    #KATIPUNAN
    def show_tooltip_katipunan(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_katipunan.show_tooltip(tooltip_pos) 
        self.katipunan_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_katipunan(self, event):
        self.katipunan_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_katipunan.hide_tooltip()

    #ANDRES BONIFACIO
    def show_tooltip_andresb(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_andresb.show_tooltip(tooltip_pos) 
        self.andresb_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_andresb(self, event):
        self.andresb_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_andresb.hide_tooltip()

    #MARTYR
    def show_tooltip_martyr(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_martyr.show_tooltip(tooltip_pos) 
        self.martyr_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_martyr(self, event):
        self.martyr_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_martyr.hide_tooltip()

    #PHILLIPINE REVOLUTION
    def show_tooltip_ph_rev(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_ph_rev.show_tooltip(tooltip_pos) 
        self.ph_rev_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_ph_rev(self, event):
        self.ph_rev_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_ph_rev.hide_tooltip()


    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter4(self):
        self.switch_window(Chapter4)

    def switch_chapter5(self):
        self.switch_window(Chapter5)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()




class Chapter5(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter5page.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r'MIDTERM_PROJECT/reso/mute.png'))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter5p2)
        nextbutton.clicked.connect(self.play_click_sound)


        # KATIPUNAN
        self.tooltip_katipunan = CustomTooltip(
            "A secret revolutionary society in 1892 aimed at\n"
            "gaining Philippine independence from Spanish rule.\n"
            "José Rizal was not a member but inspired but ins-\n"
            "pired the movement through his writings.",
            self
        )
        self.katipunan_label = self.findChild(QLabel, 'katipunan')  
        self.katipunan_label.setMouseTracking(True)
        self.katipunan_label.enterEvent = self.show_tooltip_katipunan  
        self.katipunan_label.leaveEvent = self.hide_tooltip_katipunan
        self.katipunan_label.setStyleSheet("QLabel { border: none; }")

        # ANDRES
        self.tooltip_andres = CustomTooltip(
            "Andres Bonifacio was the founder of the Katipunan\n"
            "and a key figure in the Philippine Revolution.",
            self
        )
        self.andres_label = self.findChild(QLabel, 'andres')  
        self.andres_label.setMouseTracking(True)
        self.andres_label.enterEvent = self.show_tooltip_andres  
        self.andres_label.leaveEvent = self.hide_tooltip_andres
        self.andres_label.setStyleSheet("QLabel { border: none; }")

    #KATIPUNAN
    def show_tooltip_katipunan(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_katipunan.show_tooltip(tooltip_pos)
        self.katipunan_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_katipunan(self, event):
        self.katipunan_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_katipunan.hide_tooltip()

    # ANDRES
    def show_tooltip_andres(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_andres.show_tooltip(tooltip_pos)
        self.andres_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_andres(self, event):
        self.andres_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_andres.hide_tooltip()

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter5p2(self):
        self.switch_window(Chapter5P2)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class Chapter5P2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter5page2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter5)
        backbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_chapter5p3)
        nextbutton.clicked.connect(self.play_click_sound)


        # REVOLUTION
        self.tooltip_revolution = CustomTooltip(
            "A fight for independence from Spanish rule.",
            self
        )
        self.revolution_label = self.findChild(QLabel, 'revolution')  
        self.revolution_label.setMouseTracking(True)
        self.revolution_label.enterEvent = self.show_tooltip_revolution  
        self.revolution_label.leaveEvent = self.hide_tooltip_revolution
        self.revolution_label.setStyleSheet("QLabel { border: none; }")

        # SEDITION
        self.tooltip_sedition = CustomTooltip(
            "Act of inciting rebellion against authority or government.",
            self
        )
        self.sedition_label = self.findChild(QLabel, 'sedition')  
        self.sedition_label.setMouseTracking(True)
        self.sedition_label.enterEvent = self.show_tooltip_sedition  
        self.sedition_label.leaveEvent = self.hide_tooltip_sedition
        self.sedition_label.setStyleSheet("QLabel { border: none; }")

        # TREASON
        self.tooltip_treason = CustomTooltip(
            "Crime of betraying one’s country, often by aiding enemies",
            self
        )
        self.treason_label = self.findChild(QLabel, 'treason')  
        self.treason_label.setMouseTracking(True)
        self.treason_label.enterEvent = self.show_tooltip_treason  
        self.treason_label.leaveEvent = self.hide_tooltip_treason
        self.treason_label.setStyleSheet("QLabel { border: none; }")

        # REBELLION
        self.tooltip_rebellion = CustomTooltip(
            "An armed resistance against a government or authority.",
            self
        )
        self.rebellion_label = self.findChild(QLabel, 'rebellion')  
        self.rebellion_label.setMouseTracking(True)
        self.rebellion_label.enterEvent = self.show_tooltip_rebellion  
        self.rebellion_label.leaveEvent = self.hide_tooltip_rebellion
        self.rebellion_label.setStyleSheet("QLabel { border: none; }")

        # COMPOSURE
        self.tooltip_composure = CustomTooltip(
            "State of being calm and in control of oneself",
            self
        )
        self.composure_label = self.findChild(QLabel, 'composure')  
        self.composure_label.setMouseTracking(True)
        self.composure_label.enterEvent = self.show_tooltip_composure  
        self.composure_label.leaveEvent = self.hide_tooltip_composure
        self.composure_label.setStyleSheet("QLabel { border: none; }")

        # BRAVERY
        self.tooltip_bravery = CustomTooltip(
            "Quality of facing danger or challenges with courage.",
            self
        )
        self.bravery_label = self.findChild(QLabel, 'bravery')  
        self.bravery_label.setMouseTracking(True)
        self.bravery_label.enterEvent = self.show_tooltip_bravery  
        self.bravery_label.leaveEvent = self.hide_tooltip_bravery
        self.bravery_label.setStyleSheet("QLabel { border: none; }")

        # NATIONAL
        self.tooltip_national = CustomTooltip(
            "Freedom of a nation to govern itself without external control.",
            self
        )
        self.national_label = self.findChild(QLabel, 'national')  
        self.national_label.setMouseTracking(True)
        self.national_label.enterEvent = self.show_tooltip_national  
        self.national_label.leaveEvent = self.hide_tooltip_national
        self.national_label.setStyleSheet("QLabel { border: none; }")

    # REVOLUTION
    def show_tooltip_revolution(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_revolution.show_tooltip(tooltip_pos)
        self.revolution_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_revolution(self, event):
        self.revolution_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_revolution.hide_tooltip()

    # SEDITION
    def show_tooltip_sedition(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_sedition.show_tooltip(tooltip_pos)
        self.sedition_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_sedition(self, event):
        self.sedition_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_sedition.hide_tooltip()

    # TREASON
    def show_tooltip_treason(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_treason.show_tooltip(tooltip_pos)
        self.treason_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_treason(self, event):
        self.treason_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_treason.hide_tooltip()

    # REBELLION
    def show_tooltip_rebellion(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_rebellion.show_tooltip(tooltip_pos)
        self.rebellion_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_rebellion(self, event):
        self.rebellion_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_rebellion.hide_tooltip()

    # COMPOSURE
    def show_tooltip_composure(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_composure.show_tooltip(tooltip_pos)
        self.composure_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_composure(self, event):
        self.composure_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_composure.hide_tooltip()

    # BRAVERY
    def show_tooltip_bravery(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_bravery.show_tooltip(tooltip_pos)
        self.bravery_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_bravery(self, event):
        self.bravery_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_bravery.hide_tooltip()

    # NATIONAL
    def show_tooltip_national(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_national.show_tooltip(tooltip_pos)
        self.national_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_national(self, event):
        self.national_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_national.hide_tooltip()


    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter5(self):
        self.switch_window(Chapter5)

    def switch_chapter5p3(self):
        self.switch_window(Chapter5P3)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

class Chapter5P3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'chapter5page3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        backbutton = self.findChild(QtWidgets.QPushButton, 'backbutton')
        backbutton.clicked.connect(self.switch_chapter5p2)
        backbutton.clicked.connect(self.play_click_sound)

        nextbutton = self.findChild(QtWidgets.QPushButton, 'nextbutton')
        nextbutton.clicked.connect(self.switch_epilogue)
        nextbutton.clicked.connect(self.play_click_sound)


        # MARTYR
        self.tooltip_martyr = CustomTooltip(
            "Someone who sacrifices their life for a cause,\n"
            "often for their beliefs or principles.",
            self
        )
        self.martyr_label = self.findChild(QLabel, 'martyr')  
        self.martyr_label.setMouseTracking(True)
        self.martyr_label.enterEvent = self.show_tooltip_martyr  
        self.martyr_label.leaveEvent = self.hide_tooltip_martyr
        self.martyr_label.setStyleSheet("QLabel { border: none; }")

        # INDEPENDENCE
        self.tooltip_independence = CustomTooltip(
            "State of being free from control or rule by another country. ",
            self
        )
        self.independence_label = self.findChild(QLabel, 'independence')  
        self.independence_label.setMouseTracking(True)
        self.independence_label.enterEvent = self.show_tooltip_independence  
        self.independence_label.leaveEvent = self.hide_tooltip_independence
        self.independence_label.setStyleSheet("QLabel { border: none; }")

        # FREEDOM
        self.tooltip_freedom = CustomTooltip(
            "The right to act, speak, or think without hindrance.",
            self
        )
        self.freedom_label = self.findChild(QLabel, 'freedom')  
        self.freedom_label.setMouseTracking(True)
        self.freedom_label.enterEvent = self.show_tooltip_freedom  
        self.freedom_label.leaveEvent = self.hide_tooltip_freedom
        self.freedom_label.setStyleSheet("QLabel { border: none; }")

        # JUSTICE
        self.tooltip_justice = CustomTooltip(
            "The pursuit of fairness and equality.",
            self
        )
        self.justice_label = self.findChild(QLabel, 'justice')  
        self.justice_label.setMouseTracking(True)
        self.justice_label.enterEvent = self.show_tooltip_justice  
        self.justice_label.leaveEvent = self.hide_tooltip_justice
        self.justice_label.setStyleSheet("QLabel { border: none; }")

        # UNITY
        self.tooltip_unity = CustomTooltip(
            "The sense of solidarity and togetherness within a nation.",
            self
        )
        self.unity_label = self.findChild(QLabel, 'unity')  
        self.unity_label.setMouseTracking(True)
        self.unity_label.enterEvent = self.show_tooltip_unity  
        self.unity_label.leaveEvent = self.hide_tooltip_unity
        self.unity_label.setStyleSheet("QLabel { border: none; }")

    # MARTYR
    def show_tooltip_martyr(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_martyr.show_tooltip(tooltip_pos)
        self.martyr_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_martyr(self, event):
        self.martyr_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_martyr.hide_tooltip()

    # INDEPENDENCE
    def show_tooltip_independence(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_independence.show_tooltip(tooltip_pos)
        self.independence_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_independence(self, event):
        self.independence_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_independence.hide_tooltip()

    # FREEDOM
    def show_tooltip_freedom(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_freedom.show_tooltip(tooltip_pos)
        self.freedom_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_freedom(self, event):
        self.freedom_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_freedom.hide_tooltip()

    # JUSTICE
    def show_tooltip_justice(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_justice.show_tooltip(tooltip_pos)
        self.justice_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_justice(self, event):
        self.justice_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_justice.hide_tooltip()
    
    # UNITY
    def show_tooltip_unity(self, event):
        mouse_pos = event.globalPos()
        tooltip_pos = QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)
        self.tooltip_unity.show_tooltip(tooltip_pos)
        self.unity_label.setStyleSheet("QLabel { border: none; text-decoration: underline; }")

    def hide_tooltip_unity(self, event):
        self.unity_label.setStyleSheet("QLabel { border: none; }")
        self.tooltip_unity.hide_tooltip()

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_chapter5p2(self):
        self.switch_window(Chapter5P2)

    def switch_epilogue(self):
        self.switch_window(Epilogue) 

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()





class Epilogue(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'epilogue.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.volumebutton = self.findChild(QtWidgets.QPushButton, 'volumebutton')
        self.volumebutton.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
        self.volumebutton.setIconSize(QtCore.QSize(50, 50))
        self.volumebutton.clicked.connect(self.toggle_music) 

        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitbutton')
        self.exit_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\exit.png"))
        self.exit_button.setIconSize(QtCore.QSize(50, 50))
        self.exit_button.setText("")
        self.exit_button.clicked.connect(self.play_click_sound)
        self.exit_button.clicked.connect(self.switch_exit)

        self.bm_button = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        self.bm_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\bmtable.png")) 
        self.bm_button.setIconSize(QtCore.QSize(50, 50))  
        self.bm_button.setText("") 

        bmbutton = self.findChild(QtWidgets.QPushButton, 'bmbutton')
        bmbutton.clicked.connect(self.switch_table)
        bmbutton.clicked.connect(self.play_click_sound)

        closebutton = self.findChild(QtWidgets.QPushButton, 'closebutton')
        closebutton.clicked.connect(self.switch_main_window)
        closebutton.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        BUTTON_SOUND.play()

    def toggle_music(self):
        global global_is_muted
        if not global_is_muted:
            pygame.mixer.music.set_volume(0)
            self.volume_button.setIcon(QIcon(r"C:\Users\CHI\Downloads\(10)MIDTERM_PROJEC\MIDTERM_PROJECT(8)\MIDTERM_PROJECT\reso\unmute.png"))
            self.volume_button.repaint()
            global_is_muted = True
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.setIcon(QIcon(r"C:/Users/CHI/Downloads/(10)MIDTERM_PROJEC/MIDTERM_PROJECT(8)/MIDTERM_PROJECT/reso/mute.png"))
            self.volume_button.repaint()
            global_is_muted = False

    def switch_exit(self):
        custom_message_box = RizalEDMessageBox()  
        message_box = QtWidgets.QMessageBox()
        message_box.setStyleSheet(custom_message_box.message_box_stylesheet)
        message_box.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        message_box.setText("Are you sure you want to exit?")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.No)

        result = message_box.exec()
        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass  

    def switch_main_window(self):
        self.switch_window(Main_Menu)

    def switch_table(self):
        self.switch_window(TableofContent)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()
        




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main_Menu()
    window.show()
    sys.exit(app.exec_())
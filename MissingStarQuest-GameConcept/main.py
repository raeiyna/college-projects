# TREE ALGORITHM
# CARILLO, LEE JANSEY
# PALACIOS, DONA FLOR SAACHI V.
# SANTOS, REYNA MARIE E.
# TUP-C CHRONICLES: A CHRISTMAS CHRONICLES

import sys
import os
import pygame
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPainterPath, QRegion, QMovie
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QRectF, Qt, QTimer
from PyQt5.uic import loadUi


pygame.init()
pygame.mixer.init()

CLICK_SOUND = r"click.MP3"
click_sound = pygame.mixer.Sound(CLICK_SOUND)


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
        window._drag_active = False
        window.oldPos = None

        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                window._drag_active = True
                window.oldPos = event.globalPos()

        def mouseReleaseEvent(event):
            if event.button() == Qt.LeftButton:
                window._drag_active = False

        def mouseMoveEvent(event):
            if window._drag_active:
                delta = event.globalPos() - window.oldPos
                window.move(window.x() + delta.x(), window.y() + delta.y())
                window.oldPos = event.globalPos()

        window.mousePressEvent = mousePressEvent
        window.mouseReleaseEvent = mouseReleaseEvent
        window.mouseMoveEvent = mouseMoveEvent


class CustomTooltip(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.ToolTip)

        self.message_box_stylesheet = """
            background-color: #6b1b10;
            color: #f1ac37;
            border: 3px solid #803300;
            border-radius: 20px;
            font-family: Arial, sans-serif;
            font-weight: bold;
            padding: 15px;
            font-size: 16px;
        """

        self.setStyleSheet(self.message_box_stylesheet)

        layout = QVBoxLayout(self)
        self.label = QLabel(text, self)

        self.label.setStyleSheet("""
            font-size: 16px;
            color: #e1eaf6;
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


class Landing(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'landing.ui')
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        pygame.mixer.init()
        pygame.mixer.music.load(r'bgm2.mp3')  
        pygame.mixer.music.play(-1) 

        self.is_muted = False  

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        self.musicbutton.clicked.connect(self.toggle_music)
        self.musicbutton.clicked.connect(self.play_click_sound)

        self.exitbutton = self.findChild(QtWidgets.QPushButton, 'settingsbutton')
        self.exitbutton.clicked.connect(self.switch_exit)
        self.exitbutton.clicked.connect(self.play_click_sound)

        start = self.findChild(QtWidgets.QPushButton, 'start')
        start.clicked.connect(self.switch_emblem1)
        start.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        click_sound.play()

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(0.5)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True
  
    def switch_exit(self):
        self.switch_window1(Exit)

    def switch_emblem1(self):
        self.switch_window(Emblem1)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def switch_window1(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()




class Exit(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'exit.ui')
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        yes = self.findChild(QtWidgets.QPushButton, 'yes')
        no = self.findChild(QtWidgets.QPushButton, 'no')

        if yes:
            yes.clicked.connect(self.exit_application)
            yes.clicked.connect(self.play_click_sound)

        if no:
            no.clicked.connect(self.close_exit_ui)
            no.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        click_sound.play()

    def exit_application(self):
        QtWidgets.QApplication.quit()

    def close_exit_ui(self):
        self.close()



class Settings(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'settings.ui')
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        back = self.findChild(QtWidgets.QPushButton, 'back')
        restart = self.findChild(QtWidgets.QPushButton, 'restart')

        if back:
            back.clicked.connect(self.back_settings)
            back.clicked.connect(self.play_click_sound)

        if restart:
            restart.clicked.connect(self.restart_game)
            restart.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        click_sound.play()

    def back_settings(self):
        self.close()

    def restart_game(self):
        self.switch_window(Landing)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()




class Emblem1(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'emblem1.ui')
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next_btn = self.findChild(QtWidgets.QPushButton, 'next')
        next_btn.clicked.connect(self.switch_emblem2)
        next_btn.clicked.connect(self.play_click_sound)

    def switch_emblem2(self):
        self.switch_window(Emblem2)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()



        
class Emblem2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'emblem2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        ch1 = self.findChild(QtWidgets.QPushButton, 'ch1')
        ch1.clicked.connect(self.switch_audi1)
        ch1.clicked.connect(self.play_click_sound)

        ch2 = self.findChild(QtWidgets.QPushButton, 'ch2')
        ch2.clicked.connect(self.switch_caf1)
        ch2.clicked.connect(self.play_click_sound)

        self.exitbutton = self.findChild(QtWidgets.QPushButton, 'settingsbutton')
        self.exitbutton.clicked.connect(self.switch_settings)
        self.exitbutton.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)
            self.musicbutton.clicked.connect(self.play_click_sound)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def switch_settings(self):
        self.switch_window1(Settings)

    def switch_audi1(self):
        self.switch_window(Audi1)

    def switch_caf1(self):
        self.switch_window(Caf1)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def switch_window1(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()

    def play_click_sound(self):
        click_sound.play()








#AUDI
class Audi1(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'audi1.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        ch1 = self.findChild(QtWidgets.QPushButton, 'ch1')
        ch1.clicked.connect(self.switch_audi6)
        ch1.clicked.connect(self.play_click_sound)

        ch2 = self.findChild(QtWidgets.QPushButton, 'ch2')
        ch2.clicked.connect(self.switch_audi2)
        ch2.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)
            self.musicbutton.clicked.connect(self.play_click_sound)

    def switch_audi2(self):
        self.switch_window(Audi2)

    def switch_audi6(self):
        self.switch_window(Audi6)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Audi2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'audi2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_audi3)
        next.clicked.connect(self.play_click_sound)

    def switch_audi3(self):
        self.switch_window(Audi3)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Audi3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'audi3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_audi4)
        next.clicked.connect(self.play_click_sound)

    def switch_audi4(self):
        self.switch_window(Audi4)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Audi4(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'audi4.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        ch1 = self.findChild(QtWidgets.QPushButton, 'ch1')
        ch1.clicked.connect(self.switch_lib1)
        ch1.clicked.connect(self.play_click_sound)

        ch2 = self.findChild(QtWidgets.QPushButton, 'ch2')
        ch2.clicked.connect(self.switch_caf1)
        ch2.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)
            self.musicbutton.clicked.connect(self.play_click_sound)

    def switch_lib1(self):
        self.switch_window(Lib1)

    def switch_caf1(self):
        self.switch_window(Caf1)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Audi5(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'audi5.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        next_btn = self.findChild(QtWidgets.QPushButton, 'next')
        next_btn.clicked.connect(self.switch_audi1)
        next_btn.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)
            self.musicbutton.clicked.connect(self.play_click_sound)

    def switch_audi1(self):
        self.switch_window(Audi1)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Audi6(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'audi6.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_audi5)
        next.clicked.connect(self.play_click_sound)

    def switch_audi5(self):
        self.switch_window(Audi5)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()






#CAF
class Caf1(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'caf1.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        ch1 = self.findChild(QtWidgets.QPushButton, 'ch1')
        ch1.clicked.connect(self.switch_caf2)
        ch1.clicked.connect(self.play_click_sound)

        ch2 = self.findChild(QtWidgets.QPushButton, 'ch2')
        ch2.clicked.connect(self.switch_caf4)
        ch2.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)
            self.musicbutton.clicked.connect(self.play_click_sound)

    def switch_caf4(self):
        self.switch_window(Caf4)

    def switch_caf2(self):
        self.switch_window(Caf2)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Caf2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'caf2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_caf3)
        next.clicked.connect(self.play_click_sound)

    def switch_caf3(self):
        self.switch_window(Caf3)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Caf3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'caf3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        next_btn = self.findChild(QtWidgets.QPushButton, 'next')
        next_btn.clicked.connect(self.switch_caf1)
        next_btn.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)
            self.musicbutton.clicked.connect(self.play_click_sound)

    def switch_caf1(self):
        self.switch_window(Caf1)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Caf4(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'caf4.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_caf5)
        next.clicked.connect(self.play_click_sound)

    def switch_caf5(self):
        self.switch_window(Caf5)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()


class Caf5(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'caf5.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_lib1)
        next.clicked.connect(self.play_click_sound)

    def switch_lib1(self):
        self.switch_window(Lib1)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()

    def play_click_sound(self):
        click_sound.play()




#LIB
class Lib1(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'lib1.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        ch1 = self.findChild(QtWidgets.QPushButton, 'ch1')
        ch1.clicked.connect(self.switch_lib4)
        ch1.clicked.connect(self.play_click_sound)

        ch2 = self.findChild(QtWidgets.QPushButton, 'ch2')
        ch2.clicked.connect(self.switch_lib3)
        ch2.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)

    def switch_lib3(self):
        self.switch_window(Lib4)

    def switch_lib4(self):
        self.switch_window(Lib4)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def play_click_sound(self):
        click_sound.play()

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class Lib2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'lib2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  

        next_btn = self.findChild(QtWidgets.QPushButton, 'next')
        next_btn.clicked.connect(self.switch_lib2)
        next_btn.clicked.connect(self.play_click_sound)

        self.musicbutton = self.findChild(QtWidgets.QPushButton, 'musicbutton')
        if self.musicbutton:
            self.musicbutton.clicked.connect(self.toggle_music)

    def switch_lib2(self):
        self.switch_window(Lib1)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def play_click_sound(self):
        click_sound.play()

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class Lib3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'lib3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_lib2)
        next.clicked.connect(self.play_click_sound)

    def switch_lib2(self):
        self.switch_window(Lib2)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def play_click_sound(self):
        click_sound.play()

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class Lib4(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'lib4.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_lib5)
        next.clicked.connect(self.play_click_sound)

    def switch_lib5(self):
        self.switch_window(Lib5)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def play_click_sound(self):
        click_sound.play()

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class Lib5(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'lib5.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_cqt1)
        next.clicked.connect(self.play_click_sound)

    def switch_cqt1(self):
        self.switch_window(CQT1)

    def toggle_music(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1)  
            self.is_muted = False
        else:
            pygame.mixer.music.set_volume(0)  
            self.is_muted = True

    def play_click_sound(self):
        click_sound.play()

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()






#CQT 
class CQT1(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'cqt1.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.is_muted = False  
        self.set_up(r'RESO/cqt1.gif')

        next_button = self.findChild(QtWidgets.QPushButton, 'next')
        next_button.clicked.connect(self.switch_cqt2)
        next_button.clicked.connect(self.play_click_sound)

        pygame.mixer.init()  
        pygame.mixer.music.load(r'bgm3.mp3')
        pygame.mixer.music.play(-1)  

    def set_up(self, path):
        self.setup_gif(path)

    def setup_gif(self, path):
        self.movie_CQT1 = QMovie(path)  
        self.vid_label = self.findChild(QtWidgets.QLabel, 'cqt1vid')
        self.vid_label.setMovie(self.movie_CQT1)
        self.vid_label.setScaledContents(True)

        self.total_frames = self.movie_CQT1.frameCount()
        self.movie_CQT1.frameChanged.connect(self.check_frame_CQT1)

        self.movie_CQT1.setCacheMode(QMovie.CacheAll)
        self.movie_CQT1.setSpeed(100)
        self.movie_CQT1.start()

    def play_click_sound(self):
        click_sound.play()

    def check_frame_CQT1(self, current_frame):
        if self.total_frames > 0 and current_frame == self.total_frames - 1:
            self.movie_CQT1.stop()
            self.vid_label.setMovie(self.movie_CQT1)

    def switch_cqt2(self):
        self.switch_window(CQT2)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class CQT2(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'cqt2.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.set_up(r'RESO/cqt22.gif')

        next_button = self.findChild(QtWidgets.QPushButton, 'next')
        next_button.clicked.connect(self.switch_cqt3)
        next_button.clicked.connect(self.play_click_sound)

    def play_click_sound(self):
        click_sound.play()

    def set_up(self, path):
        self.setup_gif(path)

    def setup_gif(self, path):
        self.movie_CQT2 = QMovie(path)
        self.vid_label = self.findChild(QtWidgets.QLabel, 'cqt2vid')
        self.vid_label.setMovie(self.movie_CQT2)
        self.vid_label.setScaledContents(True)

        self.total_frames = self.movie_CQT2.frameCount()
        self.movie_CQT2.frameChanged.connect(self.check_frame_CQT2)

        self.movie_CQT2.setCacheMode(QMovie.CacheAll)
        self.movie_CQT2.setSpeed(100)
        self.movie_CQT2.start()

    def check_frame_CQT2(self, current_frame):
        if self.total_frames > 0 and current_frame == self.total_frames - 1:
            self.movie_CQT2.stop()
            self.vid_label.setMovie(self.movie_CQT2)

    def switch_cqt3(self):
        self.switch_window(CQT3)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class CQT3(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'cqt3.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.set_up(r'RESO/cqt3.gif')

        next_button = self.findChild(QtWidgets.QPushButton, 'next')
        next_button.clicked.connect(self.switch_cqt4)
        next_button.clicked.connect(self.play_click_sound)

        self.gif_duration = 10800  

        QtCore.QTimer.singleShot(self.gif_duration, self.stop_gif)

    def set_up(self, path):
        self.setup_gif(path)

    def play_click_sound(self):
        click_sound.play()

    def setup_gif(self, path):
        self.movie_CQT3 = QMovie(path)
        self.vid_label = self.findChild(QtWidgets.QLabel, 'cqt3vid')
        self.vid_label.setMovie(self.movie_CQT3)
        self.vid_label.setScaledContents(True)

        self.total_frames = self.movie_CQT3.frameCount()
        self.movie_CQT3.frameChanged.connect(self.check_frame_CQT2)

        self.movie_CQT3.setCacheMode(QMovie.CacheAll)
        self.movie_CQT3.setSpeed(100)
        self.movie_CQT3.start()

    def check_frame_CQT2(self, current_frame):
        if self.total_frames > 0 and current_frame == self.total_frames - 1:
            self.movie_CQT3.stop()
            self.vid_label.setMovie(self.movie_CQT3)

    def stop_gif(self):
        self.movie_CQT3.stop()

    def switch_cqt4(self):
        self.switch_window(CQT4)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()



class CQT4(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'cqt4.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        next = self.findChild(QtWidgets.QPushButton, 'next')
        next.clicked.connect(self.switch_cqt5)
        next.clicked.connect(self.play_click_sound)

    def switch_cqt5(self):
        self.switch_window(CQT5)

    def play_click_sound(self):
        click_sound.play()

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()


class CQT5(QtWidgets.QMainWindow):
    def __init__(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'cqt5.ui')
        super().__init__()
        uic.loadUi(ui_file_path, self)
        UIUtils.remove_window_header(self)
        UIUtils.apply_rounded_corners(self)
        UIUtils.setup_window_drag(self)

        self.set_up(r'RESO/cqt5.gif')

        next_button = self.findChild(QtWidgets.QPushButton, 'next')
        next_button.clicked.connect(self.switch_landing)
        next_button.clicked.connect(self.play_click_sound)

        pygame.mixer.init()  
        pygame.mixer.music.load(r'bgm4.mp3')
        pygame.mixer.music.play(-1)  

        self.gif_duration = 16000 
        QtCore.QTimer.singleShot(self.gif_duration, self.stop_gif)

    def set_up(self, path):
        self.setup_gif(path)

    def play_click_sound(self):
        click_sound.play()

    def setup_gif(self, path):
        self.movie_CQT3 = QMovie(path)  
        self.vid_label = self.findChild(QtWidgets.QLabel, 'cqt5vid')
        self.vid_label.setMovie(self.movie_CQT3)
        self.vid_label.setScaledContents(True)

        self.movie_CQT3.setCacheMode(QMovie.CacheAll)
        self.movie_CQT3.setSpeed(100)
        self.movie_CQT3.start()

    def stop_gif(self):
        self.movie_CQT3.stop()

    def switch_landing(self):
        pygame.mixer.music.stop()
        
        self.switch_window(Landing)

    def switch_window(self, new_window_class, *args):
        self.new_window = new_window_class(*args)
        self.new_window.show()
        self.close()







if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Landing()
    window.show()
    sys.exit(app.exec_())

from PySide6.QtWidgets import QFrame
from PySide6.QtCore import QTimer, QTime, Qt
from PySide6.QtGui import QPainter, QPen, QColor

class AnalogClock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("background-color: black; border-radius: 100px;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        time = QTime.currentTime()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        # Clock face (already styled via stylesheet)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(-100, -100, 200, 200)

        # Hour tick marks (white)
        painter.setPen(QPen(Qt.white, 2))
        for i in range(12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30)

        # Hour hand (white)
        painter.save()
        painter.setPen(QPen(Qt.white, 6))
        hour_angle = 30 * ((time.hour() % 12) + time.minute() / 60.0)
        painter.rotate(hour_angle)
        painter.drawLine(0, 0, 0, -50)
        painter.restore()

        # Minute hand (white)
        painter.save()
        painter.setPen(QPen(Qt.white, 4))
        minute_angle = 6 * (time.minute() + time.second() / 60.0)
        painter.rotate(minute_angle)
        painter.drawLine(0, 0, 0, -70)
        painter.restore()

        # Second hand (orange)
        painter.save()
        painter.setPen(QPen(QColor("#ff9500"), 2))  # Apple orange
        second_angle = 6 * time.second()
        painter.rotate(second_angle)
        painter.drawLine(0, 0, 0, -80)
        painter.restore()

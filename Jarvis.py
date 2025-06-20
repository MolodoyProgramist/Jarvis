import sys
import numpy as np
import sounddevice as sd
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl, Slot
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QPixmap, QIcon
from PySide6.QtMultimedia import QSoundEffect

class MicButton(QPushButton):
    def __init__(self):
        super().__init__()
        self._wave_radius = 50
        self.setCheckable(True)
        self.setFixedSize(80, 80)
        self.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                background-color: #444;
                border: 4px solid #00aaff;
            }
            QPushButton:checked {
                background-color: #00aaff;
                border-color: #00e0ff;
            }
        """)
        self.anim = QPropertyAnimation(self, b"wave_radius")
        self.anim.setStartValue(50)
        self.anim.setEndValue(70)
        self.anim.setDuration(1000)
        self.anim.setLoopCount(-1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.toggled.connect(self.on_toggle)

    def on_toggle(self, checked):
        if checked:
            self.anim.start()
        else:
            self.anim.stop()
            self.wave_radius = 50
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isChecked():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            center = self.rect().center()
            color = QColor(0, 170, 255, 100)
            pen = QPen(color)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, self._wave_radius, self._wave_radius)

    def get_wave_radius(self):
        return self._wave_radius

    def set_wave_radius(self, val):
        self._wave_radius = val
        self.update()

    wave_radius = property(get_wave_radius, set_wave_radius)

class JarvisVoiceChat(QWidget):
    def __init__(self):
        super().__init__()

        self.phone_width = 375
        self.phone_height = 667
        self.setFixedSize(self.phone_width, self.phone_height)

        self.background = QPixmap("jarvisBk.jpg")

        self.setWindowTitle("Jarvis Voice Assistant")
        self.setWindowIcon(QIcon("icon.png"))
        self.setLayout(None)

        # Кнопка микрофона сверху слева
        self.mic_btn = MicButton()
        self.mic_btn.setParent(self)
        self.mic_btn.move(25, 25)

        self.setup_sounds()
        self.stream = None

        self.volume_timer = QTimer()
        self.volume_timer.setInterval(100)
        self.volume_timer.timeout.connect(self.update_volume_meter)
        self.current_volume = 0

        self.mic_btn.toggled.connect(self.on_mic_toggled)

    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_bg = self.background.scaled(self.phone_width, self.phone_height,
                                          Qt.KeepAspectRatioByExpanding,
                                          Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_bg)

    def setup_sounds(self):
        self.activation_sound = QSoundEffect()
        self.activation_sound.setSource(QUrl.fromLocalFile("jarvisRU.wav"))
        self.activation_sound.setVolume(0.7)

    def audio_callback(self, indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 10
        self.current_volume = min(max(volume_norm, 0), 100)

    @Slot(bool)
    def on_mic_toggled(self, checked):
        if checked:
            self.activation_sound.play()
            self.stream = sd.InputStream(callback=self.audio_callback)
            self.stream.start()
            self.volume_timer.start()
        else:
            self.volume_timer.stop()
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

    def update_volume_meter(self):
        pass  # можно удалить или оставить пустым

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisVoiceChat()
    window.show()
    sys.exit(app.exec())

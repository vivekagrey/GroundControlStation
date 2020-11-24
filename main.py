import window
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QSplashScreen, QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash_pix = QPixmap("logo.png")
    # splash_pix.scaled(500, 250)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    # splash.setFixedSize(500, 250)
    splash.show()
    def start():
        splash.close()
        global gui
        gui = window.Window()
        gui.show()
    QTimer.singleShot(5000, start)
    app.aboutToQuit.connect(window.VideoThread.stop)
    sys.exit(app.exec_())

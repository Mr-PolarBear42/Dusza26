from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

class IDE():
    def __init__(self):

        app = QApplication(sys.argv)

        self.win = QMainWindow()
        self.win.setGeometry(0, 0, 720, 480)
        self.win.setWindowTitle("Arany Bánya")

        ### put stuff here
    
        

        ###

        self.win.show()
        sys.exit(app.exec())
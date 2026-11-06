import sys

from PyQt6.QtWidgets import QApplication, QMainWindow


class Ide:
    def __init__(self):

        app = QApplication(sys.argv)

        self.win = QMainWindow()
        self.win.setWindowTitle("Arany Bánya")

        ### put stuff here
    
        

        ###

        self.win.showMaximized()
        sys.exit(app.exec())
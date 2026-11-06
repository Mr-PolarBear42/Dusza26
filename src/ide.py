import sys

import PyQt6.QtWidgets as qtw
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from block_program import BlockProgram


class Ide:
    def __init__(self):

        app = QApplication(sys.argv)

        self.win = QMainWindow()
        self.win.setWindowTitle("Arany Bánya")

        blockProgramWidget = BlockProgram()
        mapWidget = qtw.QLabel("Vizualizáció")

        centralWidget = QWidget()
        centralWidgetLayout = QHBoxLayout(centralWidget)
        centralWidgetLayout.addWidget(blockProgramWidget)
        centralWidgetLayout.addWidget(mapWidget)
        centralWidgetLayout.setStretch(0, 2)
        centralWidgetLayout.setStretch(1, 3)

        self.win.setCentralWidget(centralWidget)

        self.win.showMaximized()
        sys.exit(app.exec())

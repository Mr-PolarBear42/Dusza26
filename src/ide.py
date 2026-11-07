import sys

import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qtw
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

from block_program import BlockProgram


class Ide:
    def __init__(self):

        app = QApplication(sys.argv)

        self.win = QMainWindow()
        self.win.setWindowTitle("Arany Bánya")

        blockProgramWidget = BlockProgram()
        mapWidget = qtw.QLabel("Vizualizáció")

        centralWidget = QWidget()
        mainLayout = qtw.QHBoxLayout(centralWidget)
        mainLayoutSplitter = qtw.QSplitter(qtc.Qt.Orientation.Horizontal, centralWidget)

        mainLayoutSplitter.addWidget(blockProgramWidget)
        mainLayoutSplitter.addWidget(mapWidget)
        mainLayoutSplitter.setStretchFactor(0, 2)
        mainLayoutSplitter.setStretchFactor(1, 2)

        mainLayout.addWidget(mainLayoutSplitter)

        self.win.setCentralWidget(centralWidget)

        self.win.showMaximized()
        sys.exit(app.exec())

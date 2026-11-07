import sys

import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qtw

from block_program import BlockProgram
from map_viewer import MapViewer
from utils.enums import Direction


class Ide:
    def __init__(self, map: list[list[str]], w: int, h: int, code: str):

        app = qtw.QApplication(sys.argv)

        self.win = qtw.QMainWindow()
        self.win.setWindowTitle("Arany Bánya")

        blockProgramWidget = BlockProgram()
        mapWidget = MapViewer()

        centralWidget = qtw.QWidget()
        mainLayout = qtw.QHBoxLayout(centralWidget)
        mainLayoutSplitter = qtw.QSplitter(qtc.Qt.Orientation.Horizontal, centralWidget)

        mainLayoutSplitter.addWidget(blockProgramWidget)
        mainLayoutSplitter.addWidget(mapWidget)
        mainLayoutSplitter.setSizes((1, 1))

        mainLayout.addWidget(mainLayoutSplitter)

        self.win.setCentralWidget(centralWidget)

        mapWidget.load_map(map, w, h, 0, 0, Direction.WEST)

        self.win.showMaximized()
        sys.exit(app.exec())

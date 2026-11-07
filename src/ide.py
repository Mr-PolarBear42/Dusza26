import sys

from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from block_program import BlockProgram
from map_viewer import MapViewer
from utils.enums import Direction


class Ide:
    def __init__(self, map: list[list[str]], w: int, h: int, code: str):

        app = QApplication(sys.argv)

        self.win = QMainWindow()
        self.win.setWindowTitle("Arany Bánya")

        blockProgramWidget = BlockProgram()
        mapWidget = MapViewer()

        centralWidget = QWidget()
        centralWidgetLayout = QHBoxLayout(centralWidget)
        centralWidgetLayout.addWidget(blockProgramWidget)
        centralWidgetLayout.addWidget(mapWidget)
        centralWidgetLayout.setStretch(0, 2)
        centralWidgetLayout.setStretch(1, 3)

        mapWidget.load_map(map, w, h, 0, 0, Direction.NORTH)
        mapWidget.render_map()

        self.win.setCentralWidget(centralWidget)

        self.win.showMaximized()
        sys.exit(app.exec())

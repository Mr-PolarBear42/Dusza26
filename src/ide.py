import sys

import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qtw

from blockly_panel import BlocklyPanel
from map_viewer import MapViewer
from utils.enums import Direction


class Ide:
    def __init__(self, map: list[list[str]], w: int, h: int, code: str):
        app = qtw.QApplication(sys.argv)

        self.win = qtw.QMainWindow()
        self.win.setWindowTitle("Arany Bánya")

        blockly_panel = BlocklyPanel(map, code)
        map_widget = MapViewer()

        central_widget = qtw.QWidget()
        main_layout = qtw.QHBoxLayout(central_widget)
        splitter = qtw.QSplitter(qtc.Qt.Orientation.Horizontal, central_widget)
        splitter.addWidget(blockly_panel)
        splitter.addWidget(map_widget)
        splitter.setSizes((1, 1))
        main_layout.addWidget(splitter)
        self.win.setCentralWidget(central_widget)

        map_widget.load_map(map, w, h, 0, 0, Direction)

        self.win.showMaximized()
        sys.exit(app.exec())

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
        mapWidget = MapViewer()
        blockly_panel.robotStateChanged.connect(mapWidget.update_robot_state)

        central_widget = qtw.QWidget()
        main_layout = qtw.QHBoxLayout(central_widget)
        splitter = qtw.QSplitter(qtc.Qt.Orientation.Horizontal, central_widget)
        splitter.addWidget(blockly_panel)
        splitter.addWidget(mapWidget)
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        self.win.setCentralWidget(central_widget)

        robot_position = next(
            (
                (column, row, Direction("^>v<".index(value)))
                for row, values in enumerate(map)
                for column, value in enumerate(values)
                if value in "^>v<"
            ),
            (0, 0, Direction.WEST),
        )
        mapWidget.load_map(map, w, h, *robot_position)

        self.win.showMaximized()
        sys.exit(app.exec())

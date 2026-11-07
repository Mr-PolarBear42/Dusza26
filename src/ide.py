import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from blockly_panel import BlocklyPanel
from map_viewer import MapViewer
from utils.enums import Direction
from utils.resource_path import resource_path


class Ide:
    def __init__(self, map: list[list[str]], w: int, h: int, code: str):
        app = QtWidgets.QApplication(sys.argv)

        self.win = QtWidgets.QMainWindow()
        self.win.setWindowTitle("Arany Bánya MineScript IDE")
        self.win.setWindowIcon(QtGui.QIcon(resource_path("assets/icon.png")))

        blockly_panel = BlocklyPanel(map, code)
        mapWidget = MapViewer()
        blockly_panel.robotStateChanged.connect(mapWidget.update_robot_state)
        blockly_panel.mapResetEvent.connect(mapWidget.reset_map)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, central_widget)
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

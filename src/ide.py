import sys
from copy import deepcopy
from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets

from blockly_panel import BlocklyPanel
from map_viewer import MapViewer
from interpreter.logging import ExecutionLog
from utils.enums import Direction
from utils.resource_path import resource_path


class Ide:
    def __init__(
        self,
        map: list[list[str]],
        w: int,
        h: int,
        code: str,
        output_path: str | Path | None = None,
    ):
        app = QtWidgets.QApplication(sys.argv)

        self.win = QtWidgets.QMainWindow()
        self.win.setWindowTitle("Arany Bánya MineScript IDE")
        self.win.setWindowIcon(QtGui.QIcon(resource_path("assets/icon.png")))
        menu_bar: QtWidgets.QMenuBar = self.win.menuBar()  # ty: ignore[invalid-assignment]

        file_menu: QtWidgets.QMenu = menu_bar.addMenu("File")  # ty: ignore[invalid-assignment]
        edit_menu: QtWidgets.QMenu = menu_bar.addMenu("Edit")  # ty: ignore[invalid-assignment]

        open_action = QtGui.QAction("Open")
        close_action = QtGui.QAction("Close")
        undo_action = QtGui.QAction("Undo")
        redo_action = QtGui.QAction("Redo")
        preferences_action = QtGui.QAction("Preferences")

        open_action.setShortcut(QtGui.QKeySequence("Ctrl+o"))
        close_action.setShortcut(QtGui.QKeySequence("Ctrl+q"))
        undo_action.setShortcut(QtGui.QKeySequence("Ctrl+z"))
        redo_action.setShortcut(QtGui.QKeySequence("Ctrl+y"))
        preferences_action.setShortcut(QtGui.QKeySequence("Ctrl+."))

        file_menu.addAction(open_action)
        file_menu.addAction(close_action)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(preferences_action)

        close_action.triggered.connect(self.win.close)

        blockly_panel = BlocklyPanel(map, code)
        if output_path is not None:
            blockly_panel.executionFinished.connect(
                lambda log: self._write_execution_log(log, output_path)
            )
        mapWidget = MapViewer()
        blockly_panel.robotStateChanged.connect(mapWidget.update_robot_state)
        blockly_panel.mapResetEvent.connect(mapWidget.reset_map)
        mapWidget.commandRequested.connect(blockly_panel.execute_manual_command)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, central_widget)
        splitter.addWidget(blockly_panel)
        splitter.addWidget(mapWidget)
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        self.win.setCentralWidget(central_widget)

        map_no_robot = deepcopy(map)
        robot_position = [0, 0, Direction.NORTH]
        for row, values in enumerate(map_no_robot):
            for column, value in enumerate(values):
                if value in "^>v<":
                    map_no_robot[row][column] = "."
                    robot_position = [column, row, Direction("^>v<".index(value))]
        mapWidget.load_map(map_no_robot, w, h, *robot_position)

        self.win.showMaximized()
        sys.exit(app.exec())

    @staticmethod
    def _write_execution_log(log: object, output_path: str | Path) -> None:
        if not isinstance(log, ExecutionLog):
            raise TypeError("Expected an ExecutionLog")
        log.write(output_path)

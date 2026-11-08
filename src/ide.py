import sys
from copy import deepcopy
from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets

from blockly_panel import BlocklyPanel
from interpreter import Robot
from map_viewer import MapViewer
from read_input import read_input
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
            blockly_panel.executionProgress.connect(
                lambda lines: self._write_execution_log(lines, output_path)
            )
        mapWidget = MapViewer()
        blockly_panel.robotStateChanged.connect(mapWidget.update_robot_state)
        blockly_panel.mapResetEvent.connect(mapWidget.reset_map)
        mapWidget.commandRequested.connect(blockly_panel.execute_manual_command)
        open_action.triggered.connect(lambda: self._open_task(blockly_panel, mapWidget))

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, central_widget)
        splitter.addWidget(blockly_panel)
        splitter.addWidget(mapWidget)
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        self.win.setCentralWidget(central_widget)

        map_no_robot = deepcopy(map)
        robot_position: tuple[int, int, Direction] = (0, 0, Direction.NORTH)
        for row, values in enumerate(map_no_robot):
            for column, value in enumerate(values):
                if value in "^>v<":
                    map_no_robot[row][column] = "."
                    robot_position = (column, row, Direction("^>v<".index(value)))
        mapWidget.load_map(map_no_robot, w, h, *robot_position)

        self.win.showMaximized()
        sys.exit(app.exec())

    def _open_task(self, blockly_panel: BlocklyPanel, map_widget: MapViewer) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.win,
            "Open task",
            "",
            "Text files (*.txt)",
        )
        if not file_path:
            return

        if Path(file_path).suffix.lower() != ".txt":
            self._show_open_error("Only .txt task files can be opened.")
            return

        try:
            map_data, width, height, code = read_input(file_path)
            robot = Robot.from_map(["".join(row) for row in map_data])
        except (OSError, UnicodeError, ValueError) as error:
            self._show_open_error(f"The selected file is not a valid task:\n{error}")
            return

        map_without_robot = deepcopy(map_data)
        map_without_robot[robot.row][robot.column] = "."
        map_widget.load_map(
            map_without_robot,
            width,
            height,
            robot.column,
            robot.row,
            Direction("^>v<".index(robot.direction)),
        )
        blockly_panel.load_task(map_data, code)

    def _show_open_error(self, message: str) -> None:
        QtWidgets.QMessageBox.critical(self.win, "Could not open task", message)

    @staticmethod
    def _write_execution_log(lines: tuple[str, ...], output_path: str | Path) -> None:
        content = "\n".join(lines)
        if lines:
            content += "\n"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content, encoding="utf-8")

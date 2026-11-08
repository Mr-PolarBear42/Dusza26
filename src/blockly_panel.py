import blockly_editor
from PyQt6 import QtCore, QtGui, QtWidgets

from blockly_editor import BlocklyEditor
from icon_button import IconButton
from interpreter import Interpreter, Robot
from interpreter.state_snapshot import StateSnapshot
from minescript_highlighter import MineScriptHighlighter
from utils.arrow_to_direction import arrow_to_direction
from utils.resource_path import resource_path


class BlocklyPanel(QtWidgets.QWidget):
    codeChanged = QtCore.pyqtSignal(str)
    robotStateChanged = QtCore.pyqtSignal(object)
    mapResetEvent = QtCore.pyqtSignal()

    def __init__(
        self,
        map_data: list[list[str]],
        source: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.map_data = map_data
        self.code = source
        self.debug_snapshots = []
        self.debug_log_lines = ()
        self.debug_log_indices = []
        self.debug_index = -1
        self.debugging = False
        self._execution_timer = QtCore.QTimer(self)
        self._execution_timer.setInterval(100)
        self._execution_timer.timeout.connect(self._emit_next_execution_state)
        self._execution_states = []
        self._execution_state_index = 0

        palette = QtWidgets.QApplication.palette()
        dark_mode = palette.window().color().lightness() < 128
        self.blockly_editor = BlocklyEditor(source, dark_mode=dark_mode)
        self.blockly_editor.codeChanged.connect(self._code_changed)

        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.previous_button = IconButton(
            resource_path("assets/icons/debug-step-back.svg"),
            QtGui.QColor("#70b4f1"),
            "Step back",
        )
        self.next_button = IconButton(
            resource_path("assets/icons/debug-step-forward.svg"),
            QtGui.QColor("#70b4f1"),
            "Step forward",
        )
        self.debug_button = IconButton(
            resource_path("assets/icons/debug-start.svg"),
            QtGui.QColor("#89d185"),
            "Start debugging",
        )
        self.execute_button = IconButton(
            resource_path("assets/icons/start.svg"),
            QtGui.QColor("#89d185"),
            "Run without debugging",
        )
        self.stop_button = IconButton(
            resource_path("assets/icons/stop.svg"),
            QtGui.QColor("#f6703d"),
            "Stop",
        )
        self.stop_button.hide()

        self.execution_speed_slider = QtWidgets.QSlider(
            QtCore.Qt.Orientation.Horizontal
        )

        self.speed_slider_value_label = QtWidgets.QLabel()
        self.execution_speed_slider.setRange(5, 100)
        self.execution_speed_slider.sliderMoved.connect(self._speed_slider_moved)
        self.execution_speed_slider.setValue(self.execution_speed_slider.maximum())
        self._speed_slider_moved(self.execution_speed_slider.value())

        self.labelled_speed_slider = QtWidgets.QWidget()
        labelled_speed_slider_layout = QtWidgets.QHBoxLayout(self.labelled_speed_slider)
        labelled_speed_slider_layout.setContentsMargins(0, 0, 0, 0)
        labelled_speed_slider_layout.addWidget(QtWidgets.QLabel("Step interval (ms):"))
        labelled_speed_slider_layout.addWidget(self.speed_slider_value_label)
        labelled_speed_slider_layout.addWidget(self.execution_speed_slider)
        self.labelled_speed_slider.hide()

        self.previous_button.clicked.connect(lambda: self._select_debug_step(-1))
        self.execute_button.clicked.connect(lambda: self._execute(debug=False))
        self.debug_button.clicked.connect(lambda: self._execute(debug=True))
        self.next_button.clicked.connect(lambda: self._select_debug_step(1))
        self.stop_button.clicked.connect(lambda: self._stop())

        self.debugger_buttons = QtWidgets.QWidget()
        debugger_button_layout = QtWidgets.QHBoxLayout(self.debugger_buttons)
        debugger_button_layout.setContentsMargins(0, 0, 0, 0)
        debugger_button_layout.addWidget(self.previous_button)
        debugger_button_layout.addWidget(self.next_button)
        self.debugger_buttons.hide()

        self.start_buttons = QtWidgets.QWidget()
        start_buttons_layout = QtWidgets.QHBoxLayout(self.start_buttons)
        start_buttons_layout.setContentsMargins(0, 0, 0, 0)
        start_buttons_layout.addWidget(self.debug_button)
        start_buttons_layout.addWidget(self.execute_button)

        controls_layout.addStretch()
        controls_layout.addWidget(self.labelled_speed_slider)
        controls_layout.addWidget(self.debugger_buttons)
        controls_layout.addWidget(self.start_buttons)
        controls_layout.addWidget(self.stop_button)

        self.source_view = QtWidgets.QPlainTextEdit()
        self.source_view.setFont(QtGui.QFont("Consolas", 10))
        self.source_view_highlighter = MineScriptHighlighter(
            self.source_view.document()
        )
        self.source_view.setReadOnly(True)
        self.source_view.setPlaceholderText("Generated Minescript will appear here.")
        self.source_view.setPlainText(source)

        self.log_view = QtWidgets.QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Execution logs will appear here.")

        self.debug_panel = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        program_state_text_group = QtWidgets.QGroupBox("Program State")
        program_state_text_group_layout = QtWidgets.QVBoxLayout(
            program_state_text_group
        )
        program_state_text_group_layout.setContentsMargins(0, 0, 0, 0)

        self.program_state_text = QtWidgets.QPlainTextEdit()
        self.program_state_text.setReadOnly(True)
        self.program_state_text.setPlaceholderText("Debugger state will appear here.")
        program_state_text_group_layout.addWidget(self.program_state_text)

        self.variable_table = QtWidgets.QTableWidget()
        self.variable_table.setColumnCount(3)
        self.variable_table.setHorizontalHeaderLabels(("Name", "Value", "Type"))

        variable_table_group = QtWidgets.QGroupBox("Variables")
        labeled_variable_table_layout = QtWidgets.QVBoxLayout(variable_table_group)
        labeled_variable_table_layout.setContentsMargins(0, 0, 0, 0)
        labeled_variable_table_layout.addWidget(self.variable_table)

        self.debug_panel.addWidget(program_state_text_group)
        self.debug_panel.addWidget(variable_table_group)

        self.output_tabs = QtWidgets.QTabWidget()
        self.output_tabs.addTab(self.source_view, "Generated source")
        self.output_tabs.addTab(self.log_view, "Execution log")

        editor_output_group = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        editor_output_group.addWidget(self.blockly_editor)
        editor_output_group.addWidget(self.output_tabs)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(controls)
        layout.addWidget(editor_output_group)

    def _code_changed(self, code: str) -> None:
        self.code = code
        self.source_view.setPlainText(code)
        self.codeChanged.emit(code)

    def _reset(self):
        self.debugger_buttons.hide()
        self._hide_debug_panel()
        self._clear_highlight()
        self.start_buttons.show()
        self.stop_button.hide()
        self.labelled_speed_slider.hide()

    def _speed_slider_moved(self, value: int):
        self._execution_timer.setInterval(int(value))
        self.speed_slider_value_label.setText(str(value))

    def _execute(self, debug: bool) -> None:
        self._execution_timer.stop()
        self._emit_map_reset()
        try:
            robot = Robot.from_map(["".join(row) for row in self.map_data])
            self._emit_robot_state(
                robot.row, robot.column, robot.direction, robot.mined_positions
            )
            interpreter = Interpreter(robot)
            log = interpreter.run(self.code)
        except ValueError as error:
            self.log_view.setPlainText(f"Could not execute program: {error}")
            self.program_state_text.clear()
            self.variable_table.setRowCount(0)
            self.debug_snapshots = []
            self.debug_index = -1
            self.debugging = False
            self._reset()
            return

        self.debug_snapshots = interpreter.entry_snapshots
        self.debug_log_lines = log.lines
        self.debug_log_indices = interpreter.entry_log_indices
        self.debug_index = -1 if debug else len(self.debug_snapshots) - 1
        self.debugging = debug
        self._execution_states = [
            self._state_from_snapshot(snapshot)
            for snapshot in interpreter.state_snapshots
        ]
        self._execution_state_index = 0
        self.debugger_buttons.setVisible(debug and bool(self.debug_snapshots))
        self.start_buttons.hide()
        self.stop_button.show()
        self._clear_highlight()
        if debug:
            self._show_debug_panel()
            self.program_state_text.clear()
            self.variable_table.setRowCount(0)
            self.log_view.clear()
        else:
            self.log_view.setPlainText("\n".join(log.lines))
            if self._execution_states:
                self._execution_timer.start()
            self._hide_debug_panel()
            self.labelled_speed_slider.show()
            self.output_tabs.setCurrentWidget(self.log_view)

    def _stop(self):
        self._execution_timer.stop()
        self._emit_map_reset()
        self._reset()

    def _select_debug_step(self, delta: int) -> None:
        if not self.debugging or not self.debug_snapshots:
            return
        new_index = max(0, min(self.debug_index + delta, len(self.debug_snapshots) - 1))
        if new_index == self.debug_index:
            return
        self.debug_index = new_index
        snapshot = self.debug_snapshots[self.debug_index]
        self._emit_robot_state(
            snapshot.robot_position[0],
            snapshot.robot_position[1],
            snapshot.robot_direction,
            snapshot.mined_positions,
        )
        self._select_source_line(snapshot.line_number)
        self._render_debug_state()
        self._render_debug_log()
        if self.debug_index == len(self.debug_snapshots) - 1:
            self._finish_debugging()

    def _render_debug_state(self) -> None:
        snapshot = self.debug_snapshots[self.debug_index]
        self.variable_table.setRowCount(len(snapshot.variables.items()))
        for i, (name, value) in enumerate(sorted(snapshot.variables.items())):
            type = "Bool" if isinstance(value, bool) else "Number"
            self.variable_table.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            self.variable_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(value)))
            self.variable_table.setItem(i, 2, QtWidgets.QTableWidgetItem(type))

        self.program_state_text.setPlainText(
            f"Step {self.debug_index + 1} of {len(self.debug_snapshots)}\n"
            f"Source line: {snapshot.line_number}\n"
            f"Robot\n"
            f"  Position: row {snapshot.robot_position[0]}, "
            f"column {snapshot.robot_position[1]}\n"
            f"  Direction: {snapshot.robot_direction} ({arrow_to_direction(snapshot.robot_direction)})"
        )

    def _render_debug_log(self) -> None:
        if self.debug_index < 0:
            self.log_view.clear()
            return
        end = (
            self.debug_log_indices[self.debug_index + 1]
            if self.debug_index + 1 < len(self.debug_log_indices)
            else len(self.debug_log_lines)
        )
        self.log_view.setPlainText("\n".join(self.debug_log_lines[:end]))

    def _show_debug_panel(self) -> None:
        if self.output_tabs.indexOf(self.debug_panel) == -1:
            self.output_tabs.addTab(self.debug_panel, "Debug")
        self.output_tabs.setCurrentWidget(self.debug_panel)

    def _hide_debug_panel(self) -> None:
        index = self.output_tabs.indexOf(self.debug_panel)
        if index != -1:
            self.output_tabs.removeTab(index)

    def _finish_debugging(self) -> None:
        self.debugging = False
        if self._execution_states:
            self.robotStateChanged.emit(self._execution_states[-1])
        self.log_view.setPlainText("\n".join(self.debug_log_lines))
        self._reset()

    def _emit_next_execution_state(self) -> None:
        if self._execution_state_index >= len(self._execution_states):
            self._execution_timer.stop()
            self._reset()
            return
        self.robotStateChanged.emit(self._execution_states[self._execution_state_index])
        self._execution_state_index += 1

    def _emit_map_reset(self) -> None:
        self.mapResetEvent.emit()

    @staticmethod
    def _state_from_snapshot(snapshot: StateSnapshot) -> dict:
        return {
            "row": snapshot.robot_position[0],
            "column": snapshot.robot_position[1],
            "facing": snapshot.robot_direction,
            "mined_at": sorted(snapshot.mined_positions),
        }

    def _emit_robot_state(
        self,
        row: int,
        column: int,
        direction: str,
        mined_positions: set[tuple[int, int]] | frozenset[tuple[int, int]],
    ) -> None:
        self.robotStateChanged.emit(
            {
                "row": row,
                "column": column,
                "facing": direction,
                "mined_at": sorted(mined_positions),
            }
        )

    def _select_source_line(self, line_number: int) -> None:
        self.blockly_editor.highlight_line(line_number)
        document = self.source_view.document()
        if not document:
            return

        block = document.findBlockByLineNumber(line_number - 1)
        if not block.isValid():
            return
        cursor = self.source_view.textCursor()
        cursor.setPosition(block.position())
        cursor.movePosition(
            QtGui.QTextCursor.MoveOperation.EndOfBlock,
            QtGui.QTextCursor.MoveMode.KeepAnchor,
        )
        self.source_view.setTextCursor(cursor)
        self.source_view.ensureCursorVisible()

    def _clear_highlight(self) -> None:
        self.blockly_editor.clear_highlight()
        self.source_view.moveCursor(QtGui.QTextCursor.MoveOperation.End)

from PyQt6 import QtCore, QtGui, QtWidgets

from blockly_editor import BlocklyEditor
from interpreter import DummyRobot, Interpreter


class BlocklyPanel(QtWidgets.QWidget):
    codeChanged = QtCore.pyqtSignal(str)
    robotStateChanged = QtCore.pyqtSignal(object)

    def __init__(self, map_data: list[list[str]], source: str = "", parent=None) -> None:
        super().__init__(parent)
        self.map_data = map_data
        self.code = source
        self.debug_snapshots = []
        self.debug_log_lines = ()
        self.debug_log_indices = []
        self.debug_index = -1
        self.debugging = False
        self._execution_timer = QtCore.QTimer(self)
        self._execution_timer.setInterval(250)
        self._execution_timer.timeout.connect(self._emit_next_execution_state)
        self._execution_states = []
        self._execution_state_index = 0

        palette = QtWidgets.QApplication.palette()
        dark_mode = palette.window().color().lightness() < 128
        self.blockly_editor = BlocklyEditor(source, dark_mode=dark_mode)
        self.blockly_editor.codeChanged.connect(self._code_changed)

        execute_button = QtWidgets.QPushButton("Execute")
        execute_button.clicked.connect(lambda: self._execute(debug=False))
        debug_button = QtWidgets.QPushButton("Debug")
        debug_button.clicked.connect(lambda: self._execute(debug=True))
        self._style_buttons(execute_button, debug_button)

        previous_button = QtWidgets.QPushButton("Previous step")
        previous_button.clicked.connect(lambda: self._select_debug_step(-1))
        next_button = QtWidgets.QPushButton("Next step")
        next_button.clicked.connect(lambda: self._select_debug_step(1))
        self.debug_controls = QtWidgets.QWidget()
        debug_layout = QtWidgets.QHBoxLayout(self.debug_controls)
        debug_layout.setContentsMargins(0, 0, 0, 0)
        debug_layout.addWidget(previous_button)
        debug_layout.addWidget(next_button)
        self.debug_controls.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.debug_controls.setVisible(False)
        self._style_buttons(
            previous_button,
            next_button,
            palette_indexes=(2, 3),
        )

        self.source_view = QtWidgets.QPlainTextEdit()
        self.source_view.setReadOnly(True)
        self.source_view.setPlaceholderText("Generated Minescript will appear here.")
        self.source_view.setPlainText(source)

        self.log_view = QtWidgets.QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Execution logs will appear here.")

        self.debug_view = QtWidgets.QPlainTextEdit()
        self.debug_view.setReadOnly(True)
        self.debug_view.setPlaceholderText("Debugger state will appear here.")

        self.output_tabs = QtWidgets.QTabWidget()
        self.output_tabs.addTab(self.source_view, "Generated source")
        self.output_tabs.addTab(self.log_view, "Execution log")

        action_buttons = QtWidgets.QHBoxLayout()
        action_buttons.addWidget(execute_button)
        action_buttons.addWidget(debug_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(action_buttons)
        layout.addWidget(self.debug_controls)
        layout.addWidget(self.blockly_editor)
        layout.addWidget(self.output_tabs)
        layout.setStretch(2, 3)
        layout.setStretch(3, 2)

    @staticmethod
    def _style_buttons(
        *buttons: QtWidgets.QPushButton,
        palette_indexes: tuple[int, ...] | None = None,
    ) -> None:
        styles = (
            ("#4C97FF", "#3378D0", "#285EA8"),
            ("#FFAB19", "#D98B00", "#B87300"),
            ("#9966FF", "#7547D6", "#5935A8"),
            ("#59C059", "#419A41", "#307530"),
        )
        selected_styles = (
            tuple(styles[index] for index in palette_indexes)
            if palette_indexes is not None
            else styles[: len(buttons)]
        )
        for button, (background, hover, pressed) in zip(buttons, selected_styles):
            button.setStyleSheet(
                f"QPushButton {{ background: {background}; color: white; "
                "font-weight: bold; border: none; border-radius: 6px; "
                "padding: 8px 16px; }"
                f"QPushButton:hover {{ background: {hover}; }}"
                f"QPushButton:pressed {{ background: {pressed}; }}"
            )

    def _code_changed(self, code: str) -> None:
        self.code = code
        self.source_view.setPlainText(code)
        self.codeChanged.emit(code)

    def _execute(self, debug: bool) -> None:
        self._execution_timer.stop()
        try:
            robot = DummyRobot.from_map(["".join(row) for row in self.map_data])
            initial_state = {
                "row": robot.row,
                "column": robot.column,
                "facing": robot.direction,
                "mined_at": [],
            }
            interpreter = Interpreter(robot)
            log = interpreter.run(self.code)
        except ValueError as error:
            self.log_view.setPlainText(f"Could not execute program: {error}")
            self.debug_view.clear()
            self.debug_snapshots = []
            self.debug_index = -1
            self.debugging = False
            self.debug_controls.setVisible(False)
            self._hide_debug_panel()
            self._clear_highlight()
            return

        self.robotStateChanged.emit(initial_state)
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
        self.debug_controls.setVisible(debug and bool(self.debug_snapshots))
        if debug:
            self._show_debug_panel()
            self.debug_view.clear()
            self.log_view.clear()
            self._clear_highlight()
        else:
            self.log_view.setPlainText("\n".join(log.lines))
            if self._execution_states:
                self._execution_timer.start()
            self._hide_debug_panel()
            self._clear_highlight()

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
        variables = "\n".join(
            f"  {name} = {value}"
            for name, value in sorted(snapshot.variables.items())
        ) or "  (none)"
        self.debug_view.setPlainText(
            f"Step {self.debug_index + 1} of {len(self.debug_snapshots)}\n"
            f"Source line: {snapshot.line_number}\n\n"
            f"Variables\n{variables}\n\n"
            f"Robot\n"
            f"  Position: row {snapshot.robot_position[0]}, "
            f"column {snapshot.robot_position[1]}\n"
            f"  Direction: {snapshot.robot_direction}"
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
        if self.output_tabs.indexOf(self.debug_view) == -1:
            self.output_tabs.addTab(self.debug_view, "Debug")
        self.output_tabs.setCurrentWidget(self.debug_view)

    def _hide_debug_panel(self) -> None:
        index = self.output_tabs.indexOf(self.debug_view)
        if index != -1:
            self.output_tabs.removeTab(index)

    def _finish_debugging(self) -> None:
        self.debugging = False
        self.debug_controls.setVisible(False)
        if self._execution_states:
            self.robotStateChanged.emit(self._execution_states[-1])
        self.log_view.setPlainText("\n".join(self.debug_log_lines))
        self._hide_debug_panel()
        self._clear_highlight()

    def _emit_next_execution_state(self) -> None:
        if self._execution_state_index >= len(self._execution_states):
            self._execution_timer.stop()
            return
        self.robotStateChanged.emit(self._execution_states[self._execution_state_index])
        self._execution_state_index += 1

    @staticmethod
    def _state_from_snapshot(snapshot) -> dict:
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
        block = self.source_view.document().findBlockByLineNumber(line_number - 1)
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

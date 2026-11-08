from PyQt6 import QtCore, QtGui, QtWidgets


class SettingsWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")

        layout = QtWidgets.QVBoxLayout(self)

        labelled_theme_toggle = QtWidgets.QWidget()
        labelled_theme_toggle.setContentsMargins(0, 0, 0, 0)

        theme_toggle_layout = QtWidgets.QHBoxLayout(labelled_theme_toggle)
        theme_toggle_layout.setContentsMargins(0, 0, 0, 0)

        theme_toggle = QtWidgets.QCheckBox()
        palette = QtWidgets.QApplication.palette()
        theme_toggle.setChecked(palette.window().color().lightness() < 128)

        theme_toggle_layout.addWidget(QtWidgets.QLabel("Enable dark mode:"))
        theme_toggle_layout.addWidget(theme_toggle)
        theme_toggle_layout.addStretch()

        layout.addWidget(labelled_theme_toggle)
        layout.addStretch()

        theme_toggle.toggled.connect(self.toggle_dark_mode)

    def toggle_dark_mode(self, enabled: bool):
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()  # ty: ignore[invalid-assignment]

        if enabled:
            palette = QtGui.QPalette()

            palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
            palette.setColor(
                QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white
            )
            palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(25, 25, 25))
            palette.setColor(
                QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53)
            )
            palette.setColor(
                QtGui.QPalette.ColorRole.ToolTipBase, QtCore.Qt.GlobalColor.white
            )
            palette.setColor(
                QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.white
            )
            palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
            palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
            palette.setColor(
                QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.white
            )
            palette.setColor(
                QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218)
            )
            palette.setColor(
                QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.white
            )

            if app:
                app.setPalette(palette)

        elif app:
            style = app.style()
            if style:
                app.setPalette(style.standardPalette())

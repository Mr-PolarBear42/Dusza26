from PyQt6 import QtCore, QtGui, QtWidgets


class IconButton(QtWidgets.QPushButton):
    def __init__(
        self,
        icon_path: str | None,
        color: QtGui.QColor,
        tooltip: str,
        text: str = "",
    ):
        super().__init__()

        if icon_path is not None:
            img = QtGui.QPixmap(icon_path)
            painter = QtGui.QPainter(img)
            painter.setCompositionMode(
                QtGui.QPainter.CompositionMode.CompositionMode_SourceIn
            )
            painter.fillRect(img.rect(), color)
            painter.end()

            self.setIcon(QtGui.QIcon(img))

        self.setIconSize(QtCore.QSize(30, 30))
        self.setText(text)
        self.setToolTip(tooltip)
        self.setFixedSize(QtCore.QSize(35, 35))

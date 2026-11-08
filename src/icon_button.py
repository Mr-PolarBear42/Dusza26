from PyQt6 import QtCore, QtGui, QtWidgets


class IconButton(QtWidgets.QPushButton):
    def __init__(self, icon_path: str, color: QtGui.QColor, tooltip: str):
        super().__init__()

        img = QtGui.QPixmap(icon_path)
        painter = QtGui.QPainter(img)
        painter.setCompositionMode(
            QtGui.QPainter.CompositionMode.CompositionMode_SourceIn
        )
        painter.fillRect(img.rect(), color)
        painter.end()

        icon = QtGui.QIcon(img)

        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(30, 30))
        self.setToolTip(tooltip)
        self.setFixedSize(QtCore.QSize(35, 35))

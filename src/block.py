import PyQt6.QtWidgets as qtw
import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg


class Block(qtw.QTreeWidgetItem):
    def __init__(self):
        super().__init__()
        self.setSizeHint(0, qtc.QSize(50, 50))

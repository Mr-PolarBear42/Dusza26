import PyQt6.QtCore as qtc
import PyQt6.QtWidgets as qtw


class Block(qtw.QTreeWidgetItem):
    def __init__(self):
        super().__init__()
        self.setSizeHint(0, qtc.QSize(50, 50))


class CommandBlock(Block):
    def __init__(self):
        super().__init__()

        self.setFlags(self.flags() & ~qtc.Qt.ItemFlag.ItemIsDropEnabled)


class ControlBlock(Block):
    def __init__(self):
        super().__init__()

        self.setFlags(self.flags() | qtc.Qt.ItemFlag.ItemIsDropEnabled)

import PyQt6.QtWidgets as qtw


class BlockProgram(qtw.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(0)

        # self.addTopLevelItems(qtw.QTreeWidgetItem())

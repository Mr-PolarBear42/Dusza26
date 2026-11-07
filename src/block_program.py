import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw

from blocks import Block, CommandBlock, ControlBlock
from block_delegate import BlockDelegate


class BlockProgram(qtw.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setItemDelegate(BlockDelegate(self))
        self.setIndentation(25)
        self.setUniformRowHeights(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)

        # Helper function to create a block
        def createBlock(cls, text, parent=None):
            block = cls()
            block.setText(0, text)

            if parent:
                parent.addChild(block)

            return block

        block1 = createBlock(CommandBlock, "Set count to 0")

        block2 = createBlock(CommandBlock, "Set fal to isThere 1")

        block3 = createBlock(CommandBlock, "Set megy to not fal")

        # While megy
        block4 = createBlock(ControlBlock, "while megy")

        # Inside while
        createBlock(CommandBlock, "Set arany to isThere 2", block4)

        block6 = createBlock(ControlBlock, "if arany", block4)

        # Inside if arany
        createBlock(CommandBlock, "step forward 1", block6)

        createBlock(CommandBlock, "mine here", block6)

        createBlock(CommandBlock, "Set count to count + 1", block6)

        # Else branch
        block10 = createBlock(ControlBlock, "else", block4)

        createBlock(CommandBlock, "step forward 1", block10)

        # More blocks inside while
        createBlock(CommandBlock, "Set fal to isThere 1", block4)

        createBlock(CommandBlock, "Set megy to not fal", block4)

        # Final block
        block14 = createBlock(Block, "print count")

        # Add top-level blocks
        self.addTopLevelItems([block1, block2, block3, block4, block14])

        # Expand all blocks
        self.expandAll()

    def dropEvent(self, event: qtg.QDropEvent):
        print(event)
        super().dropEvent(event)
        # self.expandAll()

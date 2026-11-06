import PyQt6.QtWidgets as qtw
from block import Block


class BlockProgram(qtw.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(1)
        self.setHeaderHidden(True)

        # Helper function to create a block
        def createBlock(text, parent=None):
            block = Block()
            block.setText(0, text)

            if parent:
                parent.addChild(block)

            return block

        block1 = createBlock("Set count to 0")

        block2 = createBlock("Set fal to isThere 1")

        block3 = createBlock("Set megy to not fal")

        # While megy
        block4 = createBlock("while megy")

        # Inside while
        createBlock("Set arany to isThere 2", block4)

        block6 = createBlock("if arany", block4)

        # Inside if arany
        createBlock("step forward 1", block6)

        createBlock("mine here", block6)

        createBlock("Set count to count + 1", block6)

        # Else branch
        block10 = createBlock("else", block4)

        createBlock("step forward 1", block10)

        # More blocks inside while
        createBlock("Set fal to isThere 1", block4)

        createBlock("Set megy to not fal", block4)

        # Final block
        block14 = createBlock("print count")

        # Add top-level blocks
        self.addTopLevelItems([block1, block2, block3, block4, block14])

        # Expand all blocks
        self.expandAll()

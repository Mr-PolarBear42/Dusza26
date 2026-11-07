import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw

from blocks import CommandBlock, ControlBlock


class BlockDelegate(qtw.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(
        self,
        painter: qtg.QPainter,
        option: qtw.QStyleOptionViewItem,
        index: qtc.QModelIndex,
    ):
        painter.save()

        tree: qtw.QTreeWidget = self.parent()
        item = tree.itemFromIndex(index)

        if isinstance(item, ControlBlock):
            color = qtg.QColor("#FFAB19")
        elif isinstance(item, CommandBlock):
            color = qtg.QColor("#4C97FF")
        else:
            color = qtg.QColor("#9966FF")

        rect = option.rect.adjusted(2, 2, -2, -2)

        # draw rounded block
        painter.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)

        painter.setPen(qtc.Qt.PenStyle.NoPen)
        painter.setBrush(color)

        painter.drawRoundedRect(rect, 8, 8)

        # draw text
        painter.setPen(qtg.QColor("white"))

        font = option.font
        font.setBold(True)
        painter.setFont(font)

        text_rect = rect.adjusted(10, 0, -10, 0)

        painter.drawText(
            text_rect,
            qtc.Qt.AlignmentFlag.AlignVCenter | qtc.Qt.AlignmentFlag.AlignLeft,
            index.data(qtc.Qt.ItemDataRole.DisplayRole),
        )

        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)

        size.setHeight(50)

        return size

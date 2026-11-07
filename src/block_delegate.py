import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw

from blocks import CommandBlock, ControlBlock


class BlockDelegate(qtw.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.margin = 2
        self.block_height = 50
        self.block_radius = 8

    @staticmethod
    def item_num_rows(item: qtw.QTreeWidgetItem):
        total = 1
        if item.childCount() and item.isExpanded():
            for child_index in range(item.childCount()):
                total += BlockDelegate.item_num_rows(item.child(child_index))
        return total

    @staticmethod
    def get_color(item: qtw.QTreeWidgetItem):
        if isinstance(item, ControlBlock):
            color = qtg.QColor("#FFAB19")
        elif isinstance(item, CommandBlock):
            color = qtg.QColor("#4C97FF")
        else:
            color = qtg.QColor("#9966FF")

        return color

    def paint(
        self,
        painter: qtg.QPainter,
        option: qtw.QStyleOptionViewItem,
        index: qtc.QModelIndex,
    ):
        painter.save()

        tree: qtw.QTreeWidget = self.parent()
        item: qtw.QTreeWidgetItem = tree.itemFromIndex(index)
        indentation = tree.indentation()

        color = BlockDelegate.get_color(item)

        rect = option.rect.adjusted(
            self.margin, self.margin, -self.margin, -self.margin
        )

        # draw rounded block
        painter.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)

        painter.setPen(qtc.Qt.PenStyle.NoPen)
        painter.setBrush(color)

        painter.drawRoundedRect(rect, self.block_radius, self.block_radius)

        parent = item.parent()
        parent_index = 0
        gutter_rect = rect
        while parent:
            padding = 2 * self.margin + self.block_radius
            top_left = qtc.QPoint(
                gutter_rect.left() - indentation,
                gutter_rect.top() - padding,
            )
            gutter_rect = qtc.QRect(
                top_left, qtc.QSize(20, gutter_rect.height() + padding)
            )
            painter.setBrush(BlockDelegate.get_color(parent))
            painter.drawRect(gutter_rect)

            parent = parent.parent()
            parent_index += 1

        # if item.childCount() and item.isExpanded():
        #     num_rows = self.item_num_rows(item)
        #     height = num_rows * self.block_height - self.margin * 2
        #     size = qtc.QSize(20, height)
        #     side_rect = qtc.QRect(rect.topLeft(), size)
        #     painter.drawRoundedRect(side_rect, self.block_radius, self.block_radius)

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

        size.setHeight(self.block_height)

        return size

import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

from utils.enums import Direction

from sprite_manager import SpriteManager

dir_to_arrow = {
    Direction.NORTH: "^",
    Direction.EAST: ">",
    Direction.SOUTH: "v",
    Direction.WEST: "<"
}

class MapViewer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # enable built-in hand-drag mode for smoother panning
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

        self.sprite_manager = SpriteManager()
        self.tile_size = 128  # size of each tile in pixels

        self._robot_x = 0
        self._robot_y = 0
        self._robot_face: Direction = Direction.NORTH
        self._robot_item: QtWidgets.QGraphicsPixmapItem | None = None

        self._map_data: list[list[str, str]] = None
        self._map_width = 0
        self._map_height = 0

        self.clicked = False

        self._scene_item_matrix: list[list[QtWidgets.QGraphicsPixmapItem]] | None = None

        self._scene: QtWidgets.QGraphicsScene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)

    def load_map(self, map: list[list[str]], w: int, h: int, robot_x: int, robot_y: int, robot_face: Direction):
        self._map_data = [row[:] for row in map]
        self._robot_x = robot_x
        self._robot_y = robot_y
        self._robot_face = robot_face
        self._map_width = w
        self._map_height = h

        self._scene_item_matrix = [[None for _ in range(self._map_width)] for _ in range(self._map_height)]
        
        self._render_map()

        ##render robot
        robot_sprite = self.sprite_manager.get_sprite(dir_to_arrow[self._robot_face])
        self._robot_item = QtWidgets.QGraphicsPixmapItem(robot_sprite)
        self._robot_item.setScale(self.tile_size / robot_sprite.width())
        self._robot_item.setPos(
            (self._robot_x - self._robot_y) * self.tile_size / 2,
            (self._robot_x + self._robot_y) * self.tile_size / 4 - self.tile_size / 2
        )
        self._scene.addItem(self._robot_item)

    def _render_map(self):
        self._scene.clear()
        for y in range(self._map_height):
            start_x = -y * self.tile_size / 2
            start_y = y * self.tile_size / 4
            for x in range(self._map_width):
                sprite = self.sprite_manager.get_sprite(".")

                if sprite:
                    item = QtWidgets.QGraphicsPixmapItem(sprite)
                    item.setScale(self.tile_size / sprite.width())
                    item.setPos(
                        start_x + x * self.tile_size / 2,
                        start_y + x * self.tile_size / 4,
                    )
                    self._scene.addItem(item)


        for y in range(self._map_height):
            start_x = -y * self.tile_size / 2
            start_y = y * self.tile_size / 4
            for x in range(self._map_width):
                if self._map_data[y][x] != "." and self._map_data[y][x] not in [">", "<", "^", "v"]:
                    sprite = self.sprite_manager.get_sprite(self._map_data[y][x])
                    if sprite:
                        item = QtWidgets.QGraphicsPixmapItem(sprite)
                        item.setScale(self.tile_size / sprite.width())
                        item.setPos(
                            start_x + x * self.tile_size / 2,
                            start_y + x * self.tile_size / 4 - self.tile_size / 2,
                        )
                        item.setZValue(y)
                        self._scene_item_matrix[y][x] = item
                        self._scene.addItem(item)

    def remove_item(self, x: int, y:int):
        self._scene.removeItem(self._scene_item_matrix[y][x])
        self._scene_item_matrix[y][x] = None

    def move_robot(self, x: int, y: int):
        point_x = (x - y) * self.tile_size / 2
        point_y = (x + y) * self.tile_size / 4 - self.tile_size / 2
        self._robot_item.setZValue(y)
        self._robot_item.setPos(point_x, point_y)

    def change_robot_direction(self, dir: Direction):
        self._robot_item.setPixmap(self.sprite_manager.get_sprite(dir_to_arrow[dir]))

    @QtCore.pyqtSlot(object)
    def update_robot_state(self, state: object) -> None:
        if not isinstance(state, dict):
            return
        row = state.get("row")
        column = state.get("column")
        facing = state.get("facing")
        mined_at = state.get("mined_at", ())
        if not isinstance(row, int) or not isinstance(column, int):
            return
        directions = {"^": Direction.NORTH, ">": Direction.EAST, "v": Direction.SOUTH, "<": Direction.WEST}
        direction = directions.get(facing)
        if direction is None:
            return
        self._robot_x = column
        self._robot_y = row
        self._robot_face = direction
        self.move_robot(column, row)
        self.change_robot_direction(direction)
        for mined_row, mined_column in mined_at:
            if (
                0 <= mined_row < self._map_height
                and 0 <= mined_column < self._map_width
                and self._scene_item_matrix[mined_row][mined_column] is not None
            ):
                self.remove_item(mined_column, mined_row)

    # override cursor changes while dragging
    def mousePressEvent(self, event):
        if not self.clicked:
            self.clicked = True
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # zoom the view when wheel is rotated; keep within reasonable bounds
        angle = event.angleDelta().y()
        if angle == 0:
            return
        factor = 1.0 + (angle / 480.0)  # 240 corresponds to 15Â° steps; ~1.1 per notch
        old_transform = self.transform()
        scale_factor = old_transform.m11() * factor
        # clamp between 0.1 and 10x
        if 0.5 < scale_factor < 10:
            self.scale(factor, factor)
        event.accept()

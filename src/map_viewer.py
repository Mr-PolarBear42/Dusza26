from copy import deepcopy

from PyQt6 import QtCore, QtGui, QtWidgets

from sprite_manager import SpriteManager
from utils.enums import Direction
from utils.resource_path import resource_path

dir_to_arrow = {
    Direction.NORTH: "^",
    Direction.EAST: ">",
    Direction.SOUTH: "v",
    Direction.WEST: "<",
}


class MapViewer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # enable built-in hand-drag mode for smoother panning
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        # needed because qt doesn't update the full screen by default and only moves the existing view and that breaks the windrose rendering when panning
        self.setViewportUpdateMode(
            QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self.sprite_manager = SpriteManager()
        self.tile_size = 128  # size of each tile in pixels

        self._robot_x = 0
        self._robot_y = 0
        self._robot_face: Direction = Direction.NORTH

        self.windrose_sprite = QtGui.QPixmap(
            resource_path("assets/sprites/windrose.png")
        )
        self.windrose_width = 100
        self.windrose_height = int(
            self.windrose_width
            * self.windrose_sprite.height()
            / self.windrose_sprite.width()
        )

        robot_sprite = self.sprite_manager.get_sprite(dir_to_arrow[self._robot_face])
        self._robot_item = QtWidgets.QGraphicsPixmapItem(robot_sprite)
        self._robot_item.setScale(self.tile_size / robot_sprite.width())

        self._map_data: list[list[str]] = None  # ty: ignore[invalid-assignment]
        self._map_width = 0
        self._map_height = 0

        self.clicked = False

        self._scene_item_matrix: list[list[QtWidgets.QGraphicsPixmapItem | None]] | None = None  # ty: ignore[invalid-assignment]
        self._undiscovered_blockers: list[list[QtWidgets.QGraphicsPixmapItem | None]] | None = None  # ty: ignore[invalid-assignment]

        self._scene: QtWidgets.QGraphicsScene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)

    def load_map(
        self,
        map: list[list[str]],
        w: int,
        h: int,
        robot_x: int,
        robot_y: int,
        robot_face: Direction,
    ):
        self._initial_map = map

        self._map_data = deepcopy(map)
        self._robot_x = robot_x
        self._robot_y = robot_y
        self._robot_face = robot_face
        self._map_width = w
        self._map_height = h

        self._scene_item_matrix = [  # ty: ignore[invalid-assignment]
            [None for _ in range(self._map_width)] for _ in range(self._map_height)
        ]
        self._undiscovered_blockers = [  # ty: ignore[invalid-assignment]
            [None for _ in range(self._map_width)] for _ in range(self._map_height)
        ]

        self._render_map()

        ##render robot

        self._scene.addItem(self._robot_item)
        self.change_robot_direction(self._robot_face)
        self.move_robot(self._robot_x, self._robot_y)

    def reset_map(self):
        self._map_data = deepcopy(self._initial_map)
        if self._scene_item_matrix:
            for xyz in self._scene_item_matrix:
                for item in xyz:
                    if item is not None:
                        self._scene.removeItem(item)
        if self._undiscovered_blockers:
            for xyz in self._undiscovered_blockers:
                for item in xyz:
                    if item is not None:
                        self._scene.removeItem(item)
        self._add_blockers()

    def _undiscover_cell(self, x: int, y: int):
        if self._scene_item_matrix[y][x] != None:
            self._scene.removeItem(self._scene_item_matrix[y][x])
            self._scene_item_matrix[y][x] = None  # ty: ignore[invalid-assignment]

        if self._undiscovered_blockers[y][x] != None:
            return

        blocker_sprite = self.sprite_manager.get_sprite("_")
        blocker = QtWidgets.QGraphicsPixmapItem(blocker_sprite)
        blocker.setScale(self.tile_size / blocker_sprite.width())
        blocker.setPos(
            (x - y) * self.tile_size / 2,
            (x + y) * self.tile_size / 4 - self.tile_size / 2,
        )
        blocker.setZValue(y + 1 / 8)

        self._undiscovered_blockers[y][x] = blocker
        self._scene.addItem(blocker)


    def _discover_cell(self, x: int, y: int):
        if self._undiscovered_blockers[y][x] != None:
            self._scene.removeItem(self._undiscovered_blockers[y][x])
            self._undiscovered_blockers[y][x] = None  # ty: ignore[invalid-assignment]

        if self._map_data[y][x] != None:
            if self._scene_item_matrix[y][x] or self._map_data[y][x] == ".":
                return
            sprite = self.sprite_manager.get_sprite(self._map_data[y][x])
            if sprite:
                item = QtWidgets.QGraphicsPixmapItem(sprite)
                item.setScale(self.tile_size / sprite.width())
                item.setPos(
                    (x - y) * self.tile_size / 2,
                    (x + y) * self.tile_size / 4 - self.tile_size / 2,
                )
                item.setZValue(y + 1 / 4)

                self._scene_item_matrix[y][x] = item
                self._scene.addItem(item)

    def _add_blockers(self):

        blocker_sprite = self.sprite_manager.get_sprite("_")
        for y in range(self._map_height):
            start_x = -y * self.tile_size / 2
            start_y = y * self.tile_size / 4

            for x in range(self._map_width):
                blocker = QtWidgets.QGraphicsPixmapItem(blocker_sprite)
                blocker.setScale(self.tile_size / blocker_sprite.width())
                blocker.setPos(
                    start_x + x * self.tile_size / 2,
                    start_y + x * self.tile_size / 4 - self.tile_size / 2,
                )
                blocker.setZValue(y + 1 / 8)
                self._undiscovered_blockers[y][x] = blocker
                self._scene.addItem(blocker)

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

        self._add_blockers()

    def remove_item(self, x: int, y: int):
        self._scene.removeItem(self._scene_item_matrix[y][x])
        self._scene_item_matrix[y][x] = None

    def _reload_cell(self, x: int, y: int):
        if self._scene_item_matrix[y][x] != None:
            self.remove_item(x,y)

        if self._map_data[y][x] == ".":
            return
        sprite = self.sprite_manager.get_sprite(self._map_data[y][x])
        
        if sprite:
            item = QtWidgets.QGraphicsPixmapItem(sprite)
            item.setScale(self.tile_size / sprite.width())
            item.setPos(
                (x - y) * self.tile_size / 2,
                (x + y) * self.tile_size / 4 - self.tile_size / 2,
            )
            self._scene_item_matrix[y][x] = item
            self._scene.addItem(item)

    def move_robot(self, x: int, y: int):
        point_x = (x - y) * self.tile_size / 2
        point_y = (x + y) * self.tile_size / 4 - self.tile_size / 2
        self._robot_item.setZValue(y + 1 / 2)
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
        discovered = state.get("discovered", ())
        if not isinstance(row, int) or not isinstance(column, int):
            return
        directions = {
            "^": Direction.NORTH,
            ">": Direction.EAST,
            "v": Direction.SOUTH,
            "<": Direction.WEST,
        }
        direction = directions.get(facing)
        if direction is None:
            return
        self._robot_x = column
        self._robot_y = row
        self._robot_face = direction
        self.move_robot(column, row)
        self.change_robot_direction(direction)

        is_discovered = [[False for _ in range(self._map_width)] for _ in range(self._map_height)]

        for discovered_row, discovered_column in discovered:
            is_discovered[discovered_row][discovered_column] = True

        for discovered_row, values in enumerate(self._undiscovered_blockers):
            for discovered_column, value in enumerate(values):
                if value == None:
                    if is_discovered[discovered_row][discovered_column] == False:
                        self._undiscover_cell(discovered_column, discovered_row)
                else:
                    if is_discovered[discovered_row][discovered_column] == True:
                        self._discover_cell(discovered_column, discovered_row)

        for y in range(self._map_height):
            for x in range(self._map_width):
                if is_discovered[y][x]:
                    self._reload_cell(x, y)
        for mined_row, mined_column in mined_at:
            if self._scene_item_matrix[mined_row][mined_column] is not None:
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
        factor = 1.0 + (angle / 480.0)  # 240 corresponds to 15° steps; ~1.1 per notch
        old_transform = self.transform()
        scale_factor = old_transform.m11() * factor
        # clamp between 0.1 and 10x
        if 0.5 < scale_factor < 10:
            self.scale(factor, factor)
        event.accept()

    def paintEvent(self, event: QtGui.QPaintEvent | None):
        super().paintEvent(event)

        viewport = self.viewport()

        if viewport:
            painter = QtGui.QPainter(self.viewport())
            painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

            margin = 10

            target_rect = QtCore.QRect(
                viewport.width() - self.windrose_width - margin,
                margin,
                self.windrose_width,
                self.windrose_height,
            )

            painter.drawPixmap(target_rect, self.windrose_sprite)

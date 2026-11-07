from utils.resource_path import resource_path
from PyQt6 import QtGui

class SpriteManager:
    """Manages loading and providing access to sprites for the map view."""

    def __init__(self):
        super().__init__()

        self.sprites = {
            ".": QtGui.QPixmap(resource_path("assets/sprites/ground.png")),
            "#": QtGui.QPixmap(resource_path("assets/sprites/rock.png")),
            "@": QtGui.QPixmap(resource_path("assets/sprites/gold.png")),
            ">": QtGui.QPixmap(resource_path("assets/sprites/robot_dr.png")),
            "v": QtGui.QPixmap(resource_path("assets/sprites/robot_dl.png")),
            "^": QtGui.QPixmap(resource_path("assets/sprites/robot_ur.png")),
            "<": QtGui.QPixmap(resource_path("assets/sprites/robot_ul.png"))
        }

        for name, pixmap in self.sprites.items():
            if pixmap.isNull():
                print(f"Failed to load sprite: {name}")

    def get_sprite(self, tile_type):
        return self.sprites.get(tile_type, None)
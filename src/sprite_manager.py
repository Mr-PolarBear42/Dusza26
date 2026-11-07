import os
from PyQt6 import QtGui

class SpriteManager:
    """Manages loading and providing access to sprites for the map view."""

    def __init__(self):
        super().__init__()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(base_dir)

        self.sprites = {
            ".": QtGui.QPixmap(os.path.join(base_dir, "assets/sprites/ground.png")),
            "#": QtGui.QPixmap(os.path.join(base_dir, "assets/sprites/rock.png")),
            "@": QtGui.QPixmap(os.path.join(base_dir, "assets/sprites/gold.png")),
            "ROVER": QtGui.QPixmap(os.path.join(base_dir, "assets/sprites/rover.png")),
            "PATHICON": QtGui.QPixmap(os.path.join(base_dir, "assets/sprites/path_icon.png"))
        }

        for name, pixmap in self.sprites.items():
            if pixmap.isNull():
                print(f"Failed to load sprite: {name}")

    def get_sprite(self, tile_type):
        return self.sprites.get(tile_type, None)
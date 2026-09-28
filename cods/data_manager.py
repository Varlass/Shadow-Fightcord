from data.manager import FileManage
from utils.utils import ntime
from utils.data_tools import text_to_collection, object_to_collection

from cods.game.obj.general import Player, Helmet, Armor, Melee, Range


FILES = {"WINDOWS": "windows.txt",
         "ITEMS": "items.txt",
         "USERS": "users.json"}
CACHE_TIME = 3600

class DataManager:
    def __init__(self):
        self.players: dict[int, Player] = {}
        self.windows: dict[str, dict] = {}
        self.items: dict[str, Helmet|Armor|Melee|Range] = {}

    def start(self):
        self.load_windows(FILES["WINDOWS"])
        self.load_items(FILES["ITEMS"])

    def update(self):
        ...

    def end(self):
        ...

    def load_windows(self, file: str):
        ...

    def load_items(self, file: str):
        ...

    def create_player(self):
        ...

    def get_player(self):
        ...

    def save_player(self):
        ...

    def delete_player(self):
        ...

    def cache_manager(self):
        ...
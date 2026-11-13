from data.manager import FileManager
from utils.time import ntime
from utils.data_tools import text_to_collection, object_to_collection

from cods.game.objects.general import Player, Helmet, Armor, Melee, Range


FILES = {"WINDOWS_TEXT": "windows.txt",
         "ITEMS_TEXT": "items.txt",
         "WINDOWS_DATA": "windows.txt",
         "ITEMS_DATA": "items.txt",
         "PLAYERS": "players.json"}
CACHE_TIME = 3600

class DataManager:
    def __init__(self):
        self.players: dict[int, Player] = {}
        self.windows: dict[str, dict] = {}
        self.items: dict[str, Helmet|Armor|Melee|Range] = {}

    def start(self):
        self.load_windows(FILES["WINDOWS_DATA"])
        self.load_items(FILES["ITEMS_DATA"])

    def update(self):
        self.load_windows(FILES["WINDOWS_TEXT"])
        self.load_items(FILES["ITEMS_TEXT"])

    def end(self):
        data = {}
        for player_id, player in self.players.items:
            data[str(player_id)] = object_to_collection(player)

        FileManager(FILES["PLAYERS"]).update(data)

    def load_windows(self, file: str):
        self.windows = text_to_collection(FileManager(file).read(), {})

    def load_items(self, file: str):
        self.items = text_to_collection(FileManager(file).read(), {})

    def create_player(self, player_id: int) -> Player:
        self.players[player_id] = Player()
        return self.players[player_id]

    def get_player(self, player_id: int) -> Player|None:
        if player_id in self.players:
            return self.players[player_id]

        data: dict[str, dict] = FileManager(FILES["PLAYERS"]).read()

        if str(player_id) in data:
            self.players[player_id] = data[str(player_id)]
            return self.players[player_id]

        return None

    def save_player(self, player_id: int) -> None:
        try:
            player_data: dict = object_to_collection(self.players[player_id])

            FileManager(FILES["PLAYERS"]).write(player_data)

        except KeyError:
            raise KeyError("save func used for non existent player")

    def delete_player(self):
        ...

    def cache_manager(self):
        ...
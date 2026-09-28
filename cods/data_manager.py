from data.manager import DIR, json_manage
from utils.data_tools import text_to_collection, collection_to_object
from utils.utils import ntime


FILES = {"WINDOWS": "windows.txt",
         "ITEMS": "items.txt",
         "USERS": "users.json"}
CACHE_TIME = 3600

class DataManager:
    def __init__(self):
        self.players: list[object] = []
        self.windows: dict = {}
        self.items: dict[object] = {}

    def init_data(self):
        with open(DIR/FILES["windows"], "r", encoding = "utf-8") as file:
            self.windows = text_to_collection(file.read(), {})

        with open(DIR/FILES["items"], "r", encoding = "utf-8") as file:
            self.items = collection_to_object(text_to_collection)

    def get_user(self, id: int):
        for player in self.players:
            if player.id == id:
                return player

        json_dict = json_manage.read("users")
        for player in json_dict:
            if player["id"] == id:
                player["time"] = ntime().timestamp()
                object_player = collection_to_object(player)

                self.players.append(object_player)
                return object_player

        return None

    def cache_manager(self):
        current_time = ntime().timestamp()
        self.players[:] = [player for player in self.players if player.time + CACHE_TIME >= current_time]
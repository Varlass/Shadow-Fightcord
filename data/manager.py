import json, yaml, sqlite3
from typing import Callable, Any, TextIO
from shutil import copy2
from pathlib import Path


DIR = Path(__file__).resolve().parents[0] # Путь к текущей папке.

class DefaultData: # Создание файлов при их отсутствии.
    def __init__(self, template_dir: Path = DIR/"default_data", data_dir: Path = DIR):
        self.template_dir = template_dir
        self.data_dir = data_dir

    def init_files(self) -> None:
        for source in self.template_dir.rglob("*"):
            if not source.is_file():
                continue

            relative = source.relative_to(self.template_dir)
            destination = self.data_dir / relative

            if destination.exists():
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            copy2(source, destination)


class FileManage:
    def __init__(self, file_path: Path|str):
        self.file: Path = self._get_path(file_path)
        self.handlers: dict[str, Callable] = self._get_format(self.file)


    def update(self, data: Any) -> None:
        self.handlers["update"](self, data, self.file)

    def read(self) -> Any:
        with open(self.file, mode =  "r", encoding = "utf-8") as file:
            return self.handlers["read"](file)
            

    def write(self, data: Any) -> None:
        with open(self.file, mode = "w", encoding = "utf-8") as file:
            self.handlers["write"](data, file)


    @staticmethod
    def _update_txt(self: "FileManage", data: Any, file: Path) -> None:
        with open(file, mode = "a", encoding = "utf-8") as f:
            self._write_txt(data, f)

    @staticmethod
    def _update_json(self: "FileManage", data: dict, _: Path) -> None:
        old_data = self.read() or {}
        new_data = {**old_data, **data}
        self.write(new_data)

    @staticmethod
    def _update_yaml(self: "FileManage", data: dict, _: Path) -> None:
        old_data = self.read() or {}
        new_data = {**old_data, **data}
        self.write(new_data)

    @staticmethod
    def _read_txt(file: TextIO) -> str:
        return file.read()

    @staticmethod
    def _read_json(file: TextIO) -> dict|None:
        return json.load(file)

    @staticmethod
    def _read_yaml(file: TextIO) -> dict|None:
        return yaml.safe_load(file)

    @staticmethod
    def _write_txt(data: Any, file: TextIO) -> None:
        file.write(str(data))

    @staticmethod
    def _write_json(data: dict, file: TextIO) -> None:
        json.dump(data, file, ensure_ascii = False, intent = 4)

    @staticmethod
    def _write_yaml(data, file: TextIO) -> None:
        yaml.safe_dump(data, file, allow_unicode = True, sort_keys = False)


    @staticmethod
    def _get_path(file_path: Path|str) -> Path:
        if isinstance(file_path, Path):
            return file_path

        if isinstance(file_path, str):
            return DIR/file_path

        else:
            raise TypeError(f"argument 'file_path' must be a Path or str, got {type(file_path).__name__}")

    def _get_format(self, file_path: Path) -> dict[str, Callable]:
        file_format = file_path.suffix.lower()

        if file_format in self.FORMATS:
            return self.FORMATS[file_format]

        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    FORMATS: dict[str, dict[str, Callable]] = {".txt": {"read": _read_txt,
                                                       "write": _write_txt,
                                                       "update": _update_txt},
                                              ".json": {"read": _read_json,
                                                        "write": _write_json,
                                                        "update": _update_json},
                                              ".yaml": {"read": _read_yaml,
                                                        "write": _write_yaml,
                                                        "update": _update_yaml}}


class DataBaseManage: # Работа с db.
    TYPE_MAP: dict[type, str] = {str: "TEXT",
                                 int: "INTEGER",
                                 float: "REAL",
                                 bool: "INTEGER",
                                 bytes: "BLOB"}

    def __init__(self):
        self.connections = {}

    def table_create(self, file_name: str, table_name: str|None = None, *, dir: Path = DIR, **schemes): # Создание таблицы в db.
        table_name = table_name or file_name

        columns = []
        for column_name, py_type in schemes.items():
            if not isinstance(py_type, type):
                py_type = type(py_type)

            sql_type = self.TYPE_MAP[py_type]
            columns.append(f"{column_name} {sql_type}")

        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(columns)})"

        self.execute(file_name, query, dir = dir)

    def fetch(self, file_name: str, query: str, params: list|tuple = (), *, dir: Path = DIR): # Чтение db.
        _, cursor = self._connect(file_name, dir = dir)

        cursor.execute(query, params)

        return cursor.fetchall()

    def execute(self, file_name: str, query: str, params: list|tuple = (), *, dir: Path = DIR): # Запись в db.
        conn, cursor = self._connect(file_name, dir = dir)

        if isinstance(params, (list, tuple)) and params and isinstance(params[0], (list, tuple, dict)):
            cursor.executemany(query, params)

        else:
            cursor.execute(query, params)

        conn.commit()

    def _connect(self, file_name: str, *, dir: Path = DIR): # Низкоуровневая функция подключения к db.
        if file_name not in self.connections:
            self.connections[file_name] = sqlite3.connect(dir/f"{file_name}.db")

        return self.connections[file_name], self.connections[file_name].cursor()

    def close(self, file_name: str) -> None: # Закрытие 1 db подключения.
        conn = self.connections.pop(file_name, None)
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    def close_all(self) -> None: # Закрытие всех db подключений.
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()


default_data = DefaultData()
db_manage = DataBaseManage()
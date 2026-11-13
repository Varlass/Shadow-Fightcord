from sqlite3 import connect, Connection, Row
from pathlib import Path
from typing import Any
from beartype import beartype
from dataclasses import dataclass, field
from threading import Lock

from .data_manager import DIR


__all__ = ["SQLiteManager", "Connections"]


class SQLiteManager:
    """
    A wrapper class for the SQLite library.
    """

    @beartype
    def __init__(self, file: Path|str, *, timeout: float = 5, row_factory: bool = True):
        (file_name, connection) = self._connect(file, timeout, row_factory)

        self.file_name: str = file_name
        self.connect: Connection = connection


    @beartype
    def table_create(self, table_name: str|None = None, **schemes: type):
        """
        Create SQLite table.
        """

        if not schemes:
            raise ValueError("At least one column is required.")

        table_name: str = self._quote_identifier(table_name or self.file_name)

        columns = []
        for column_name, py_type in schemes.items():
            if py_type not in TYPE_MAP:
                raise TypeError(f"Unsupported Python type: {py_type.__name__}.")

            sql_type = TYPE_MAP[py_type]
            columns.append(f"{self._quote_identifier(column_name)} {sql_type}")

        query = f"CREATE TABLE {table_name} ({', '.join(columns)})"

        self.connect.execute(query)


    def execute(self, **kwargs):
        self.connect.execute(**kwargs)

    def executemany(self, **kwargs):
        self.connect.executemany(**kwargs)


    def close(self) -> None:
        """
        Closes the connection to the file.
        """

        self.connect.close()
        connections.delete(self)


    @staticmethod
    def _quote_identifier(name: str) -> str:
        return '"' + {name.replace('"', '""')} + '"'

    def _connect(self, file: Path|str, timeout: float, row_factory: bool) -> tuple[str, Connection]:
        if isinstance(file, str):
            file_name: str = file
            file_path: Path = DIR / f"{file}.db"

        elif isinstance(file, Path):
            file_name: str = file.stem
            file_path: Path = file

        connection = connect(file_path, timeout = timeout)

        try:
            connection.execute("PRAGMA foreign_keys = ON")

            if row_factory == True:
                connection.row_factory = Row

        except Exception:
            connection.close()
            raise

        connections.add(self)

        return (file_name, connection)

TYPE_MAP: dict[type, str] = {str: "TEXT",
                             int: "INTEGER",
                             float: "REAL",
                             bool: "INTEGER",
                             bytes: "BLOB"}


@dataclass(slots = True, eq = False)
class Connections:
    managers: set[SQLiteManager] = field(default_factory = set)
    lock: Lock = field(default_factory = Lock)

    @beartype
    def add(self, manager: SQLiteManager) -> None:
        with self.lock:
            self.managers.add(manager)

    @beartype
    def delete(self, manager: SQLiteManager) -> None:
        with self.lock:
            self.managers.discard(manager)

    def close_all(self) -> None:
        with self.lock:
            managers = self.managers.copy()

            for manager in managers:
                manager.close()

connections = Connections()
from pathlib import Path
from beartype import beartype
from typing import Any

from data.manager import FileManager


log_file = FileManager("LogFile.log")

@beartype
def logger(error: Any, *, file_path: Path|str|None = None):
    if file_path != None:
        log_file = FileManager(file_path)

    log_file.write(error)
from shutil import copy2
from pathlib import Path
from beartype import beartype


__all__ = ["DIR", "DefaultData"]


DIR = Path(__file__).resolve().parents[1] # Путь к папке /data/

class DefaultData:
    """
    A class for preparing a file for data storage.
    """

    @beartype
    def __init__(self, template_dir: Path|None = None, data_dir: Path = DIR):
        self.template_dir = template_dir if template_dir is not None else self._create_template_folder()
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


    @staticmethod
    def _create_template_folder() -> Path:
        template_dir = DIR / "default_data"
        template_dir.mkdir(parents = True, exist_ok = True)

        return template_dir
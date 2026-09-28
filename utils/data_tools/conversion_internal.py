from functools import wraps
from warnings import warn
from collections.abc import Callable
from types import MethodType
from typing import Any
from dataclasses import dataclass

from .config import SYNTAX, DEFAULT_NAME, CHECKING_KEY, CHECKING_VALUE


Collection = dict|list|tuple|set

class Object:
    def __init__(self, items = None):
        self._items = items

    def __getitem__(self, key):
        if self._items is None:
            raise TypeError(f"'{type(self).__name__}' does not support indexing")

        return self._items[key]

    def __getattr__(self, attribute):
        if self._items is not None:
            return getattr(self._items, attribute)

        raise AttributeError(f"{type(self).__name__} object has no attribute {attribute}")

    def _add(self, function: Callable) -> None:
        """Adds a function to the object."""

        if not callable(function):
            raise TypeError(f"'_add' expects a callable, got {type(function).__name__}")

        setattr(self, function.__name__, MethodType(function, self))

class_cache: dict[str, object] = {}


@dataclass(slots = True, eq = False)
class Token:
    parent: "Token"|None = None
    key: Any = None
    value: Any = None

    high: int|None = None

    path: str = ""


class EmptyKeyWarning(UserWarning):
    pass

class EmptyValueWarning(UserWarning):
    pass


def normaliser(function):
    """Normalises input text into a sequence of ligical lines."""

    @wraps(function)
    def wrapper(text: str) -> list[tuple[str, int]]:
        lines = text.splitlines()
        result = []
        current_line = None
        current_number = 0

        for number, raw_line in enumerate(lines):
            line = raw_line.strip()

            if not line or line.startswith(SYNTAX["commentary"]):
                continue

            if SYNTAX["separator"] in line or line.startswith(tuple(marker for marker in SYNTAX["types"])):
                if current_line is not None:
                    result.append((current_line, "line " + str(current_number)))

                current_line = line
                current_number = number + 1

            else:
                if current_line is None:
                    raise KeyError(f"The key is missing from the string.\n{number}: {line}.")

                current_line += "\n" + line

        if current_line is not None:
            result.append((current_line, "line " + str(current_number)))

        return function(result)
    return wrapper

def checking(tokens: list[Token]) -> None:
    """Checks tokens for non-critical errors."""

    for token in tokens:
        if token.key in CHECKING_KEY:
            warn(f"Emply key at {token.path}", EmptyKeyWarning)

        if token.value in CHECKING_VALUE:
            warn(f"Emply value at {token.path}", EmptyValueWarning)


@normaliser
def text_tokeniser(text: str) -> list[Token]:
    """Converts logical lines into tokens."""

    result: list[Token] = []
    parents: list[Token] = []

    for line, path in text:
        token = Token(path = path)

        if SYNTAX["separator"] in line:
            token.parent = parents[-1] if parents else None
            token.key, token.value = map(str.strip, line.split(SYNTAX["separator"], 1))

        else:
            for marker in SYNTAX["types"]:
                if line.startswith(marker):
                    token.key = line.strip(f"{marker} ")
                    token.value = SYNTAX["types"][marker]
                    token.high = len(line) - len(line.lstrip(marker))

                    while parents and parents[-1].high >= token.high:
                        parents.pop()
                    token.parent = parents[-1] if parents else None

                    parents.append(token)

                    break

        result.append(token)

    return result

def tokeniser(data: object|Collection, core_path: str = DEFAULT_NAME) -> list[Token]:
    """Converts object and collecgion into tokens."""

    result: list[Token] = []

    def _walk(data: object|Collection, parent: Token|None = None, max_depth: int = 1, depth: int = 1, path: str = "", ) -> int:
        if isinstance(data, dict):
            items = data.items()
            temp_path = lambda key, _: f'{path}["{key}"]'

        elif isinstance(data, (list, tuple)):
            items =  enumerate(data)
            temp_path = lambda key, _: f'{path}[{key}]'

        elif isinstance(data, set):
            items =  enumerate(data)
            temp_path = lambda _, value: f'{path}{{{value!r}}}'

        else:
            items = vars(data).items()
            temp_path = lambda key, _: f'{path}.{key}'

        for key, value in items:
            current_path = temp_path(key, value)

            if isinstance(data, set): # Проверка текста.
                print(current_path)

            token = Token(parent = parent, key = key + 1, value = value, path = current_path)

            if isinstance(value, Collection):
                token.value = type(value)

            elif hasattr(value, "__dict__"):
                token.value = dict

            else:
                result.append(token)
                continue

            token.high = depth
            max_depth = max(max_depth, depth)

            result.append(token)
            max_depth = _walk(value, token, max_depth, depth + 1, current_path)

        return max_depth


    max_depth = _walk(data = data, path = core_path)

    for token in result:
        if token.high is not None:
            token.high = max_depth - token.high + 1

    return result


def text_builder(tokens: list[Token]) -> str:
    """Builds a formatted text from tokens."""

    result: list[tuple[str, Token]] = []

    for token in tokens:
        if token.value in SYNTAX["types"].values():
            marker = next(marker for marker, collection in SYNTAX["types"].items() if collection is token.value)

            result.append((f"{marker * token.high} {token.key} {marker * token.high}", token))

        else:
            parent_index = next(item for item, (_, parent_token) in enumerate(result) if parent_token is token.parent) if token.parent else -1

            result.insert(parent_index + 1, (f"{token.key}{SYNTAX["separator"]} {token.value}", token))

    return "\n".join(line for line, _ in result)

def collection_builder(tokens: list[Token], collection: Collection) -> Collection:
    """Builds a collection from tokens."""

    collections: dict[Token, tuple[Any]] = {}

    for token in tokens:
        parent = collection
        parent_path = ()

        if token.parent:
            parent_path = collections[token.parent]

            for key in parent_path:
                if isinstance(parent, set):
                    parent = next(item for item in parent if item == key)

                else:
                    parent = parent[key]

        if len(parent_path) == 1:
            key = parent_path[0]

        if isinstance(parent, dict):
            new_parent = {**parent, token.key: token.value}
            coolection = {**collection, parent_path: new_parent}

        if isinstance(parent, list):
            new_parent = [*parent, token.value]

        if isinstance(parent, tuple):
            new_parent = (*parent, token.value)

        if isinstance(parent, set):
            new_parent = {*parent, token.value}

    return collection

def object_builder(tokens: list[Token], functions: list[Callable]|None, class_name: str) -> Object:
    """Builds an Object from tokens."""

    if class_name not in class_cache.keys():
        class_cache[class_name] = type(class_name, (Object,), {})
    ClassObject = class_cache[class_name]
    obj = ClassObject()

    stack = []

    for token in tokens:
        if token["high"]:
            while stack and stack[-1]["high"] <= token["high"]:
                stack.pop()

        parent = stack[-1]["node"] if stack else obj
        value = token["value"]

        if value is dict:
            value = ClassObject()

        elif value in (list, set):
            value = ClassObject(value())

        if parent._items is None:
            key = token["key"].replace(" ", "_")
            setattr(parent, key, value)

        elif isinstance(parent._items, list):
            parent._items.append(value)

        elif isinstance(parent._items, set):
            parent._items.add(value)

        if token["high"]:
            stack.append({"node": value,
                          "high": token["high"]})

    if functions is not None:
        for function in functions:
            obj._add(function)

    return obj
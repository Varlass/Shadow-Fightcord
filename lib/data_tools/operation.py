from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    path: tuple
    parent: object
    key: object
    value: object

MISSING = object()


def fetch(collection: list|dict, *, target_path: Any = MISSING , target_value: Any = MISSING) -> list[Node]: # Поиск узла.
    result = []

    if target_path is not MISSING:
        target_path = tuple(target_path.split("."))

    for node in _walk(collection):
        if (target_path is not MISSING and target_path == node.path[-len(target_path):]) or (target_value is not MISSING and target_value == node.value):
            result.append(node)

    return result

def edit(collection: list|dict, change: Any, *, target_path: Any = MISSING , target_value: Any = MISSING): # Изменение значения узла.
    for node in fetch(collection, target_path = target_path, target_value = target_value):
        value = change(node.value) if callable(change) else change
        node.parent[node.key] = value


def _walk(obj, path = (), parent = None, key = None): # Рекурсивный обход контейнера.
    if parent is not None:
        yield Node(path = path, parent = parent, key = key, value = obj)

    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _walk(value, path + (key,), obj, key)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from _walk(value, path + (index,), obj, index)
SYNTAX = {
    "types": {
        "=": dict,
        "-": list,
        "~": set,
        "%": tuple
    },
    "commentary": "#",
    "separator": ":",
    "escape": ""
}

DEFAULT_NAME: str = "Object"

CHECKING_KEY = frozenset({""})
CHECKING_VALUE = frozenset()
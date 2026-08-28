from typing import Callable, Dict, Any
import inspect

FUNCTIONS: Dict[str, Dict[str, Any]] = {}

def register(name: str = None, description: str = ""):
    def deco(fn: Callable):
        key = name or f"{fn.__module__}.{fn.__name__}"
        FUNCTIONS[key] = {
            "fn": fn,
            "description": description,
            "signature": str(inspect.signature(fn))
        }
        return fn
    return deco

def list_functions():
    return {k: {"description": v["description"], "signature": v["signature"]} for k, v in FUNCTIONS.items()}

def get_function(name: str):
    return FUNCTIONS.get(name)

import os
import sys


def ensure_directory(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def build_data_path(*parts: str) -> str:
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, *parts)


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)
    return os.path.join(base_path, relative_path)

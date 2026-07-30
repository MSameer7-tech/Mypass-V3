import os
import sys


def ensure_directory(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def build_data_path(*parts: str) -> str:
    base_dir = os.environ.get("MYPASS_DATA_DIR")
    if not base_dir:
        home_dir = os.path.expanduser("~")
        if not os.access(home_dir, os.W_OK):
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".local_data")
        else:
            base_dir = home_dir
    return os.path.join(base_dir, *parts)


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)
    return os.path.join(base_path, relative_path)

import glob
from os.path import dirname, isfile

def fetch_active_plugins():
    base_path = dirname(__file__)
    python_files = glob.glob(base_path + "/*/*.py")

    valid_plugins = [
        (((file_path.replace(base_path, "")).replace("/", "."))[:-3])
        for file_path in python_files
        if isfile(file_path) and file_path.endswith(".py") and not file_path.endswith("__init__.py")
    ]

    return valid_plugins

ALL_MODULES = sorted(fetch_active_plugins())
__all__ = ALL_MODULES + ["ALL_MODULES"]
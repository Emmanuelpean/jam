import json
import os


def open_json(filepath: str) -> list[dict]:
    """Open a file and return its content
    :param filepath: The json file to open
    :return: The contents of the file"""

    base_dir = str(os.path.dirname(__file__))
    path = os.path.join(base_dir, "../..", filepath)
    with open(path, "r", encoding="utf8") as ofile:
        return json.load(ofile)

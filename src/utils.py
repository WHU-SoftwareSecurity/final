import json
from typing import Dict, Union, List
from pathlib import PurePath


def load_json(json_path: Union[str, PurePath]) -> Union[Dict, List]:
    with open(json_path, "r", encoding="utf8") as f:
        return json.loads(f.read())

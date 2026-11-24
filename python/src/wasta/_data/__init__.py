from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load(name: str) -> Any:
    return json.loads(files(__name__).joinpath(name).read_text(encoding="utf-8"))

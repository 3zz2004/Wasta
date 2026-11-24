from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SPEC_DIR = Path(__file__).resolve().parents[2] / "spec"


def load_spec(name: str) -> Any:
    """Shared test vectors live in /spec so the JS and Python packages are held to the same answers."""
    return json.loads((SPEC_DIR / f"{name}.json").read_text(encoding="utf-8"))

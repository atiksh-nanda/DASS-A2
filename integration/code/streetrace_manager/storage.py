from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"crew_members": []}

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "crew_members" not in data or not isinstance(data["crew_members"], list):
            data["crew_members"] = []

        return data

    def write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

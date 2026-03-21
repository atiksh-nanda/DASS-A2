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
            return {
                "crew_members": [],
                "role_skills": [],
                "cars": [],
                "spare_parts": [],
                "tools": [],
                "cash_balance": 0.0,
                "races": [],
            }

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "crew_members" not in data or not isinstance(data["crew_members"], list):
            data["crew_members"] = []
        if "role_skills" not in data or not isinstance(data["role_skills"], list):
            data["role_skills"] = []
        if "cars" not in data or not isinstance(data["cars"], list):
            data["cars"] = []
        if "spare_parts" not in data or not isinstance(data["spare_parts"], list):
            data["spare_parts"] = []
        if "tools" not in data or not isinstance(data["tools"], list):
            data["tools"] = []
        if "cash_balance" not in data:
            data["cash_balance"] = 0.0
        if "races" not in data or not isinstance(data["races"], list):
            data["races"] = []

        return data

    def write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

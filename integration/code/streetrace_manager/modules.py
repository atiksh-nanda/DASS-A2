from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import CrewMember
from streetrace_manager.storage import JsonStore


class RegistrationModule:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def register_member(self, name: str, role: str) -> CrewMember:
        clean_name = name.strip()
        clean_role = role.strip().lower()

        if not clean_name:
            raise ValueError("Name cannot be empty.")
        if not clean_role:
            raise ValueError("Role cannot be empty.")

        data = self.store.read()
        existing_names = {member["name"].lower() for member in data["crew_members"]}
        if clean_name.lower() in existing_names:
            raise ValueError(f"Crew member '{clean_name}' is already registered.")

        member = CrewMember(name=clean_name, role=clean_role)
        data["crew_members"].append(asdict(member))
        self.store.write(data)
        return member

    def list_members(self) -> Iterable[CrewMember]:
        data = self.store.read()
        for item in data["crew_members"]:
            yield CrewMember(name=item["name"], role=item["role"])

    def remove_member(self, name: str) -> bool:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Name cannot be empty.")

        data = self.store.read()
        original_count = len(data["crew_members"])
        data["crew_members"] = [
            member for member in data["crew_members"] if member["name"].lower() != clean_name.lower()
        ]

        removed = len(data["crew_members"]) < original_count
        if removed:
            self.store.write(data)
        return removed

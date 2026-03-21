from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import RoleSkill
from streetrace_manager.storage import JsonStore


class CrewManagementModule:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def _member_exists(self, name: str) -> bool:
        """Check if crew member exists in registration data."""
        data = self.store.read()
        return any(
            member["name"].lower() == name.lower()
            for member in data["crew_members"]
        )

    def assign_role(self, member_name: str, role: str, skill_level: int) -> RoleSkill:
        """Assign a role with skill level to a crew member."""
        clean_name = member_name.strip()
        clean_role = role.strip().lower()

        if not clean_name:
            raise ValueError("Name cannot be empty.")
        if not clean_role:
            raise ValueError("Role cannot be empty.")
        if not 1 <= skill_level <= 5:
            raise ValueError("Skill level must be between 1 and 5.")

        # Enforce business rule: crew member must be registered first
        if not self._member_exists(clean_name):
            raise ValueError(f"Crew member '{clean_name}' is not registered.")

        data = self.store.read()
        # Check if role skill already exists
        for skill in data["role_skills"]:
            if (
                skill["member_name"].lower() == clean_name.lower()
                and skill["role"].lower() == clean_role
            ):
                # Update existing
                skill["skill_level"] = skill_level
                self.store.write(data)
                return RoleSkill(member_name=clean_name, role=clean_role, skill_level=skill_level)

        # Add new
        role_skill = RoleSkill(member_name=clean_name, role=clean_role, skill_level=skill_level)
        data["role_skills"].append(asdict(role_skill))
        self.store.write(data)
        return role_skill

    def list_role_skills(self, member_name: str | None = None) -> Iterable[RoleSkill]:
        """List role skills for a member, or all if member_name is None."""
        data = self.store.read()
        for skill in data["role_skills"]:
            if member_name is None or skill["member_name"].lower() == member_name.lower():
                yield RoleSkill(
                    member_name=skill["member_name"],
                    role=skill["role"],
                    skill_level=skill["skill_level"],
                )

    def remove_role(self, member_name: str, role: str) -> bool:
        """Remove a role assignment from a crew member."""
        clean_name = member_name.strip()
        clean_role = role.strip().lower()

        if not clean_name:
            raise ValueError("Name cannot be empty.")
        if not clean_role:
            raise ValueError("Role cannot be empty.")

        data = self.store.read()
        original_count = len(data["role_skills"])
        data["role_skills"] = [
            skill
            for skill in data["role_skills"]
            if not (
                skill["member_name"].lower() == clean_name.lower()
                and skill["role"].lower() == clean_role
            )
        ]

        removed = len(data["role_skills"]) < original_count
        if removed:
            self.store.write(data)
        return removed

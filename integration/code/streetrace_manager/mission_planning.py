from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import Mission
from streetrace_manager.storage import JsonStore


class MissionPlanningModule:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def create_mission(self, name: str, mission_type: str, required_roles: list[str]) -> Mission:
        clean_name = name.strip()
        clean_type = mission_type.strip().lower()
        clean_roles = [role.strip().lower() for role in required_roles if role.strip()]

        if not clean_name:
            raise ValueError("Mission name cannot be empty.")
        if not clean_type:
            raise ValueError("Mission type cannot be empty.")
        if not clean_roles:
            raise ValueError("At least one required role is needed.")

        data = self.store.read()
        if any(m["name"].lower() == clean_name.lower() for m in data["missions"]):
            raise ValueError(f"Mission '{clean_name}' already exists.")

        mission = Mission(
            name=clean_name,
            mission_type=clean_type,
            required_roles=clean_roles,
            assigned_members=[],
            status="planned",
        )
        data["missions"].append(asdict(mission))
        self.store.write(data)
        return mission

    def list_missions(self) -> Iterable[Mission]:
        data = self.store.read()
        for item in data["missions"]:
            yield Mission(
                name=item["name"],
                mission_type=item["mission_type"],
                required_roles=item["required_roles"],
                assigned_members=item["assigned_members"],
                status=item["status"],
            )

    def assign_member(self, mission_name: str, member_name: str, role: str) -> bool:
        clean_mission = mission_name.strip()
        clean_member = member_name.strip()
        clean_role = role.strip().lower()

        if not clean_mission or not clean_member or not clean_role:
            raise ValueError("Mission, member, and role are required.")

        data = self.store.read()
        mission = next((m for m in data["missions"] if m["name"].lower() == clean_mission.lower()), None)
        if mission is None:
            return False

        if clean_role not in mission["required_roles"]:
            raise ValueError(f"Role '{clean_role}' is not required by mission '{mission['name']}'.")

        has_role = any(
            rs["member_name"].lower() == clean_member.lower() and rs["role"].lower() == clean_role
            for rs in data["role_skills"]
        )
        if not has_role:
            raise ValueError(f"Crew member '{clean_member}' does not have role '{clean_role}'.")

        already_assigned = any(
            am["member_name"].lower() == clean_member.lower() and am["role"].lower() == clean_role
            for am in mission["assigned_members"]
        )
        if not already_assigned:
            mission["assigned_members"].append({"member_name": clean_member, "role": clean_role})
            self.store.write(data)
        return True

    def start_mission(self, mission_name: str) -> tuple[bool, list[str]]:
        clean_mission = mission_name.strip()
        if not clean_mission:
            raise ValueError("Mission name cannot be empty.")

        data = self.store.read()
        mission = next((m for m in data["missions"] if m["name"].lower() == clean_mission.lower()), None)
        if mission is None:
            return False, []

        assigned_roles = {item["role"].lower() for item in mission["assigned_members"]}
        missing_roles = [role for role in mission["required_roles"] if role.lower() not in assigned_roles]
        if missing_roles:
            return False, missing_roles

        mission["status"] = "in_progress"
        self.store.write(data)
        return True, []

    def complete_mission(self, mission_name: str) -> bool:
        clean_mission = mission_name.strip()
        if not clean_mission:
            raise ValueError("Mission name cannot be empty.")

        data = self.store.read()
        mission = next((m for m in data["missions"] if m["name"].lower() == clean_mission.lower()), None)
        if mission is None:
            return False

        mission["status"] = "completed"
        self.store.write(data)
        return True

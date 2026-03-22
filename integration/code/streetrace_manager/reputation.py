from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import Reputation, ReputationLog
from streetrace_manager.storage import JsonStore


class ReputationModule:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def add_points(self, member_name: str, points: int, reason: str) -> Reputation:
        return self._apply_change(member_name=member_name, change=abs(points), reason=reason)

    def deduct_points(self, member_name: str, points: int, reason: str) -> Reputation:
        return self._apply_change(member_name=member_name, change=-abs(points), reason=reason)

    def list_reputations(self) -> Iterable[Reputation]:
        data = self.store.read()
        ordered = sorted(data["reputations"], key=lambda item: (-item["points"], item["member_name"].lower()))
        for item in ordered:
            yield Reputation(member_name=item["member_name"], points=item["points"])

    def list_logs(self, member_name: str | None = None) -> Iterable[ReputationLog]:
        data = self.store.read()
        for item in data["reputation_logs"]:
            if member_name is None or item["member_name"].lower() == member_name.lower():
                yield ReputationLog(
                    member_name=item["member_name"],
                    change=item["change"],
                    reason=item["reason"],
                )

    def _apply_change(self, member_name: str, change: int, reason: str) -> Reputation:
        clean_name = member_name.strip()
        clean_reason = reason.strip()

        if not clean_name:
            raise ValueError("Member name cannot be empty.")
        if change == 0:
            raise ValueError("Change in points cannot be zero.")
        if not clean_reason:
            raise ValueError("Reason cannot be empty.")

        data = self.store.read()
        is_registered = any(member["name"].lower() == clean_name.lower() for member in data["crew_members"])
        if not is_registered:
            raise ValueError(f"Crew member '{clean_name}' is not registered.")

        reputation = next(
            (item for item in data["reputations"] if item["member_name"].lower() == clean_name.lower()),
            None,
        )
        if reputation is None:
            reputation = {"member_name": clean_name, "points": 0}
            data["reputations"].append(reputation)

        reputation["points"] += change

        log = ReputationLog(member_name=clean_name, change=change, reason=clean_reason)
        data["reputation_logs"].append(asdict(log))
        self.store.write(data)

        return Reputation(member_name=reputation["member_name"], points=reputation["points"])

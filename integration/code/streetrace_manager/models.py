from dataclasses import dataclass


@dataclass(slots=True)
class CrewMember:
    name: str
    role: str

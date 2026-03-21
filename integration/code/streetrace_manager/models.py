from dataclasses import dataclass


@dataclass(slots=True)
class CrewMember:
    name: str
    role: str


@dataclass(slots=True)
class RoleSkill:
    member_name: str
    role: str
    skill_level: int  # 1-5 scale

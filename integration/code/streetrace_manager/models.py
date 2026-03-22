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


@dataclass(slots=True)
class Car:
    name: str
    model: str
    status: str  # "available", "damaged", "in_use"


@dataclass(slots=True)
class SparePart:
    name: str
    quantity: int


@dataclass(slots=True)
class Tool:
    name: str
    quantity: int


@dataclass(slots=True)
class Race:
    name: str
    location: str
    driver_name: str
    car_name: str
    status: str  # "planned", "in_progress", "completed"


@dataclass(slots=True)
class RaceResult:
    race_name: str
    driver_name: str
    position: int
    prize_money: float
    car_damaged: bool


@dataclass(slots=True)
class DriverRanking:
    driver_name: str
    points: int
    races_run: int
    wins: int


@dataclass(slots=True)
class Mission:
    name: str
    mission_type: str
    required_roles: list[str]
    assigned_members: list[dict[str, str]]
    status: str  # "planned", "in_progress", "completed"


@dataclass(slots=True)
class VehicleRepair:
    car_name: str
    mechanic_name: str
    spare_part_name: str
    spare_part_qty: int
    repair_cost: float
    status: str  # "completed"


@dataclass(slots=True)
class Reputation:
    member_name: str
    points: int


@dataclass(slots=True)
class ReputationLog:
    member_name: str
    change: int
    reason: str

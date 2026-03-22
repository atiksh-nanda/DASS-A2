from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from streetrace_manager.crew_management import CrewManagementModule
from streetrace_manager.inventory import InventoryModule
from streetrace_manager.mission_planning import MissionPlanningModule
from streetrace_manager.race_management import RaceManagementModule
from streetrace_manager.registration import RegistrationModule
from streetrace_manager.reputation import ReputationModule
from streetrace_manager.results import ResultsModule
from streetrace_manager.storage import JsonStore
from streetrace_manager.vehicle_repair import VehicleRepairModule


@pytest.fixture
def modules(tmp_path: Path) -> dict[str, object]:
    store = JsonStore(tmp_path / "integration_test.json")
    return {
        "store": store,
        "registration": RegistrationModule(store),
        "crew": CrewManagementModule(store),
        "inventory": InventoryModule(store),
        "race": RaceManagementModule(store),
        "results": ResultsModule(store),
        "mission": MissionPlanningModule(store),
        "repair": VehicleRepairModule(store),
        "reputation": ReputationModule(store),
    }


def test_register_driver_then_enter_race_success(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]

    registration.register_member("Ari", "driver")
    crew.assign_role("Ari", "driver", 4)
    inventory.add_car("Falcon", "Mazda RX7")

    created_race = race.create_race("Night Sprint", "Downtown", "Ari", "Falcon")

    assert created_race.status == "planned"
    assert created_race.driver_name == "Ari"
    assert created_race.car_name == "Falcon"


def test_enter_race_without_registered_driver_fails(modules: dict[str, object]) -> None:
    inventory = modules["inventory"]
    race = modules["race"]

    inventory.add_car("Tempest", "Nissan 370Z")

    with pytest.raises(ValueError, match="not registered"):
        race.create_race("Harbor Run", "Harbor", "Ghost", "Tempest")


def test_complete_race_updates_result_rankings_and_inventory_cash(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]
    results = modules["results"]

    registration.register_member("Mika", "driver")
    crew.assign_role("Mika", "driver", 5)
    inventory.add_car("Nova", "Toyota Supra")
    race.create_race("Tunnel Clash", "Tunnel", "Mika", "Nova")

    result = results.record_result(
        race_name="Tunnel Clash",
        driver_name="Mika",
        position=1,
        prize_money=1500.0,
        car_damaged=False,
    )

    assert result.race_name == "Tunnel Clash"
    assert inventory.get_cash_balance() == 1500.0

    race_list = list(race.list_races())
    assert race_list[0].status == "completed"

    rankings = list(results.list_rankings())
    assert rankings[0].driver_name == "Mika"
    assert rankings[0].wins == 1
    assert rankings[0].points == 10


def test_assign_mission_validates_required_roles(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    mission = modules["mission"]

    registration.register_member("Jin", "driver")
    registration.register_member("Nora", "mechanic")
    crew.assign_role("Jin", "driver", 4)
    crew.assign_role("Nora", "mechanic", 4)

    mission.create_mission("Rescue Drift", "rescue", ["driver", "mechanic"])
    mission.assign_member("Rescue Drift", "Jin", "driver")

    can_start, missing_roles = mission.start_mission("Rescue Drift")
    assert can_start is False
    assert "mechanic" in missing_roles

    mission.assign_member("Rescue Drift", "Nora", "mechanic")
    can_start_after_fix, missing_after_fix = mission.start_mission("Rescue Drift")
    assert can_start_after_fix is True
    assert missing_after_fix == []


def test_car_damaged_in_result_then_repair_updates_inventory(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]
    results = modules["results"]
    repair = modules["repair"]

    registration.register_member("Rio", "driver")
    registration.register_member("Ken", "mechanic")
    crew.assign_role("Rio", "driver", 5)
    crew.assign_role("Ken", "mechanic", 5)

    inventory.add_car("Viper", "Dodge Viper")
    inventory.add_spare_part("Turbo Kit", 3)
    inventory.add_cash(1000.0)

    race.create_race("Bridge Blitz", "Bridge", "Rio", "Viper")
    results.record_result(
        race_name="Bridge Blitz",
        driver_name="Rio",
        position=2,
        prize_money=500.0,
        car_damaged=True,
    )

    cars_before_repair = list(inventory.list_cars())
    assert cars_before_repair[0].status == "damaged"

    repair_record = repair.repair_vehicle(
        car_name="Viper",
        mechanic_name="Ken",
        spare_part_name="Turbo Kit",
        spare_part_qty=2,
        repair_cost=400.0,
    )

    assert repair_record.status == "completed"

    cars_after_repair = list(inventory.list_cars())
    assert cars_after_repair[0].status == "available"

    spare_parts = list(inventory.list_spare_parts())
    assert spare_parts[0].name == "Turbo Kit"
    assert spare_parts[0].quantity == 1

    assert inventory.get_cash_balance() == 1100.0


def test_reputation_change_requires_registered_member(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    reputation = modules["reputation"]

    with pytest.raises(ValueError, match="not registered"):
        reputation.add_points("Unlisted", 10, "Won a small race")

    registration.register_member("Lia", "strategist")
    updated = reputation.add_points("Lia", 12, "Clean mission planning")

    assert updated.member_name == "Lia"
    assert updated.points == 12


def test_registered_member_without_driver_role_cannot_enter_race(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    inventory = modules["inventory"]
    race = modules["race"]

    registration.register_member("Omar", "crew")
    inventory.add_car("Comet", "Mitsubishi Evo")

    with pytest.raises(ValueError, match="does not have the driver role"):
        race.create_race("Hill Dash", "Hill", "Omar", "Comet")


def test_unavailable_car_cannot_be_used_in_race(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]

    registration.register_member("Kira", "driver")
    crew.assign_role("Kira", "driver", 4)
    inventory.add_car("Blaze", "Subaru WRX")
    inventory.update_car_status("Blaze", "damaged")

    with pytest.raises(ValueError, match="not available"):
        race.create_race("Cliff Run", "Cliffside", "Kira", "Blaze")


def test_duplicate_race_result_is_blocked(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]
    results = modules["results"]

    registration.register_member("Zed", "driver")
    crew.assign_role("Zed", "driver", 5)
    inventory.add_car("Orbit", "BMW M3")
    race.create_race("Metro Rush", "Metro", "Zed", "Orbit")

    results.record_result("Metro Rush", "Zed", 1, 1000.0, False)
    with pytest.raises(ValueError, match="already recorded"):
        results.record_result("Metro Rush", "Zed", 2, 200.0, False)


def test_record_result_with_wrong_driver_is_blocked(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]
    results = modules["results"]

    registration.register_member("Ivy", "driver")
    registration.register_member("Noel", "driver")
    crew.assign_role("Ivy", "driver", 3)
    crew.assign_role("Noel", "driver", 5)
    inventory.add_car("Sting", "Audi R8")
    race.create_race("Port Loop", "Port", "Ivy", "Sting")

    with pytest.raises(ValueError, match="is assigned to driver"):
        results.record_result("Port Loop", "Noel", 1, 1200.0, False)


def test_repair_requires_registered_mechanic(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]
    results = modules["results"]
    repair = modules["repair"]

    registration.register_member("Dax", "driver")
    crew.assign_role("Dax", "driver", 4)
    inventory.add_car("Raven", "Mazda MX-5")
    inventory.add_spare_part("Brake Pad", 5)
    inventory.add_cash(500.0)
    race.create_race("Dock Raid", "Dock", "Dax", "Raven")
    results.record_result("Dock Raid", "Dax", 3, 200.0, True)

    with pytest.raises(ValueError, match="is not registered"):
        repair.repair_vehicle("Raven", "Unknown", "Brake Pad", 1, 100.0)


def test_repair_requires_mechanic_role(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]
    results = modules["results"]
    repair = modules["repair"]

    registration.register_member("Sol", "driver")
    registration.register_member("Mina", "crew")
    crew.assign_role("Sol", "driver", 4)
    inventory.add_car("Quake", "Ford Mustang")
    inventory.add_spare_part("Axle", 2)
    inventory.add_cash(500.0)
    race.create_race("Ring Run", "Ring", "Sol", "Quake")
    results.record_result("Ring Run", "Sol", 2, 300.0, True)

    with pytest.raises(ValueError, match="does not have mechanic role"):
        repair.repair_vehicle("Quake", "Mina", "Axle", 1, 120.0)


def test_repair_fails_on_insufficient_parts_and_cash(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    inventory = modules["inventory"]
    race = modules["race"]
    results = modules["results"]
    repair = modules["repair"]

    registration.register_member("Ren", "driver")
    registration.register_member("Tao", "mechanic")
    crew.assign_role("Ren", "driver", 5)
    crew.assign_role("Tao", "mechanic", 5)
    inventory.add_car("Pulse", "Honda Civic")
    inventory.add_spare_part("ECU", 1)
    inventory.add_cash(300.0)
    race.create_race("Bypass", "Bypass", "Ren", "Pulse")
    results.record_result("Bypass", "Ren", 2, 200.0, True)

    with pytest.raises(ValueError, match="Insufficient spare part quantity"):
        repair.repair_vehicle("Pulse", "Tao", "ECU", 2, 100.0)

    with pytest.raises(ValueError, match="Insufficient funds"):
        repair.repair_vehicle("Pulse", "Tao", "ECU", 1, 1000.0)


def test_mission_assignment_and_reputation_input_validation(modules: dict[str, object]) -> None:
    registration = modules["registration"]
    crew = modules["crew"]
    mission = modules["mission"]
    reputation = modules["reputation"]

    registration.register_member("Eli", "driver")
    mission.create_mission("Courier", "delivery", ["mechanic"])

    with pytest.raises(ValueError, match="is not required"):
        mission.assign_member("Courier", "Eli", "driver")

    crew.assign_role("Eli", "driver", 3)
    with pytest.raises(ValueError, match="cannot be zero"):
        reputation.add_points("Eli", 0, "No-op")

    with pytest.raises(ValueError, match="Reason cannot be empty"):
        reputation.add_points("Eli", 3, "")

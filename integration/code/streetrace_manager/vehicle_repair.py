from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import VehicleRepair
from streetrace_manager.storage import JsonStore


class VehicleRepairModule:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def repair_vehicle(
        self,
        car_name: str,
        mechanic_name: str,
        spare_part_name: str,
        spare_part_qty: int,
        repair_cost: float,
    ) -> VehicleRepair:
        clean_car = car_name.strip()
        clean_mechanic = mechanic_name.strip()
        clean_part = spare_part_name.strip()

        if not clean_car:
            raise ValueError("Car name cannot be empty.")
        if not clean_mechanic:
            raise ValueError("Mechanic name cannot be empty.")
        if not clean_part:
            raise ValueError("Spare part name cannot be empty.")
        if spare_part_qty <= 0:
            raise ValueError("Spare part quantity must be greater than 0.")
        if repair_cost < 0:
            raise ValueError("Repair cost cannot be negative.")

        data = self.store.read()

        car = next((item for item in data["cars"] if item["name"].lower() == clean_car.lower()), None)
        if car is None:
            raise ValueError(f"Car '{clean_car}' does not exist.")
        if car["status"].lower() != "damaged":
            raise ValueError(f"Car '{clean_car}' is not damaged.")

        is_registered = any(member["name"].lower() == clean_mechanic.lower() for member in data["crew_members"])
        if not is_registered:
            raise ValueError(f"Mechanic '{clean_mechanic}' is not registered.")

        has_mechanic_role = any(
            role_skill["member_name"].lower() == clean_mechanic.lower()
            and role_skill["role"].lower() == "mechanic"
            for role_skill in data["role_skills"]
        )
        if not has_mechanic_role:
            raise ValueError(f"Crew member '{clean_mechanic}' does not have mechanic role.")

        spare_part = next(
            (item for item in data["spare_parts"] if item["name"].lower() == clean_part.lower()),
            None,
        )
        if spare_part is None:
            raise ValueError(f"Spare part '{clean_part}' not found in inventory.")
        if spare_part["quantity"] < spare_part_qty:
            raise ValueError(
                f"Insufficient spare part quantity for '{clean_part}'. "
                f"Available: {spare_part['quantity']}, required: {spare_part_qty}."
            )

        if data.get("cash_balance", 0.0) < repair_cost:
            raise ValueError(
                f"Insufficient funds. Balance: ${data.get('cash_balance', 0.0):.2f}, "
                f"required: ${repair_cost:.2f}."
            )

        spare_part["quantity"] -= spare_part_qty
        if spare_part["quantity"] == 0:
            data["spare_parts"] = [
                item for item in data["spare_parts"] if item["name"].lower() != clean_part.lower()
            ]

        data["cash_balance"] = float(data.get("cash_balance", 0.0)) - repair_cost
        car["status"] = "available"

        repair_record = VehicleRepair(
            car_name=car["name"],
            mechanic_name=clean_mechanic,
            spare_part_name=clean_part,
            spare_part_qty=spare_part_qty,
            repair_cost=repair_cost,
            status="completed",
        )
        data["vehicle_repairs"].append(asdict(repair_record))
        self.store.write(data)
        return repair_record

    def list_repairs(self) -> Iterable[VehicleRepair]:
        data = self.store.read()
        for item in data["vehicle_repairs"]:
            yield VehicleRepair(
                car_name=item["car_name"],
                mechanic_name=item["mechanic_name"],
                spare_part_name=item["spare_part_name"],
                spare_part_qty=item["spare_part_qty"],
                repair_cost=item["repair_cost"],
                status=item["status"],
            )

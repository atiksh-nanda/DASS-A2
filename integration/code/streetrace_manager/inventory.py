from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import Car, SparePart, Tool
from streetrace_manager.storage import JsonStore


class InventoryModule:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    # ===== Car Management =====
    def add_car(self, name: str, model: str) -> Car:
        """Add a new car to inventory with 'available' status."""
        clean_name = name.strip()
        clean_model = model.strip()

        if not clean_name:
            raise ValueError("Car name cannot be empty.")
        if not clean_model:
            raise ValueError("Car model cannot be empty.")

        data = self.store.read()
        # Check for duplicate car names
        existing_cars = {car["name"].lower() for car in data["cars"]}
        if clean_name.lower() in existing_cars:
            raise ValueError(f"Car '{clean_name}' already exists in inventory.")

        car = Car(name=clean_name, model=clean_model, status="available")
        data["cars"].append(asdict(car))
        self.store.write(data)
        return car

    def list_cars(self) -> Iterable[Car]:
        """List all cars in inventory."""
        data = self.store.read()
        for item in data["cars"]:
            yield Car(name=item["name"], model=item["model"], status=item["status"])

    def remove_car(self, name: str) -> bool:
        """Remove a car from inventory."""
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Car name cannot be empty.")

        data = self.store.read()
        original_count = len(data["cars"])
        data["cars"] = [car for car in data["cars"] if car["name"].lower() != clean_name.lower()]

        removed = len(data["cars"]) < original_count
        if removed:
            self.store.write(data)
        return removed

    def update_car_status(self, name: str, status: str) -> bool:
        """Update car status (available, damaged, in_use)."""
        clean_name = name.strip()
        clean_status = status.strip().lower()

        if clean_status not in ("available", "damaged", "in_use"):
            raise ValueError("Status must be 'available', 'damaged', or 'in_use'.")

        data = self.store.read()
        for car in data["cars"]:
            if car["name"].lower() == clean_name.lower():
                car["status"] = clean_status
                self.store.write(data)
                return True
        return False

    # ===== Spare Parts Management =====
    def add_spare_part(self, name: str, quantity: int) -> SparePart:
        """Add spare parts to inventory or increase existing quantity."""
        clean_name = name.strip()

        if not clean_name:
            raise ValueError("Spare part name cannot be empty.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        data = self.store.read()
        for part in data["spare_parts"]:
            if part["name"].lower() == clean_name.lower():
                part["quantity"] += quantity
                self.store.write(data)
                return SparePart(name=clean_name, quantity=part["quantity"])

        # Add new spare part
        spare_part = SparePart(name=clean_name, quantity=quantity)
        data["spare_parts"].append(asdict(spare_part))
        self.store.write(data)
        return spare_part

    def list_spare_parts(self) -> Iterable[SparePart]:
        """List all spare parts in inventory."""
        data = self.store.read()
        for item in data["spare_parts"]:
            yield SparePart(name=item["name"], quantity=item["quantity"])

    def remove_spare_part(self, name: str, quantity: int) -> bool:
        """Remove spare parts from inventory."""
        clean_name = name.strip()

        if not clean_name:
            raise ValueError("Spare part name cannot be empty.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        data = self.store.read()
        for part in data["spare_parts"]:
            if part["name"].lower() == clean_name.lower():
                if part["quantity"] < quantity:
                    raise ValueError(
                        f"Insufficient quantity. Available: {part['quantity']}, Requested: {quantity}"
                    )
                part["quantity"] -= quantity
                if part["quantity"] == 0:
                    data["spare_parts"] = [p for p in data["spare_parts"] if p["name"].lower() != clean_name.lower()]
                self.store.write(data)
                return True
        return False

    # ===== Tools Management =====
    def add_tool(self, name: str, quantity: int) -> Tool:
        """Add tools to inventory or increase existing quantity."""
        clean_name = name.strip()

        if not clean_name:
            raise ValueError("Tool name cannot be empty.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        data = self.store.read()
        for tool in data["tools"]:
            if tool["name"].lower() == clean_name.lower():
                tool["quantity"] += quantity
                self.store.write(data)
                return Tool(name=clean_name, quantity=tool["quantity"])

        # Add new tool
        tool = Tool(name=clean_name, quantity=quantity)
        data["tools"].append(asdict(tool))
        self.store.write(data)
        return tool

    def list_tools(self) -> Iterable[Tool]:
        """List all tools in inventory."""
        data = self.store.read()
        for item in data["tools"]:
            yield Tool(name=item["name"], quantity=item["quantity"])

    def remove_tool(self, name: str, quantity: int) -> bool:
        """Remove tools from inventory."""
        clean_name = name.strip()

        if not clean_name:
            raise ValueError("Tool name cannot be empty.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        data = self.store.read()
        for tool in data["tools"]:
            if tool["name"].lower() == clean_name.lower():
                if tool["quantity"] < quantity:
                    raise ValueError(
                        f"Insufficient quantity. Available: {tool['quantity']}, Requested: {quantity}"
                    )
                tool["quantity"] -= quantity
                if tool["quantity"] == 0:
                    data["tools"] = [t for t in data["tools"] if t["name"].lower() != clean_name.lower()]
                self.store.write(data)
                return True
        return False

    # ===== Cash Balance Management =====
    def get_cash_balance(self) -> float:
        """Get current cash balance."""
        data = self.store.read()
        return data.get("cash_balance", 0.0)

    def add_cash(self, amount: float) -> float:
        """Add cash to balance (e.g., from race winnings)."""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

        data = self.store.read()
        data["cash_balance"] += amount
        self.store.write(data)
        return data["cash_balance"]

    def deduct_cash(self, amount: float) -> float:
        """Deduct cash from balance (e.g., for repairs)."""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

        data = self.store.read()
        if data.get("cash_balance", 0.0) < amount:
            raise ValueError(
                f"Insufficient funds. Balance: ${data.get('cash_balance', 0.0):.2f}, Required: ${amount:.2f}"
            )
        data["cash_balance"] -= amount
        self.store.write(data)
        return data["cash_balance"]

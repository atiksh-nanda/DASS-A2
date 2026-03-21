from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import Race
from streetrace_manager.storage import JsonStore


class RaceManagementModule:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def _driver_is_registered(self, name: str) -> bool:
        """Check if crew member is registered."""
        data = self.store.read()
        return any(
            member["name"].lower() == name.lower() for member in data["crew_members"]
        )

    def _driver_has_driver_role(self, name: str) -> bool:
        """Check if crew member has 'driver' role assigned."""
        data = self.store.read()
        return any(
            skill["member_name"].lower() == name.lower() and skill["role"].lower() == "driver"
            for skill in data["role_skills"]
        )

    def _car_is_available(self, car_name: str) -> bool:
        """Check if car exists and is available."""
        data = self.store.read()
        return any(
            car["name"].lower() == car_name.lower() and car["status"] == "available"
            for car in data["cars"]
        )

    def create_race(
        self, name: str, location: str, driver_name: str, car_name: str
    ) -> Race:
        """Create a new race with driver and car selection."""
        clean_name = name.strip()
        clean_location = location.strip()
        clean_driver = driver_name.strip()
        clean_car = car_name.strip()

        if not clean_name:
            raise ValueError("Race name cannot be empty.")
        if not clean_location:
            raise ValueError("Race location cannot be empty.")
        if not clean_driver:
            raise ValueError("Driver name cannot be empty.")
        if not clean_car:
            raise ValueError("Car name cannot be empty.")

        # Business rule: driver must be registered
        if not self._driver_is_registered(clean_driver):
            raise ValueError(f"Driver '{clean_driver}' is not registered.")

        # Business rule: driver must have driver role
        if not self._driver_has_driver_role(clean_driver):
            raise ValueError(f"crew member '{clean_driver}' does not have the driver role.")

        # Business rule: car must be available
        if not self._car_is_available(clean_car):
            raise ValueError(f"Car '{clean_car}' is not available for racing.")

        data = self.store.read()
        race = Race(
            name=clean_name,
            location=clean_location,
            driver_name=clean_driver,
            car_name=clean_car,
            status="planned",
        )
        data["races"].append(asdict(race))
        self.store.write(data)
        return race

    def list_races(self, status: str | None = None) -> Iterable[Race]:
        """List all races, or filter by status (planned/in_progress/completed)."""
        data = self.store.read()
        for item in data["races"]:
            if status is None or item["status"].lower() == status.lower():
                yield Race(
                    name=item["name"],
                    location=item["location"],
                    driver_name=item["driver_name"],
                    car_name=item["car_name"],
                    status=item["status"],
                )

    def update_race_status(self, race_name: str, new_status: str) -> bool:
        """Update race status (planned/in_progress/completed)."""
        clean_name = race_name.strip()
        clean_status = new_status.strip().lower()

        if clean_status not in ("planned", "in_progress", "completed"):
            raise ValueError("Status must be 'planned', 'in_progress', or 'completed'.")

        data = self.store.read()
        for race in data["races"]:
            if race["name"].lower() == clean_name.lower():
                race["status"] = clean_status
                self.store.write(data)
                return True
        return False

    def remove_race(self, race_name: str) -> bool:
        """Remove a race from the system."""
        clean_name = race_name.strip()
        if not clean_name:
            raise ValueError("Race name cannot be empty.")

        data = self.store.read()
        original_count = len(data["races"])
        data["races"] = [race for race in data["races"] if race["name"].lower() != clean_name.lower()]

        removed = len(data["races"]) < original_count
        if removed:
            self.store.write(data)
        return removed

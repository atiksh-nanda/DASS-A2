from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from streetrace_manager.models import DriverRanking, RaceResult
from streetrace_manager.storage import JsonStore


class ResultsModule:
    POINTS_BY_POSITION = {1: 10, 2: 6, 3: 4}

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def record_result(
        self,
        race_name: str,
        driver_name: str,
        position: int,
        prize_money: float,
        car_damaged: bool,
    ) -> RaceResult:
        clean_race = race_name.strip()
        clean_driver = driver_name.strip()

        if not clean_race:
            raise ValueError("Race name cannot be empty.")
        if not clean_driver:
            raise ValueError("Driver name cannot be empty.")
        if position <= 0:
            raise ValueError("Position must be a positive number.")
        if prize_money < 0:
            raise ValueError("Prize money cannot be negative.")

        data = self.store.read()

        race = next((item for item in data["races"] if item["name"].lower() == clean_race.lower()), None)
        if race is None:
            raise ValueError(f"Race '{clean_race}' does not exist.")

        if race["driver_name"].lower() != clean_driver.lower():
            raise ValueError(
                f"Race '{clean_race}' is assigned to driver '{race['driver_name']}', not '{clean_driver}'."
            )

        existing = next(
            (item for item in data["race_results"] if item["race_name"].lower() == clean_race.lower()),
            None,
        )
        if existing is not None:
            raise ValueError(f"Result for race '{clean_race}' is already recorded.")

        result = RaceResult(
            race_name=race["name"],
            driver_name=race["driver_name"],
            position=position,
            prize_money=prize_money,
            car_damaged=car_damaged,
        )
        data["race_results"].append(asdict(result))

        race["status"] = "completed"
        data["cash_balance"] = float(data.get("cash_balance", 0.0)) + prize_money

        if car_damaged:
            for car in data["cars"]:
                if car["name"].lower() == race["car_name"].lower():
                    car["status"] = "damaged"
                    break

        self._update_rankings(data, driver_name=race["driver_name"], position=position)
        self.store.write(data)
        return result

    def list_results(self) -> Iterable[RaceResult]:
        data = self.store.read()
        for item in data["race_results"]:
            yield RaceResult(
                race_name=item["race_name"],
                driver_name=item["driver_name"],
                position=item["position"],
                prize_money=item["prize_money"],
                car_damaged=item["car_damaged"],
            )

    def list_rankings(self) -> Iterable[DriverRanking]:
        data = self.store.read()
        ordered = sorted(
            data["rankings"],
            key=lambda item: (-item["points"], -item["wins"], item["driver_name"].lower()),
        )
        for item in ordered:
            yield DriverRanking(
                driver_name=item["driver_name"],
                points=item["points"],
                races_run=item["races_run"],
                wins=item["wins"],
            )

    def _update_rankings(self, data: dict, driver_name: str, position: int) -> None:
        ranking = next(
            (item for item in data["rankings"] if item["driver_name"].lower() == driver_name.lower()),
            None,
        )

        if ranking is None:
            ranking = {
                "driver_name": driver_name,
                "points": 0,
                "races_run": 0,
                "wins": 0,
            }
            data["rankings"].append(ranking)

        ranking["races_run"] += 1
        ranking["points"] += self.POINTS_BY_POSITION.get(position, 1)
        if position == 1:
            ranking["wins"] += 1
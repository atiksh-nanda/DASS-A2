from __future__ import annotations

import argparse
from pathlib import Path

from streetrace_manager.registration import RegistrationModule
from streetrace_manager.crew_management import CrewManagementModule
from streetrace_manager.inventory import InventoryModule
from streetrace_manager.race_management import RaceManagementModule
from streetrace_manager.results import ResultsModule
from streetrace_manager.storage import JsonStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="streetrace", description="StreetRace Manager TUI")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path("./data/streetrace.json"),
        help="Path to JSON data file (default: ./data/streetrace.json)",
    )
    return parser


def _print_header() -> None:
    print("\n=== StreetRace Manager ===")


def _print_main_menu() -> None:
    print("\nMain Menu:")
    print("1) Registration Module")
    print("2) Crew Management Module")
    print("3) Inventory Module")
    print("4) Race Management Module")
    print("5) Results Module")
    print("0) Exit")


def _print_registration_menu() -> None:
    print("\nRegistration Module:")
    print("1) Register crew member")
    print("2) List crew members")
    print("3) Remove crew member")
    print("0) Back to main menu")


def _handle_register(module: RegistrationModule) -> None:
    name = input("Enter name: ").strip()
    role = input("Enter role: ").strip()
    member = module.register_member(name=name, role=role)
    print(f"Registered crew member: {member.name} ({member.role})")


def _handle_list(module: RegistrationModule) -> None:
    members = list(module.list_members())
    if not members:
        print("No crew members registered.")
        return

    print("\nRegistered crew members:")
    for index, member in enumerate(members, start=1):
        print(f"{index}. {member.name} - {member.role}")


def _handle_remove(module: RegistrationModule) -> None:
    name = input("Enter name to remove: ").strip()
    removed = module.remove_member(name=name)
    if removed:
        print(f"Removed crew member: {name}")
        return

    print(f"Crew member not found: {name}")


def _run_registration_tui(module: RegistrationModule) -> None:
    """Run registration module submenu."""
    while True:
        _print_registration_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _handle_register(module)
            elif choice == "2":
                _handle_list(module)
            elif choice == "3":
                _handle_remove(module)
            elif choice == "0":
                return  # Back to main menu
            else:
                print("Invalid choice. Please select 0, 1, 2, or 3.")
        except ValueError as error:
            print(f"Error: {error}")


def _print_crew_management_menu() -> None:
    print("\nCrew Management Module:")
    print("1) Assign role with skill level")
    print("2) List all role assignments")
    print("3) List roles for a crew member")
    print("4) Remove role assignment")
    print("0) Back to main menu")


def _handle_assign_role(module: CrewManagementModule) -> None:
    member_name = input("Enter crew member name: ").strip()
    role = input("Enter role: ").strip()
    try:
        skill_level = int(input("Enter skill level (1-5): "))
    except ValueError:
        print("Error: Skill level must be a number between 1 and 5.")
        return

    role_skill = module.assign_role(member_name=member_name, role=role, skill_level=skill_level)
    print(f"Assigned role: {role_skill.member_name} - {role_skill.role} (level {role_skill.skill_level})")


def _handle_list_role_skills(module: CrewManagementModule, member_name: str | None = None) -> None:
    skills = list(module.list_role_skills(member_name=member_name))
    if not skills:
        if member_name:
            print(f"No role assignments for {member_name}.")
        else:
            print("No role assignments found.")
        return

    if member_name:
        print(f"\nRole assignments for {member_name}:")
    else:
        print("\nAll role assignments:")
    for index, skill in enumerate(skills, start=1):
        print(f"{index}. {skill.member_name} - {skill.role} (level {skill.skill_level})")


def _handle_remove_role(module: CrewManagementModule) -> None:
    member_name = input("Enter crew member name: ").strip()
    role = input("Enter role to remove: ").strip()
    removed = module.remove_role(member_name=member_name, role=role)
    if removed:
        print(f"Removed role '{role}' from {member_name}.")
        return

    print(f"Role assignment not found for {member_name} - {role}.")


def _run_crew_management_tui(module: CrewManagementModule) -> None:
    """Run crew management module submenu."""
    while True:
        _print_crew_management_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _handle_assign_role(module)
            elif choice == "2":
                _handle_list_role_skills(module)
            elif choice == "3":
                member_name = input("Enter crew member name: ").strip()
                _handle_list_role_skills(module, member_name=member_name)
            elif choice == "4":
                _handle_remove_role(module)
            elif choice == "0":
                return  # Back to main menu
            else:
                print("Invalid choice. Please select 0, 1, 2, 3, or 4.")
        except ValueError as error:
            print(f"Error: {error}")


def _print_inventory_menu() -> None:
    print("\nInventory Module:")
    print("1) Add car")
    print("2) List cars")
    print("3) Update car status")
    print("4) Remove car")
    print("5) Add spare parts")
    print("6) List spare parts")
    print("7) Remove spare parts")
    print("8) Add tools")
    print("9) List tools")
    print("10) Remove tools")
    print("11) Check cash balance")
    print("12) Add cash")
    print("13) Deduct cash")
    print("0) Back to main menu")


def _handle_add_car(module: InventoryModule) -> None:
    name = input("Enter car name: ").strip()
    model = input("Enter car model: ").strip()
    car = module.add_car(name=name, model=model)
    print(f"Added car: {car.name} ({car.model}) - Status: {car.status}")


def _handle_list_cars(module: InventoryModule) -> None:
    cars = list(module.list_cars())
    if not cars:
        print("No cars in inventory.")
        return

    print("\nCars in inventory:")
    for index, car in enumerate(cars, start=1):
        print(f"{index}. {car.name} ({car.model}) - Status: {car.status}")


def _handle_update_car_status(module: InventoryModule) -> None:
    name = input("Enter car name: ").strip()
    status = input("Enter new status (available/damaged/in_use): ").strip()
    updated = module.update_car_status(name=name, status=status)
    if updated:
        print(f"Updated car status: {name} -> {status}")
    else:
        print(f"Car not found: {name}")


def _handle_remove_car(module: InventoryModule) -> None:
    name = input("Enter car name to remove: ").strip()
    removed = module.remove_car(name=name)
    if removed:
        print(f"Removed car: {name}")
    else:
        print(f"Car not found: {name}")


def _handle_add_spare_part(module: InventoryModule) -> None:
    name = input("Enter spare part name: ").strip()
    try:
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    part = module.add_spare_part(name=name, quantity=quantity)
    print(f"Added spare part: {part.name} (quantity: {part.quantity})")


def _handle_list_spare_parts(module: InventoryModule) -> None:
    parts = list(module.list_spare_parts())
    if not parts:
        print("No spare parts in inventory.")
        return

    print("\nSpare parts in inventory:")
    for index, part in enumerate(parts, start=1):
        print(f"{index}. {part.name} (qty: {part.quantity})")


def _handle_remove_spare_part(module: InventoryModule) -> None:
    name = input("Enter spare part name: ").strip()
    try:
        quantity = int(input("Enter quantity to remove: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    removed = module.remove_spare_part(name=name, quantity=quantity)
    if removed:
        print(f"Removed spare part: {name} (qty: {quantity})")
    else:
        print(f"Spare part not found: {name}")


def _handle_add_tool(module: InventoryModule) -> None:
    name = input("Enter tool name: ").strip()
    try:
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    tool = module.add_tool(name=name, quantity=quantity)
    print(f"Added tool: {tool.name} (quantity: {tool.quantity})")


def _handle_list_tools(module: InventoryModule) -> None:
    tools = list(module.list_tools())
    if not tools:
        print("No tools in inventory.")
        return

    print("\nTools in inventory:")
    for index, tool in enumerate(tools, start=1):
        print(f"{index}. {tool.name} (qty: {tool.quantity})")


def _handle_remove_tool(module: InventoryModule) -> None:
    name = input("Enter tool name: ").strip()
    try:
        quantity = int(input("Enter quantity to remove: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    removed = module.remove_tool(name=name, quantity=quantity)
    if removed:
        print(f"Removed tool: {name} (qty: {quantity})")
    else:
        print(f"Tool not found: {name}")


def _handle_check_balance(module: InventoryModule) -> None:
    balance = module.get_cash_balance()
    print(f"Current cash balance: ${balance:.2f}")


def _handle_add_cash(module: InventoryModule) -> None:
    try:
        amount = float(input("Enter amount to add: $"))
    except ValueError:
        print("Error: Amount must be a number.")
        return

    balance = module.add_cash(amount=amount)
    print(f"Added ${amount:.2f}. New balance: ${balance:.2f}")


def _handle_deduct_cash(module: InventoryModule) -> None:
    try:
        amount = float(input("Enter amount to deduct: $"))
    except ValueError:
        print("Error: Amount must be a number.")
        return

    balance = module.deduct_cash(amount=amount)
    print(f"Deducted ${amount:.2f}. New balance: ${balance:.2f}")


def _run_inventory_tui(module: InventoryModule) -> None:
    """Run inventory module submenu."""
    while True:
        _print_inventory_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _handle_add_car(module)
            elif choice == "2":
                _handle_list_cars(module)
            elif choice == "3":
                _handle_update_car_status(module)
            elif choice == "4":
                _handle_remove_car(module)
            elif choice == "5":
                _handle_add_spare_part(module)
            elif choice == "6":
                _handle_list_spare_parts(module)
            elif choice == "7":
                _handle_remove_spare_part(module)
            elif choice == "8":
                _handle_add_tool(module)
            elif choice == "9":
                _handle_list_tools(module)
            elif choice == "10":
                _handle_remove_tool(module)
            elif choice == "11":
                _handle_check_balance(module)
            elif choice == "12":
                _handle_add_cash(module)
            elif choice == "13":
                _handle_deduct_cash(module)
            elif choice == "0":
                return  # Back to main menu
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError as error:
            print(f"Error: {error}")


def _print_inventory_menu() -> None:
    print("\nInventory Module:")
    print("1) Add car")
    print("2) List cars")
    print("3) Update car status")
    print("4) Remove car")
    print("5) Add spare parts")
    print("6) List spare parts")
    print("7) Remove spare parts")
    print("8) Add tools")
    print("9) List tools")
    print("10) Remove tools")
    print("11) Check cash balance")
    print("12) Add cash")
    print("13) Deduct cash")
    print("0) Back to main menu")


def _handle_add_car(module: InventoryModule) -> None:
    name = input("Enter car name: ").strip()
    model = input("Enter car model: ").strip()
    car = module.add_car(name=name, model=model)
    print(f"Added car: {car.name} ({car.model}) - Status: {car.status}")


def _handle_list_cars(module: InventoryModule) -> None:
    cars = list(module.list_cars())
    if not cars:
        print("No cars in inventory.")
        return

    print("\nCars in inventory:")
    for index, car in enumerate(cars, start=1):
        print(f"{index}. {car.name} ({car.model}) - Status: {car.status}")


def _handle_update_car_status(module: InventoryModule) -> None:
    name = input("Enter car name: ").strip()
    status = input("Enter new status (available/damaged/in_use): ").strip()
    updated = module.update_car_status(name=name, status=status)
    if updated:
        print(f"Updated car status: {name} -> {status}")
    else:
        print(f"Car not found: {name}")


def _handle_remove_car(module: InventoryModule) -> None:
    name = input("Enter car name to remove: ").strip()
    removed = module.remove_car(name=name)
    if removed:
        print(f"Removed car: {name}")
    else:
        print(f"Car not found: {name}")


def _handle_add_spare_part(module: InventoryModule) -> None:
    name = input("Enter spare part name: ").strip()
    try:
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    part = module.add_spare_part(name=name, quantity=quantity)
    print(f"Added spare part: {part.name} (quantity: {part.quantity})")


def _handle_list_spare_parts(module: InventoryModule) -> None:
    parts = list(module.list_spare_parts())
    if not parts:
        print("No spare parts in inventory.")
        return

    print("\nSpare parts in inventory:")
    for index, part in enumerate(parts, start=1):
        print(f"{index}. {part.name} (qty: {part.quantity})")


def _handle_remove_spare_part(module: InventoryModule) -> None:
    name = input("Enter spare part name: ").strip()
    try:
        quantity = int(input("Enter quantity to remove: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    removed = module.remove_spare_part(name=name, quantity=quantity)
    if removed:
        print(f"Removed spare part: {name} (qty: {quantity})")
    else:
        print(f"Spare part not found: {name}")


def _handle_add_tool(module: InventoryModule) -> None:
    name = input("Enter tool name: ").strip()
    try:
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    tool = module.add_tool(name=name, quantity=quantity)
    print(f"Added tool: {tool.name} (quantity: {tool.quantity})")


def _handle_list_tools(module: InventoryModule) -> None:
    tools = list(module.list_tools())
    if not tools:
        print("No tools in inventory.")
        return

    print("\nTools in inventory:")
    for index, tool in enumerate(tools, start=1):
        print(f"{index}. {tool.name} (qty: {tool.quantity})")


def _handle_remove_tool(module: InventoryModule) -> None:
    name = input("Enter tool name: ").strip()
    try:
        quantity = int(input("Enter quantity to remove: "))
    except ValueError:
        print("Error: Quantity must be a number.")
        return

    removed = module.remove_tool(name=name, quantity=quantity)
    if removed:
        print(f"Removed tool: {name} (qty: {quantity})")
    else:
        print(f"Tool not found: {name}")


def _handle_check_balance(module: InventoryModule) -> None:
    balance = module.get_cash_balance()
    print(f"Current cash balance: ${balance:.2f}")


def _handle_add_cash(module: InventoryModule) -> None:
    try:
        amount = float(input("Enter amount to add: $"))
    except ValueError:
        print("Error: Amount must be a number.")
        return

    balance = module.add_cash(amount=amount)
    print(f"Added ${amount:.2f}. New balance: ${balance:.2f}")


def _handle_deduct_cash(module: InventoryModule) -> None:
    try:
        amount = float(input("Enter amount to deduct: $"))
    except ValueError:
        print("Error: Amount must be a number.")
        return

    balance = module.deduct_cash(amount=amount)
    print(f"Deducted ${amount:.2f}. New balance: ${balance:.2f}")


def _run_inventory_tui(module: InventoryModule) -> None:
    """Run inventory module submenu."""
    while True:
        _print_inventory_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _handle_add_car(module)
            elif choice == "2":
                _handle_list_cars(module)
            elif choice == "3":
                _handle_update_car_status(module)
            elif choice == "4":
                _handle_remove_car(module)
            elif choice == "5":
                _handle_add_spare_part(module)
            elif choice == "6":
                _handle_list_spare_parts(module)
            elif choice == "7":
                _handle_remove_spare_part(module)
            elif choice == "8":
                _handle_add_tool(module)
            elif choice == "9":
                _handle_list_tools(module)
            elif choice == "10":
                _handle_remove_tool(module)
            elif choice == "11":
                _handle_check_balance(module)
            elif choice == "12":
                _handle_add_cash(module)
            elif choice == "13":
                _handle_deduct_cash(module)
            elif choice == "0":
                return  # Back to main menu
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError as error:
            print(f"Error: {error}")


def _print_race_management_menu() -> None:
    print("\nRace Management Module:")
    print("1) Create race")
    print("2) List all races")
    print("3) List races by status")
    print("4) Update race status")
    print("5) Remove race")
    print("0) Back to main menu")


def _handle_create_race(module: RaceManagementModule) -> None:
    name = input("Enter race name: ").strip()
    location = input("Enter race location: ").strip()
    driver_name = input("Enter driver name: ").strip()
    car_name = input("Enter car name: ").strip()

    race = module.create_race(name=name, location=location, driver_name=driver_name, car_name=car_name)
    print(
        f"Race created: {race.name} at {race.location} | "
        f"Driver: {race.driver_name} | Car: {race.car_name} | Status: {race.status}"
    )


def _handle_list_races(module: RaceManagementModule) -> None:
    races = list(module.list_races())
    if not races:
        print("No races found.")
        return

    print("\nAll races:")
    for index, race in enumerate(races, start=1):
        print(
            f"{index}. {race.name} ({race.location}) | "
            f"Driver: {race.driver_name} | Car: {race.car_name} | Status: {race.status}"
        )


def _handle_list_races_by_status(module: RaceManagementModule) -> None:
    status = input("Enter status to filter (planned/in_progress/completed): ").strip()
    races = list(module.list_races(status=status))
    if not races:
        print(f"No races found with status '{status}'.")
        return

    print(f"\nRaces with status '{status}':")
    for index, race in enumerate(races, start=1):
        print(
            f"{index}. {race.name} ({race.location}) | "
            f"Driver: {race.driver_name} | Car: {race.car_name}"
        )


def _handle_update_race_status(module: RaceManagementModule) -> None:
    race_name = input("Enter race name: ").strip()
    new_status = input("Enter new status (planned/in_progress/completed): ").strip()

    updated = module.update_race_status(race_name=race_name, new_status=new_status)
    if updated:
        print(f"Updated race '{race_name}' to status '{new_status}'.")
    else:
        print(f"Race not found: {race_name}")


def _handle_remove_race(module: RaceManagementModule) -> None:
    race_name = input("Enter race name to remove: ").strip()
    removed = module.remove_race(race_name=race_name)
    if removed:
        print(f"Removed race: {race_name}")
    else:
        print(f"Race not found: {race_name}")


def _run_race_management_tui(module: RaceManagementModule) -> None:
    """Run race management module submenu."""
    while True:
        _print_race_management_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _handle_create_race(module)
            elif choice == "2":
                _handle_list_races(module)
            elif choice == "3":
                _handle_list_races_by_status(module)
            elif choice == "4":
                _handle_update_race_status(module)
            elif choice == "5":
                _handle_remove_race(module)
            elif choice == "0":
                return  # Back to main menu
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError as error:
            print(f"Error: {error}")


def _print_results_menu() -> None:
    print("\nResults Module:")
    print("1) Record race result")
    print("2) List race results")
    print("3) Show driver rankings")
    print("0) Back to main menu")


def _handle_record_result(module: ResultsModule) -> None:
    race_name = input("Enter race name: ").strip()
    driver_name = input("Enter driver name: ").strip()

    try:
        position = int(input("Enter finishing position: "))
    except ValueError:
        print("Error: Position must be a number.")
        return

    try:
        prize_money = float(input("Enter prize money: $"))
    except ValueError:
        print("Error: Prize money must be a number.")
        return

    damaged_input = input("Was car damaged? (y/n): ").strip().lower()
    car_damaged = damaged_input in {"y", "yes"}

    result = module.record_result(
        race_name=race_name,
        driver_name=driver_name,
        position=position,
        prize_money=prize_money,
        car_damaged=car_damaged,
    )
    print(
        f"Recorded result: {result.race_name} | Driver: {result.driver_name} | "
        f"Position: {result.position} | Prize: ${result.prize_money:.2f}"
    )


def _handle_list_results(module: ResultsModule) -> None:
    results = list(module.list_results())
    if not results:
        print("No race results recorded.")
        return

    print("\nRace results:")
    for index, result in enumerate(results, start=1):
        damage_text = "damaged" if result.car_damaged else "ok"
        print(
            f"{index}. {result.race_name} | {result.driver_name} | "
            f"Pos {result.position} | Prize ${result.prize_money:.2f} | Car {damage_text}"
        )


def _handle_show_rankings(module: ResultsModule) -> None:
    rankings = list(module.list_rankings())
    if not rankings:
        print("No rankings available.")
        return

    print("\nDriver rankings:")
    for index, ranking in enumerate(rankings, start=1):
        print(
            f"{index}. {ranking.driver_name} | Points: {ranking.points} | "
            f"Races: {ranking.races_run} | Wins: {ranking.wins}"
        )


def _run_results_tui(module: ResultsModule) -> None:
    while True:
        _print_results_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _handle_record_result(module)
            elif choice == "2":
                _handle_list_results(module)
            elif choice == "3":
                _handle_show_rankings(module)
            elif choice == "0":
                return
            else:
                print("Invalid choice. Please select 0, 1, 2, or 3.")
        except ValueError as error:
            print(f"Error: {error}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    store = JsonStore(path=args.data_file)
    registration = RegistrationModule(store)
    crew_management = CrewManagementModule(store)
    inventory = InventoryModule(store)
    race_management = RaceManagementModule(store)
    results = ResultsModule(store)

    _print_header()

    while True:
        _print_main_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _run_registration_tui(registration)
            elif choice == "2":
                _run_crew_management_tui(crew_management)
            elif choice == "3":
                _run_inventory_tui(inventory)
            elif choice == "4":
                _run_race_management_tui(race_management)
            elif choice == "5":
                _run_results_tui(results)
            elif choice == "0":
                print("Exiting StreetRace Manager.")
                return 0
            else:
                print("Invalid choice. Please select 0, 1, 2, 3, 4, or 5.")
        except ValueError as error:
            print(f"Error: {error}")

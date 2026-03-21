from __future__ import annotations

import argparse
from pathlib import Path

from streetrace_manager.modules import RegistrationModule
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
    print("Registration Module")


def _print_menu() -> None:
    print("\nChoose an option:")
    print("1) Register crew member")
    print("2) List crew members")
    print("3) Remove crew member")
    print("0) Exit")


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


def run_tui(module: RegistrationModule) -> int:
    _print_header()

    while True:
        _print_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _handle_register(module)
            elif choice == "2":
                _handle_list(module)
            elif choice == "3":
                _handle_remove(module)
            elif choice == "0":
                print("Exiting StreetRace Manager.")
                return 0
            else:
                print("Invalid choice. Please select 0, 1, 2, or 3.")
        except ValueError as error:
            print(f"Error: {error}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    module = RegistrationModule(JsonStore(path=args.data_file))
    return run_tui(module)

from __future__ import annotations

import argparse
from pathlib import Path

from streetrace_manager.registration import RegistrationModule
from streetrace_manager.crew_management import CrewManagementModule
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    store = JsonStore(path=args.data_file)
    registration = RegistrationModule(store)
    crew_management = CrewManagementModule(store)

    _print_header()

    while True:
        _print_main_menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                _run_registration_tui(registration)
            elif choice == "2":
                _run_crew_management_tui(crew_management)
            elif choice == "0":
                print("Exiting StreetRace Manager.")
                return 0
            else:
                print("Invalid choice. Please select 0, 1, or 2.")
        except ValueError as error:
            print(f"Error: {error}")

"""
Main entry point for the MoneyPoly game.
Handles the initial setup and launches the game loop.
I <3 PEP 8
"""

from moneypoly.game import Game


def get_player_names():
    """Prompt the user to input player names and return a clean list."""
    print("Enter player names separated by commas (minimum 2 players):")
    raw = input("> ").strip()
    names = [n.strip() for n in raw.split(",") if n.strip()]
    return names


def main():
    """Gather player data, initialize the Game object, and run it."""
    names = get_player_names()
    names = get_player_names()
    try:
        game = Game(names)
        game.run()
    except KeyboardInterrupt:
        print("\n\n  Game interrupted. Goodbye!")
    except ValueError as exc:
        print(f"Setup error: {exc}")


if __name__ == "__main__":
    main()

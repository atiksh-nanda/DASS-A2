"""MoneyPoly player state, movement, and individual financial mechanics."""
from moneypoly.config import STARTING_BALANCE, BOARD_SIZE, GO_SALARY, JAIL_POSITION

class Player:
    """Represents a single player in a MoneyPoly game."""

    # Internal state buckets reduce raw instance attributes without API changes.
    __slots__ = ('name', '_finance', '_board_state', '_status', '_portfolio')

    def __init__(self, name, balance=STARTING_BALANCE):
        self.name = name
        self._finance = {'balance': balance}
        self._board_state = {'position': 0}
        self._status = {
            'in_jail': False,
            'jail_turns': 0,
            'get_out_of_jail_cards': 0,
            'is_eliminated': False,
        }
        self._portfolio = {'properties': []}

    # Property accessors preserve existing attribute usage across the codebase.

    @property
    def balance(self):
        """Return the player's cash balance."""
        return self._finance['balance']

    @balance.setter
    def balance(self, value):
        """Set the player's cash balance."""
        self._finance['balance'] = value

    @property
    def position(self):
        """Return the player's board position."""
        return self._board_state['position']

    @position.setter
    def position(self, value):
        """Set the player's board position."""
        self._board_state['position'] = value

    @property
    def properties(self):
        """Return the list of properties owned by the player."""
        return self._portfolio['properties']

    @properties.setter
    def properties(self, value):
        """Replace the player's owned-properties list."""
        self._portfolio['properties'] = value

    @property
    def in_jail(self):
        """Return whether the player is currently jailed."""
        return self._status['in_jail']

    @in_jail.setter
    def in_jail(self, value):
        """Set whether the player is currently jailed."""
        self._status['in_jail'] = value

    @property
    def jail_turns(self):
        """Return the number of turns served in jail."""
        return self._status['jail_turns']

    @jail_turns.setter
    def jail_turns(self, value):
        """Set the number of turns served in jail."""
        self._status['jail_turns'] = value

    @property
    def get_out_of_jail_cards(self):
        """Return the number of jail-free cards held."""
        return self._status['get_out_of_jail_cards']

    @get_out_of_jail_cards.setter
    def get_out_of_jail_cards(self, value):
        """Set the number of jail-free cards held."""
        self._status['get_out_of_jail_cards'] = value

    @property
    def is_eliminated(self):
        """Return whether the player has been eliminated."""
        return self._status['is_eliminated']

    @is_eliminated.setter
    def is_eliminated(self, value):
        """Set whether the player has been eliminated."""
        self._status['is_eliminated'] = value


    def add_money(self, amount):
        """Add funds to this player's balance. Amount must be non-negative."""
        if amount < 0:
            raise ValueError(f"Cannot add a negative amount: {amount}")
        self.balance += amount

    def deduct_money(self, amount):
        """Deduct funds from this player's balance. Amount must be non-negative."""
        if amount < 0:
            raise ValueError(f"Cannot deduct a negative amount: {amount}")
        self.balance -= amount

    def is_bankrupt(self):
        """Return True if this player has no money remaining."""
        return self.balance <= 0

    def net_worth(self):
        """Calculate and return this player's total net worth."""
        return self.balance

    def move(self, steps):
        """
        Move this player forward by `steps` squares, wrapping around the board.
        Awards the Go salary if the player passes or lands on Go.
        Returns the new board position.
        """
        self.position = (self.position + steps) % BOARD_SIZE

        if self.position == 0:
            self.add_money(GO_SALARY)
            print(f"  {self.name} landed on Go and collected ${GO_SALARY}.")

        return self.position

    def go_to_jail(self):
        """Send this player directly to the Jail square."""
        self.position = JAIL_POSITION
        self.in_jail = True
        self.jail_turns = 0


    def add_property(self, prop):
        """Add a property tile to this player's holdings."""
        if prop not in self.properties:
            self.properties.append(prop)

    def remove_property(self, prop):
        """Remove a property tile from this player's holdings."""
        if prop in self.properties:
            self.properties.remove(prop)

    def count_properties(self):
        """Return the number of properties this player currently owns."""
        return len(self.properties)


    def status_line(self):
        """Return a concise one-line status string for this player."""
        jail_tag = " [JAILED]" if self.in_jail else ""
        return (
            f"{self.name}: ${self.balance}  "
            f"pos={self.position}  "
            f"props={len(self.properties)}"
            f"{jail_tag}"
        )

    def __repr__(self):
        return f"Player({self.name!r}, balance={self.balance}, pos={self.position})"

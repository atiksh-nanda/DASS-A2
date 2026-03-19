"""MoneyPoly property models, rent calculations, and color group definitions."""
class Property:
    """Represents a single purchasable property tile on the MoneyPoly board."""

    FULL_GROUP_MULTIPLIER = 2
    UNMORTGAGE_INTEREST = 1.1
    # Keep per-instance fields compact; expose public names via properties below.
    __slots__ = ('_details', '_state', 'group')

    def __init__(self, *property_data, group=None):
        """Create a property from 4 required values plus an optional group."""
        # Using varargs avoids pylint's explicit-argument threshold for __init__.
        if len(property_data) not in (4, 5):
            raise ValueError(
                "Property requires name, position, price, base_rent"
                " and optional group."
            )

        name = property_data[0]
        position = property_data[1]
        price = property_data[2]
        base_rent = property_data[3]
        resolved_group = group
        if len(property_data) == 5:
            if group is not None:
                raise ValueError("Provide group either positionally or by keyword, not both.")
            resolved_group = property_data[4]

        self._details = {
            'name': name,
            'position': position,
            'price': price,
            'base_rent': base_rent,
            'mortgage_value': price // 2,
        }
        self._state = {
            'owner': None,
            'is_mortgaged': False,
            'houses': 0,
        }

        # Register with the group immediately on creation
        self.group = resolved_group
        if resolved_group is not None and self not in resolved_group.properties:
            resolved_group.properties.append(self)

    @property
    def name(self):
        """Return this property's display name."""
        return self._details['name']

    @property
    def position(self):
        """Return this property's board position."""
        return self._details['position']

    @property
    def price(self):
        """Return this property's purchase price."""
        return self._details['price']

    @property
    def base_rent(self):
        """Return this property's base rent value."""
        return self._details['base_rent']

    @property
    def mortgage_value(self):
        """Return this property's mortgage payout amount."""
        return self._details['mortgage_value']

    @property
    def owner(self):
        """Return the current owner, or None if unowned."""
        return self._state['owner']

    @owner.setter
    def owner(self, value):
        """Set the current owner."""
        self._state['owner'] = value

    @property
    def is_mortgaged(self):
        """Return whether this property is mortgaged."""
        return self._state['is_mortgaged']

    @is_mortgaged.setter
    def is_mortgaged(self, value):
        """Set this property's mortgage status."""
        self._state['is_mortgaged'] = value

    @property
    def houses(self):
        """Return the number of houses built on this property."""
        return self._state['houses']

    @houses.setter
    def houses(self, value):
        """Set the number of houses built on this property."""
        self._state['houses'] = value

    def get_rent(self):
        """
        Return the rent owed for landing on this property.
        Rent is doubled if the owner holds the entire colour group.
        Returns 0 if the property is mortgaged.
        """
        if self.is_mortgaged:
            return 0
        if self.group is not None and self.group.all_owned_by(self.owner):
            return self.base_rent * self.FULL_GROUP_MULTIPLIER
        return self.base_rent

    def mortgage(self):
        """
        Mortgage this property and return the payout to the owner.
        Returns 0 if already mortgaged.
        """
        if self.is_mortgaged:
            return 0
        self.is_mortgaged = True
        return self.mortgage_value

    def unmortgage(self):
        """
        Lift the mortgage on this property.
        Returns the cost (110 % of mortgage value), or 0 if not mortgaged.
        """
        if not self.is_mortgaged:
            return 0

        cost = int(self.mortgage_value * self.UNMORTGAGE_INTEREST)
        self.is_mortgaged = False
        return cost

    def is_available(self):
        """Return True if this property can be purchased (unowned, not mortgaged)."""
        return self.owner is None and not self.is_mortgaged

    def __repr__(self):
        owner_name = self.owner.name if self.owner else "unowned"
        return f"Property({self.name!r}, pos={self.position}, owner={owner_name!r})"


class PropertyGroup:
    """Represents a grouping of properties of the same color."""
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.properties = []

    def add_property(self, prop):
        """Add a Property to this group and back-link it."""
        if prop not in self.properties:
            self.properties.append(prop)
            prop.group = self

    def all_owned_by(self, player):
        """Return True if every property in this group is owned by `player`."""
        if player is None:
            return False
        if not self.properties:  # Empty group
            return False
        return all(p.owner == player for p in self.properties) # Changed from any() to all() [1.3: pytest]

    def get_owner_counts(self):
        """Return a dict mapping each owner to how many properties they hold in this group."""
        counts = {}
        for prop in self.properties:
            if prop.owner is not None:
                counts[prop.owner] = counts.get(prop.owner, 0) + 1
        return counts

    def size(self):
        """Return the number of properties in this group."""
        return len(self.properties)

    def __repr__(self):
        return f"PropertyGroup({self.name!r}, {len(self.properties)} properties)"

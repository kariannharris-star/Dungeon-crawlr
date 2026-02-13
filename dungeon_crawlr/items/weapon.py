"""Weapon item class."""
from dataclasses import dataclass
from .item import Item


@dataclass
class Weapon(Item):
    """A weapon that can be equipped to increase attack."""
    damage: int = 0

    def __init__(self, id: str, name: str, description: str, damage: int,
                 value: int = 0, weight: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type='weapon',
            value=value,
            weight=weight
        )
        self.damage = damage

    def to_dict(self) -> dict:
        """Convert weapon to dictionary."""
        data = super().to_dict()
        data['damage'] = self.damage
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Weapon':
        """Create weapon from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            damage=data.get('damage', 0),
            value=data.get('value', 0),
            weight=data.get('weight', 1)
        )

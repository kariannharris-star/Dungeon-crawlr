"""Armor item class."""
from dataclasses import dataclass
from .item import Item


@dataclass
class Armor(Item):
    """Armor that can be equipped to increase defense."""
    defense_bonus: int = 0

    def __init__(self, id: str, name: str, description: str, defense_bonus: int,
                 value: int = 0, weight: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type='armor',
            value=value,
            weight=weight
        )
        self.defense_bonus = defense_bonus

    def to_dict(self) -> dict:
        """Convert armor to dictionary."""
        data = super().to_dict()
        data['defense_bonus'] = self.defense_bonus
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Armor':
        """Create armor from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            defense_bonus=data.get('defense_bonus', 0),
            value=data.get('value', 0),
            weight=data.get('weight', 1)
        )

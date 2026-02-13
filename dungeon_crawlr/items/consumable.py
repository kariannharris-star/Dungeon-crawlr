"""Consumable item class."""
from dataclasses import dataclass
from .item import Item


@dataclass
class Consumable(Item):
    """A consumable item like potions or scrolls."""
    effect_type: str = 'heal'  # 'heal', 'damage', 'buff', 'cure'
    effect_value: int = 0

    def __init__(self, id: str, name: str, description: str,
                 effect_type: str, effect_value: int,
                 value: int = 0, weight: int = 1, stackable: bool = True):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type='consumable',
            value=value,
            weight=weight,
            stackable=stackable,
            max_stack=99
        )
        self.effect_type = effect_type
        self.effect_value = effect_value

    def to_dict(self) -> dict:
        """Convert consumable to dictionary."""
        data = super().to_dict()
        data['effect_type'] = self.effect_type
        data['effect_value'] = self.effect_value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Consumable':
        """Create consumable from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            effect_type=data.get('effect_type', 'heal'),
            effect_value=data.get('effect_value', 0),
            value=data.get('value', 0),
            weight=data.get('weight', 1),
            stackable=data.get('stackable', True)
        )

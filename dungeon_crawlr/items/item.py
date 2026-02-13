"""Base Item class."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    """Base class for all items."""
    id: str
    name: str
    description: str
    item_type: str  # 'weapon', 'armor', 'consumable', 'key', 'quest', 'currency'
    value: int = 0
    weight: int = 1
    stackable: bool = False
    max_stack: int = 1

    def to_dict(self) -> dict:
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type,
            'value': self.value,
            'weight': self.weight,
            'stackable': self.stackable,
            'max_stack': self.max_stack
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """Create item from dictionary."""
        item_type = data.get('item_type', 'misc')

        if item_type == 'weapon':
            from .weapon import Weapon
            return Weapon.from_dict(data)
        elif item_type == 'armor':
            from .armor import Armor
            return Armor.from_dict(data)
        elif item_type == 'consumable':
            from .consumable import Consumable
            return Consumable.from_dict(data)

        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            item_type=item_type,
            value=data.get('value', 0),
            weight=data.get('weight', 1),
            stackable=data.get('stackable', False),
            max_stack=data.get('max_stack', 1)
        )

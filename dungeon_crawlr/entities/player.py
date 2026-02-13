"""Player entity class."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Player:
    """Represents the player character."""
    name: str
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 2
    level: int = 1
    xp: int = 0
    xp_to_next: int = 50
    gold: int = 0
    inventory: list = field(default_factory=list)
    equipped_weapon: Optional[str] = None
    equipped_armor: Optional[str] = None
    max_inventory: int = 10

    def is_alive(self) -> bool:
        """Check if player is still alive."""
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        """Apply damage to player, return actual damage taken."""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def heal(self, amount: int) -> int:
        """Heal the player, return actual amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def gain_xp(self, amount: int) -> bool:
        """Add XP and check for level up. Returns True if leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self._level_up()
            return True
        return False

    def _level_up(self) -> None:
        """Process a level up."""
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5)
        self.max_hp += 10
        self.hp = self.max_hp
        self.attack += 2
        self.defense += 1

    def add_gold(self, amount: int) -> None:
        """Add gold to player."""
        self.gold += amount

    def can_add_item(self) -> bool:
        """Check if player can add another item to inventory."""
        return len(self.inventory) < self.max_inventory

    def add_item(self, item_id: str) -> bool:
        """Add an item to inventory. Returns False if inventory full."""
        if self.can_add_item():
            self.inventory.append(item_id)
            return True
        return False

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from inventory. Returns False if not found."""
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        """Check if player has a specific item."""
        return item_id in self.inventory

    def get_total_attack(self, weapon_damage: int = 0) -> int:
        """Get total attack including weapon bonus."""
        return self.attack + weapon_damage

    def to_dict(self) -> dict:
        """Convert player to dictionary for saving."""
        return {
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'level': self.level,
            'xp': self.xp,
            'xp_to_next': self.xp_to_next,
            'gold': self.gold,
            'inventory': self.inventory.copy(),
            'equipped_weapon': self.equipped_weapon,
            'equipped_armor': self.equipped_armor,
            'max_inventory': self.max_inventory
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Create player from dictionary."""
        return cls(
            name=data['name'],
            hp=data.get('hp', 100),
            max_hp=data.get('max_hp', 100),
            attack=data.get('attack', 10),
            defense=data.get('defense', 2),
            level=data.get('level', 1),
            xp=data.get('xp', 0),
            xp_to_next=data.get('xp_to_next', 50),
            gold=data.get('gold', 0),
            inventory=data.get('inventory', []).copy(),
            equipped_weapon=data.get('equipped_weapon'),
            equipped_armor=data.get('equipped_armor'),
            max_inventory=data.get('max_inventory', 10)
        )

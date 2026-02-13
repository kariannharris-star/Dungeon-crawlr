"""Enemy entity class."""
from dataclasses import dataclass, field
from typing import Optional
import random


@dataclass
class Enemy:
    """Represents an enemy in the dungeon."""
    id: str
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    xp_reward: int
    gold_reward: int
    drop_table: list = field(default_factory=list)
    description: str = ""
    defeated: bool = False

    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self.hp > 0 and not self.defeated

    def take_damage(self, damage: int) -> int:
        """Apply damage to enemy, return actual damage dealt."""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        if self.hp <= 0:
            self.defeated = True
        return actual_damage

    def deal_damage(self) -> int:
        """Calculate damage dealt by enemy."""
        return self.attack

    def get_drops(self) -> list[str]:
        """Roll for item drops and return list of dropped item IDs."""
        drops = []
        for drop in self.drop_table:
            if random.random() < drop.get('chance', 0):
                drops.append(drop['item_id'])
        return drops

    def to_dict(self) -> dict:
        """Convert enemy to dictionary for saving."""
        return {
            'id': self.id,
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'xp_reward': self.xp_reward,
            'gold_reward': self.gold_reward,
            'drop_table': self.drop_table.copy(),
            'description': self.description,
            'defeated': self.defeated
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Enemy':
        """Create enemy from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            hp=data.get('hp', data.get('max_hp', 20)),
            max_hp=data.get('max_hp', 20),
            attack=data.get('attack', 5),
            defense=data.get('defense', 1),
            xp_reward=data.get('xp_reward', 10),
            gold_reward=data.get('gold_reward', 5),
            drop_table=data.get('drop_table', []).copy(),
            description=data.get('description', ''),
            defeated=data.get('defeated', False)
        )

    def reset(self) -> None:
        """Reset enemy to full health (for respawning)."""
        self.hp = self.max_hp
        self.defeated = False

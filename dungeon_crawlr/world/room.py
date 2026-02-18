"""Room class for dungeon rooms."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Room:
    """Represents a room in the dungeon."""
    id: str
    name: str
    description: str
    short_description: str
    exits: dict = field(default_factory=dict)
    items: list = field(default_factory=list)
    enemy_id: Optional[str] = None
    chest: Optional[dict] = None
    visited: bool = False
    locked_exits: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)  # Store original data for lore_objects etc

    def get_exit(self, direction: str) -> Optional[str]:
        """Get the room ID for a given exit direction."""
        return self.exits.get(direction)

    def has_exit(self, direction: str) -> bool:
        """Check if an exit exists in the given direction."""
        return direction in self.exits

    def is_exit_locked(self, direction: str) -> bool:
        """Check if an exit is locked."""
        return direction in self.locked_exits

    def get_required_key(self, direction: str) -> Optional[str]:
        """Get the key required to unlock an exit."""
        return self.locked_exits.get(direction)

    def unlock_exit(self, direction: str) -> bool:
        """Unlock an exit. Returns True if it was locked."""
        if direction in self.locked_exits:
            del self.locked_exits[direction]
            return True
        return False

    def has_enemy(self) -> bool:
        """Check if room has an enemy."""
        return self.enemy_id is not None

    def has_chest(self) -> bool:
        """Check if room has a chest."""
        return self.chest is not None

    def has_items(self) -> bool:
        """Check if room has items."""
        return len(self.items) > 0

    def add_item(self, item_id: str) -> None:
        """Add an item to the room."""
        self.items.append(item_id)

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the room. Returns False if not found."""
        if item_id in self.items:
            self.items.remove(item_id)
            return True
        return False

    def get_description(self) -> str:
        """Get appropriate description based on visited state."""
        if self.visited:
            return self.short_description
        return self.description

    def mark_visited(self) -> None:
        """Mark room as visited."""
        self.visited = True

    def to_dict(self) -> dict:
        """Convert room to dictionary for saving."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'exits': self.exits.copy(),
            'items': self.items.copy(),
            'enemy_id': self.enemy_id,
            'chest': self.chest.copy() if self.chest else None,
            'visited': self.visited,
            'locked_exits': self.locked_exits.copy()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        """Create room from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            short_description=data.get('short_description', data['description'][:100]),
            exits=data.get('exits', {}).copy(),
            items=data.get('items', []).copy(),
            enemy_id=data.get('enemy_id'),
            chest=data.get('chest', {}).copy() if data.get('chest') else None,
            visited=data.get('visited', False),
            locked_exits=data.get('locked_exits', {}).copy(),
            data=data  # Store full data for lore_objects and other custom fields
        )

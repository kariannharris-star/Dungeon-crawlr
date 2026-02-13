"""Game state manager - Central game state and command execution."""
import json
from typing import Optional, Callable
from ..entities.player import Player
from ..entities.enemy import Enemy
from ..world.dungeon import Dungeon
from ..world.room import Room


class GameState:
    """Manages the overall game state."""

    def __init__(self):
        self.player: Optional[Player] = None
        self.dungeon: Dungeon = Dungeon()
        self.current_room_id: str = ""
        self.enemies: dict[str, Enemy] = {}
        self.items_data: dict = {}
        self.enemies_data: dict = {}
        self.in_combat: bool = False
        self.current_enemy: Optional[Enemy] = None
        self.game_won: bool = False
        self.game_over: bool = False

    @property
    def current_room(self) -> Optional[Room]:
        """Get the current room."""
        return self.dungeon.get_room(self.current_room_id)

    def initialize_new_game(self, player_name: str) -> None:
        """Initialize a new game with the given player name."""
        self.player = Player(name=player_name)
        self.current_room_id = self.dungeon.starting_room_id
        self.game_won = False
        self.game_over = False
        self.in_combat = False
        self.current_enemy = None
        self._spawn_enemies()

        # Mark starting room as visited
        if self.current_room:
            self.current_room.mark_visited()

    def load_items_data(self, filepath: str) -> bool:
        """Load item definitions from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.items_data = {item['id']: item for item in data.get('items', [])}
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading items: {e}")
            return False

    def load_enemies_data(self, filepath: str) -> bool:
        """Load enemy definitions from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.enemies_data = {enemy['id']: enemy for enemy in data.get('enemies', [])}
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading enemies: {e}")
            return False

    def _spawn_enemies(self) -> None:
        """Spawn enemies in rooms based on room data."""
        self.enemies = {}
        for room_id, room in self.dungeon.rooms.items():
            if room.enemy_id and room.enemy_id in self.enemies_data:
                enemy_data = self.enemies_data[room.enemy_id].copy()
                self.enemies[room_id] = Enemy.from_dict(enemy_data)

    def get_room_enemy(self, room_id: Optional[str] = None) -> Optional[Enemy]:
        """Get the enemy in a room (defaults to current room)."""
        if room_id is None:
            room_id = self.current_room_id
        return self.enemies.get(room_id)

    def get_item_data(self, item_id: str) -> dict:
        """Get item data by ID."""
        return self.items_data.get(item_id, {})

    def move_to_room(self, room_id: str) -> bool:
        """Move player to a different room."""
        room = self.dungeon.get_room(room_id)
        if room:
            self.current_room_id = room_id
            room.mark_visited()

            # Check for enemy
            enemy = self.get_room_enemy()
            if enemy and enemy.is_alive():
                self.in_combat = True
                self.current_enemy = enemy

            return True
        return False

    def can_move(self, direction: str) -> tuple[bool, str]:
        """
        Check if player can move in the given direction.
        Returns (can_move, reason).
        """
        room = self.current_room
        if not room:
            return False, "No current room."

        if not room.has_exit(direction):
            return False, f"There is no exit to the {direction}."

        if room.is_exit_locked(direction):
            key_needed = room.get_required_key(direction)
            if self.player and self.player.has_item(key_needed):
                return True, f"You use the {key_needed} to unlock the door."
            return False, f"The way {direction} is locked. You need a key."

        return True, ""

    def try_move(self, direction: str) -> tuple[bool, str]:
        """Attempt to move in a direction. Returns (success, message)."""
        can, msg = self.can_move(direction)
        if not can:
            return False, msg

        room = self.current_room
        if room.is_exit_locked(direction):
            key_needed = room.get_required_key(direction)
            room.unlock_exit(direction)
            next_room_id = room.get_exit(direction)
            self.move_to_room(next_room_id)
            return True, f"You use the {key_needed} to unlock the door and proceed {direction}."

        next_room_id = room.get_exit(direction)
        self.move_to_room(next_room_id)
        return True, ""

    def check_victory(self) -> bool:
        """Check if victory conditions are met."""
        if self.player and self.player.has_item('warlord_amulet'):
            self.game_won = True
            return True
        return False

    def is_won(self) -> bool:
        """Check if the game has been won."""
        return self.game_won

    def is_over(self) -> bool:
        """Check if the game is over (player died)."""
        return self.game_over or (self.player and not self.player.is_alive())

    def end_combat(self) -> None:
        """End the current combat."""
        self.in_combat = False
        self.current_enemy = None

    def to_dict(self) -> dict:
        """Convert game state to dictionary for saving."""
        return {
            'version': '1.0',
            'player': self.player.to_dict() if self.player else None,
            'current_room': self.current_room_id,
            'dungeon_state': self.dungeon.to_dict(),
            'enemies_state': {
                room_id: enemy.to_dict()
                for room_id, enemy in self.enemies.items()
            },
            'game_won': self.game_won
        }

    def restore_from_dict(self, data: dict) -> bool:
        """Restore game state from dictionary."""
        try:
            if data.get('player'):
                self.player = Player.from_dict(data['player'])

            self.current_room_id = data.get('current_room', self.dungeon.starting_room_id)

            if data.get('dungeon_state'):
                self.dungeon.restore_state(data['dungeon_state'])

            if data.get('enemies_state'):
                for room_id, enemy_data in data['enemies_state'].items():
                    self.enemies[room_id] = Enemy.from_dict(enemy_data)

            self.game_won = data.get('game_won', False)
            return True
        except Exception as e:
            print(f"Error restoring game state: {e}")
            return False

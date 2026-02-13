"""Dungeon class - Manages the dungeon map and room graph."""
import json
from typing import Optional
from .room import Room


class Dungeon:
    """Manages the dungeon map and all rooms."""

    def __init__(self):
        self.rooms: dict[str, Room] = {}
        self.starting_room_id: str = "entrance_hall"

    def load_from_file(self, filepath: str) -> bool:
        """Load dungeon rooms from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for room_data in data.get('rooms', []):
                room = Room.from_dict(room_data)
                self.rooms[room.id] = room

            self.starting_room_id = data.get('starting_room', 'entrance_hall')
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dungeon: {e}")
            return False

    def load_from_dict(self, data: dict) -> None:
        """Load dungeon from a dictionary."""
        for room_data in data.get('rooms', []):
            room = Room.from_dict(room_data)
            self.rooms[room.id] = room
        self.starting_room_id = data.get('starting_room', 'entrance_hall')

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID."""
        return self.rooms.get(room_id)

    def get_starting_room(self) -> Optional[Room]:
        """Get the starting room."""
        return self.rooms.get(self.starting_room_id)

    def get_adjacent_room(self, room_id: str, direction: str) -> Optional[Room]:
        """Get the room adjacent to the given room in the specified direction."""
        room = self.get_room(room_id)
        if room and room.has_exit(direction):
            next_room_id = room.get_exit(direction)
            return self.get_room(next_room_id)
        return None

    def get_all_room_ids(self) -> list[str]:
        """Get all room IDs in the dungeon."""
        return list(self.rooms.keys())

    def get_discovered_rooms(self) -> list[Room]:
        """Get all rooms that have been visited."""
        return [room for room in self.rooms.values() if room.visited]

    def reset_all_rooms(self) -> None:
        """Reset all rooms to their initial state."""
        for room in self.rooms.values():
            room.visited = False

    def to_dict(self) -> dict:
        """Convert dungeon state to dictionary for saving."""
        return {
            'starting_room': self.starting_room_id,
            'room_states': {
                room_id: {
                    'visited': room.visited,
                    'items': room.items.copy(),
                    'chest': room.chest.copy() if room.chest else None,
                    'enemy_defeated': room.enemy_id is None
                }
                for room_id, room in self.rooms.items()
            }
        }

    def restore_state(self, state: dict) -> None:
        """Restore dungeon state from saved data."""
        room_states = state.get('room_states', {})
        for room_id, room_state in room_states.items():
            room = self.rooms.get(room_id)
            if room:
                room.visited = room_state.get('visited', False)
                room.items = room_state.get('items', []).copy()
                if room_state.get('chest'):
                    room.chest = room_state['chest'].copy()

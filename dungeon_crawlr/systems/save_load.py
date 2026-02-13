"""Save/Load system - JSON-based game state persistence."""
import json
import os
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..engine.game import GameState


DEFAULT_SAVE_PATH = "save_game.json"


class SaveLoadSystem:
    """Manages saving and loading game state."""

    @staticmethod
    def save_game(game_state: 'GameState', filepath: str = None) -> Tuple[bool, str]:
        """
        Save the current game state to a JSON file.
        Returns (success, message).
        """
        if filepath is None:
            filepath = DEFAULT_SAVE_PATH

        try:
            save_data = game_state.to_dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
            return True, f"Game saved successfully to {filepath}."
        except IOError as e:
            return False, f"Failed to save game: {e}"
        except Exception as e:
            return False, f"An error occurred while saving: {e}"

    @staticmethod
    def load_game(game_state: 'GameState', filepath: str = None) -> Tuple[bool, str]:
        """
        Load game state from a JSON file.
        Returns (success, message).
        """
        if filepath is None:
            filepath = DEFAULT_SAVE_PATH

        if not os.path.exists(filepath):
            return False, f"Save file not found: {filepath}"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Validate version
            version = save_data.get('version', '1.0')
            if not version.startswith('1.'):
                return False, f"Incompatible save file version: {version}"

            # Restore state
            if game_state.restore_from_dict(save_data):
                return True, "Game loaded successfully!"
            else:
                return False, "Failed to restore game state from save file."

        except json.JSONDecodeError as e:
            return False, f"Invalid save file format: {e}"
        except IOError as e:
            return False, f"Failed to read save file: {e}"
        except Exception as e:
            return False, f"An error occurred while loading: {e}"

    @staticmethod
    def save_exists(filepath: str = None) -> bool:
        """Check if a save file exists."""
        if filepath is None:
            filepath = DEFAULT_SAVE_PATH
        return os.path.exists(filepath)

    @staticmethod
    def delete_save(filepath: str = None) -> Tuple[bool, str]:
        """Delete a save file."""
        if filepath is None:
            filepath = DEFAULT_SAVE_PATH

        if not os.path.exists(filepath):
            return False, "No save file to delete."

        try:
            os.remove(filepath)
            return True, "Save file deleted."
        except IOError as e:
            return False, f"Failed to delete save file: {e}"

    @staticmethod
    def get_save_info(filepath: str = None) -> dict | None:
        """Get basic info about a save file without fully loading it."""
        if filepath is None:
            filepath = DEFAULT_SAVE_PATH

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            player_data = save_data.get('player', {})
            return {
                'player_name': player_data.get('name', 'Unknown'),
                'level': player_data.get('level', 1),
                'current_room': save_data.get('current_room', 'Unknown'),
                'gold': player_data.get('gold', 0),
            }
        except Exception:
            return None

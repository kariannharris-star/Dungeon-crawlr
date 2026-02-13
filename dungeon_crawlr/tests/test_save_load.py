"""Tests for save/load system."""
import unittest
import sys
import os
import json
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dungeon_crawlr.entities.player import Player
from dungeon_crawlr.engine.game import GameState
from dungeon_crawlr.systems.save_load import SaveLoadSystem


class TestSaveLoad(unittest.TestCase):
    """Test cases for save/load system."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.temp_dir, "test_save.json")

    def tearDown(self):
        """Clean up temp files."""
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
        os.rmdir(self.temp_dir)

    def test_save_exists_false(self):
        """Test save_exists returns False when no save."""
        self.assertFalse(SaveLoadSystem.save_exists(self.save_path))

    def test_player_to_dict(self):
        """Test player serialization to dict."""
        player = Player(
            name="TestHero",
            hp=80,
            max_hp=100,
            level=3,
            gold=50
        )
        player.add_item("sword")
        player.equipped_weapon = "sword"

        data = player.to_dict()

        self.assertEqual(data['name'], "TestHero")
        self.assertEqual(data['hp'], 80)
        self.assertEqual(data['level'], 3)
        self.assertEqual(data['gold'], 50)
        self.assertIn("sword", data['inventory'])
        self.assertEqual(data['equipped_weapon'], "sword")

    def test_player_from_dict(self):
        """Test player deserialization from dict."""
        data = {
            'name': 'LoadedHero',
            'hp': 75,
            'max_hp': 100,
            'attack': 15,
            'defense': 5,
            'level': 2,
            'xp': 30,
            'xp_to_next': 75,
            'gold': 100,
            'inventory': ['potion', 'key'],
            'equipped_weapon': 'sword',
            'equipped_armor': None,
            'max_inventory': 10
        }

        player = Player.from_dict(data)

        self.assertEqual(player.name, 'LoadedHero')
        self.assertEqual(player.hp, 75)
        self.assertEqual(player.level, 2)
        self.assertIn('potion', player.inventory)
        self.assertEqual(player.equipped_weapon, 'sword')

    def test_save_file_format(self):
        """Test saved file is valid JSON with expected fields."""
        # Create minimal game state
        game_state = GameState()
        game_state.player = Player(name="TestHero", gold=25)
        game_state.current_room_id = "test_room"

        success, msg = SaveLoadSystem.save_game(game_state, self.save_path)
        self.assertTrue(success)

        # Verify file contents
        with open(self.save_path, 'r') as f:
            data = json.load(f)

        self.assertIn('version', data)
        self.assertIn('player', data)
        self.assertIn('current_room', data)
        self.assertEqual(data['player']['name'], "TestHero")
        self.assertEqual(data['player']['gold'], 25)


class TestSaveLoadIntegration(unittest.TestCase):
    """Integration tests for save/load."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.temp_dir, "test_save.json")

    def tearDown(self):
        """Clean up temp files."""
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
        os.rmdir(self.temp_dir)

    def test_invalid_save_file(self):
        """Test loading invalid save file."""
        # Write invalid JSON
        with open(self.save_path, 'w') as f:
            f.write("not valid json")

        game_state = GameState()
        success, msg = SaveLoadSystem.load_game(game_state, self.save_path)
        self.assertFalse(success)
        self.assertIn("Invalid", msg)

    def test_missing_save_file(self):
        """Test loading nonexistent save file."""
        game_state = GameState()
        success, msg = SaveLoadSystem.load_game(game_state, "/nonexistent/path.json")
        self.assertFalse(success)
        self.assertIn("not found", msg)


if __name__ == '__main__':
    unittest.main()

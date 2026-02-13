"""Tests for inventory system."""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dungeon_crawlr.entities.player import Player
from dungeon_crawlr.world.room import Room


class TestPlayerInventory(unittest.TestCase):
    """Test cases for player inventory operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(name="TestHero", max_inventory=5)

    def test_add_item(self):
        """Test adding item to inventory."""
        result = self.player.add_item("health_potion")
        self.assertTrue(result)
        self.assertIn("health_potion", self.player.inventory)

    def test_inventory_limit(self):
        """Test inventory respects max limit."""
        for i in range(5):
            self.player.add_item(f"item_{i}")

        result = self.player.add_item("overflow_item")
        self.assertFalse(result)
        self.assertEqual(len(self.player.inventory), 5)

    def test_remove_item(self):
        """Test removing item from inventory."""
        self.player.add_item("health_potion")
        result = self.player.remove_item("health_potion")
        self.assertTrue(result)
        self.assertNotIn("health_potion", self.player.inventory)

    def test_remove_nonexistent_item(self):
        """Test removing item not in inventory."""
        result = self.player.remove_item("nonexistent")
        self.assertFalse(result)

    def test_has_item(self):
        """Test checking if player has item."""
        self.player.add_item("sword")
        self.assertTrue(self.player.has_item("sword"))
        self.assertFalse(self.player.has_item("shield"))

    def test_can_add_item(self):
        """Test checking if player can add more items."""
        self.assertTrue(self.player.can_add_item())

        for i in range(5):
            self.player.add_item(f"item_{i}")

        self.assertFalse(self.player.can_add_item())


class TestRoomItems(unittest.TestCase):
    """Test cases for room item operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.room = Room(
            id="test_room",
            name="Test Room",
            description="A test room.",
            short_description="Test room.",
            items=["sword", "potion"]
        )

    def test_room_has_items(self):
        """Test room has items check."""
        self.assertTrue(self.room.has_items())

    def test_remove_item_from_room(self):
        """Test removing item from room."""
        result = self.room.remove_item("sword")
        self.assertTrue(result)
        self.assertNotIn("sword", self.room.items)

    def test_add_item_to_room(self):
        """Test adding item to room."""
        self.room.add_item("shield")
        self.assertIn("shield", self.room.items)


if __name__ == '__main__':
    unittest.main()

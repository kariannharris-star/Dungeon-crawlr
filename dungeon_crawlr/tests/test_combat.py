"""Tests for combat system."""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dungeon_crawlr.entities.player import Player
from dungeon_crawlr.entities.enemy import Enemy
from dungeon_crawlr.systems.combat import CombatSystem


class TestCombat(unittest.TestCase):
    """Test cases for combat system."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(name="TestHero", hp=100, max_hp=100, attack=10, defense=2)
        self.enemy = Enemy(
            id="test_goblin",
            name="Test Goblin",
            hp=20,
            max_hp=20,
            attack=5,
            defense=1,
            xp_reward=15,
            gold_reward=10,
            drop_table=[],
            description="A test goblin."
        )

    def test_enemy_take_damage(self):
        """Test enemy takes damage correctly."""
        damage = self.enemy.take_damage(10)
        # damage = 10 - 1 defense = 9
        self.assertEqual(damage, 9)
        self.assertEqual(self.enemy.hp, 11)

    def test_enemy_minimum_damage(self):
        """Test enemy takes at least 1 damage."""
        damage = self.enemy.take_damage(0)
        self.assertEqual(damage, 1)

    def test_enemy_defeat(self):
        """Test enemy is defeated when HP reaches 0."""
        self.enemy.take_damage(100)
        self.assertFalse(self.enemy.is_alive())
        self.assertTrue(self.enemy.defeated)

    def test_player_take_damage(self):
        """Test player takes damage correctly."""
        damage = self.player.take_damage(10)
        # damage = 10 - 2 defense = 8
        self.assertEqual(damage, 8)
        self.assertEqual(self.player.hp, 92)

    def test_player_death(self):
        """Test player death when HP reaches 0."""
        self.player.take_damage(200)
        self.assertFalse(self.player.is_alive())
        self.assertEqual(self.player.hp, 0)

    def test_player_heal(self):
        """Test player healing."""
        self.player.hp = 50
        healed = self.player.heal(30)
        self.assertEqual(healed, 30)
        self.assertEqual(self.player.hp, 80)

    def test_player_heal_cap(self):
        """Test healing doesn't exceed max HP."""
        self.player.hp = 90
        healed = self.player.heal(30)
        self.assertEqual(healed, 10)
        self.assertEqual(self.player.hp, 100)

    def test_xp_gain(self):
        """Test XP gain."""
        leveled = self.player.gain_xp(25)
        self.assertFalse(leveled)
        self.assertEqual(self.player.xp, 25)

    def test_level_up(self):
        """Test leveling up."""
        self.player.xp_to_next = 50
        leveled = self.player.gain_xp(50)
        self.assertTrue(leveled)
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.attack, 12)  # +2 attack
        self.assertEqual(self.player.defense, 3)  # +1 defense
        self.assertEqual(self.player.max_hp, 110)  # +10 max HP


class TestCombatSystem(unittest.TestCase):
    """Test cases for CombatSystem class."""

    def test_calculate_enemy_damage(self):
        """Test enemy damage calculation."""
        enemy = Enemy(
            id="test", name="Test", hp=20, max_hp=20,
            attack=8, defense=2, xp_reward=10, gold_reward=5
        )
        damage = CombatSystem.calculate_enemy_damage(enemy)
        self.assertEqual(damage, 8)


if __name__ == '__main__':
    unittest.main()

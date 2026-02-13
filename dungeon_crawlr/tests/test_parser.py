"""Tests for command parser."""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dungeon_crawlr.engine.parser import parse_command, normalize_direction, validate_direction


class TestParser(unittest.TestCase):
    """Test cases for command parsing."""

    def test_empty_input(self):
        """Test empty input returns empty command."""
        cmd, args = parse_command('')
        self.assertEqual(cmd, '')
        self.assertEqual(args, [])

    def test_whitespace_input(self):
        """Test whitespace-only input returns empty command."""
        cmd, args = parse_command('   ')
        self.assertEqual(cmd, '')
        self.assertEqual(args, [])

    def test_simple_command(self):
        """Test basic single-word command."""
        cmd, args = parse_command('look')
        self.assertEqual(cmd, 'look')
        self.assertEqual(args, [])

    def test_command_with_args(self):
        """Test command with arguments."""
        cmd, args = parse_command('move north')
        self.assertEqual(cmd, 'move')
        self.assertEqual(args, ['north'])

    def test_direction_aliases(self):
        """Test direction shorthand aliases."""
        cmd, args = parse_command('n')
        self.assertEqual(cmd, 'move')
        self.assertEqual(args, ['north'])

        cmd, args = parse_command('s')
        self.assertEqual(cmd, 'move')
        self.assertEqual(args, ['south'])

    def test_command_aliases(self):
        """Test command aliases."""
        cmd, args = parse_command('go north')
        self.assertEqual(cmd, 'move')
        self.assertEqual(args, ['north'])

        cmd, args = parse_command('i')
        self.assertEqual(cmd, 'inventory')

        cmd, args = parse_command('l')
        self.assertEqual(cmd, 'look')

    def test_case_insensitivity(self):
        """Test commands are case insensitive."""
        cmd, args = parse_command('LOOK')
        self.assertEqual(cmd, 'look')

        cmd, args = parse_command('Move North')
        self.assertEqual(cmd, 'move')
        self.assertEqual(args, ['north'])

    def test_pick_up_alias(self):
        """Test 'pick up' as alias for take."""
        cmd, args = parse_command('pick up sword')
        self.assertEqual(cmd, 'take')
        self.assertEqual(args, ['sword'])

    def test_normalize_direction(self):
        """Test direction normalization."""
        self.assertEqual(normalize_direction('n'), 'north')
        self.assertEqual(normalize_direction('s'), 'south')
        self.assertEqual(normalize_direction('e'), 'east')
        self.assertEqual(normalize_direction('w'), 'west')
        self.assertEqual(normalize_direction('north'), 'north')

    def test_validate_direction(self):
        """Test direction validation."""
        self.assertTrue(validate_direction('north'))
        self.assertTrue(validate_direction('south'))
        self.assertTrue(validate_direction('east'))
        self.assertTrue(validate_direction('west'))
        self.assertTrue(validate_direction('up'))
        self.assertTrue(validate_direction('down'))
        self.assertFalse(validate_direction('sideways'))
        self.assertFalse(validate_direction(''))


if __name__ == '__main__':
    unittest.main()

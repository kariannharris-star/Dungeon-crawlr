"""Command parser - Handles user input and command parsing."""
from typing import Tuple, Optional
import re


# Command aliases mapping
ALIASES = {
    # Movement
    'go': 'move',
    'walk': 'move',
    'n': 'move north',
    's': 'move south',
    'e': 'move east',
    'w': 'move west',
    'u': 'move up',
    'd': 'move down',
    'north': 'move north',
    'south': 'move south',
    'east': 'move east',
    'west': 'move west',
    'up': 'move up',
    'down': 'move down',

    # Look
    'l': 'look',
    'inspect': 'examine',
    'study': 'examine',
    'read': 'examine',

    # Combat
    'fight': 'attack',
    'a': 'attack',
    'run': 'flee',
    'escape': 'flee',

    # Inventory
    'inv': 'inventory',
    'i': 'inventory',
    'pick': 'take',
    'grab': 'take',

    # Stats
    'status': 'stats',

    # Help
    '?': 'help',

    # Quit
    'exit': 'quit',
    'q': 'quit',
}

# Direction aliases
DIRECTION_ALIASES = {
    'n': 'north',
    's': 'south',
    'e': 'east',
    'w': 'west',
    'u': 'up',
    'd': 'down',
}


def normalize_direction(direction: str) -> str:
    """Normalize direction aliases to full direction names."""
    return DIRECTION_ALIASES.get(direction.lower(), direction.lower())


def parse_command(raw_input: str) -> Tuple[str, list]:
    """
    Parse raw user input into a command and arguments.

    Returns:
        Tuple of (command, [arguments])
    """
    # Handle empty or whitespace-only input
    if not raw_input or not raw_input.strip():
        return ('', [])

    # Clean and normalize input
    cleaned = raw_input.strip().lower()

    # Remove special characters except spaces
    cleaned = re.sub(r'[^\w\s]', '', cleaned)

    # Split into parts
    parts = cleaned.split()

    if not parts:
        return ('', [])

    # Get the first word as potential command
    first_word = parts[0]
    rest = parts[1:]

    # Check if entire input matches an alias (like 'n' for 'move north')
    if cleaned in ALIASES:
        expanded = ALIASES[cleaned].split()
        return (expanded[0], expanded[1:])

    # Handle "pick up" as two-word command BEFORE single-word aliases
    if first_word == 'pick' and rest and rest[0] == 'up':
        return ('take', rest[1:])

    # Check if first word is an alias
    if first_word in ALIASES:
        expanded = ALIASES[first_word]
        if ' ' in expanded:
            # Alias expands to command + arg (like 'go' -> 'move')
            exp_parts = expanded.split()
            return (exp_parts[0], exp_parts[1:] + rest)
        else:
            return (expanded, rest)

    # Handle "open chest" specially
    if first_word == 'open':
        return ('open', rest)

    # Normalize direction for move commands
    if first_word == 'move' and rest:
        rest[0] = normalize_direction(rest[0])

    return (first_word, rest)


def get_item_name_from_args(args: list) -> str:
    """Join args into a single item name."""
    return ' '.join(args).strip()


def parse_look_target(args: list) -> Optional[str]:
    """Parse target for look command."""
    if not args:
        return None
    return ' '.join(args).strip()


def validate_direction(direction: str) -> bool:
    """Check if a direction is valid."""
    valid_directions = {'north', 'south', 'east', 'west', 'up', 'down'}
    return direction.lower() in valid_directions

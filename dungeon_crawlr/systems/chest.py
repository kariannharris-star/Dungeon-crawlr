"""Chest system - Handles chest interaction logic."""
import random
from typing import TYPE_CHECKING, Tuple, List

if TYPE_CHECKING:
    from ..engine.game import GameState


# Loot tables by tier
LOOT_TABLES = {
    'common': [
        {'item_id': 'health_potion', 'weight': 40},
        {'item_id': 'gold_small', 'weight': 40},
        {'item_id': 'short_sword', 'weight': 20},
    ],
    'uncommon': [
        {'item_id': 'greater_health_potion', 'weight': 25},
        {'item_id': 'leather_armor', 'weight': 20},
        {'item_id': 'spell_scroll', 'weight': 25},
        {'item_id': 'gold_medium', 'weight': 30},
    ],
    'rare': [
        {'item_id': 'iron_sword', 'weight': 30},
        {'item_id': 'iron_shield', 'weight': 25},
        {'item_id': 'gold_large', 'weight': 30},
        {'item_id': 'antidote', 'weight': 15},
    ]
}


class ChestSystem:
    """Manages chest interactions."""

    @staticmethod
    def get_chest_in_room(game_state: 'GameState') -> dict | None:
        """Get the chest in the current room, if any."""
        room = game_state.current_room
        if room and room.has_chest():
            return room.chest
        return None

    @staticmethod
    def open_chest(game_state: 'GameState') -> Tuple[bool, str, List[str]]:
        """
        Attempt to open the chest in the current room.
        Returns (success, message, list_of_items_obtained).
        """
        room = game_state.current_room
        player = game_state.player

        if not room or not player:
            return False, "Invalid game state.", []

        if not room.has_chest():
            return False, "There is no chest here.", []

        chest = room.chest

        if chest.get('opened', False):
            return False, "The chest has already been opened.", []

        state = chest.get('state', 'unlocked')

        # Handle locked chest
        if state == 'locked':
            key_required = chest.get('key_required')
            if key_required and not player.has_item(key_required):
                key_data = game_state.get_item_data(key_required)
                key_name = key_data.get('name', key_required)
                return False, f"The chest is locked. You need {key_name}.", []

        # Handle trapped chest
        trap_damage = 0
        trap_message = ""
        if state == 'trapped':
            trap_damage = chest.get('trap_damage', 10)
            player.hp = max(1, player.hp - trap_damage)
            trap_message = f"The chest was trapped! You take {trap_damage} damage. "

        # Handle mimic
        if state == 'mimic':
            # Spawn a mimic enemy
            mimic_id = 'mimic'
            if mimic_id in game_state.enemies_data:
                from ..entities.enemy import Enemy
                mimic_data = game_state.enemies_data[mimic_id].copy()
                game_state.enemies[game_state.current_room_id] = Enemy.from_dict(mimic_data)
                game_state.current_enemy = game_state.enemies[game_state.current_room_id]
                game_state.in_combat = True
                room.chest['opened'] = True
                return False, "The chest springs to life! It's a MIMIC!", []

        # Open the chest and get loot
        items_obtained = []
        messages = []

        # Fixed loot
        fixed_loot = chest.get('fixed_loot', [])
        for item_id in fixed_loot:
            if player.can_add_item():
                player.add_item(item_id)
                item_data = game_state.get_item_data(item_id)
                items_obtained.append(item_data.get('name', item_id))

        # Random loot from tier
        loot_tier = chest.get('loot_tier')
        if loot_tier and loot_tier in LOOT_TABLES:
            rolled_item = ChestSystem._roll_loot(loot_tier)
            if rolled_item and player.can_add_item():
                # Handle gold items specially
                if rolled_item.startswith('gold_'):
                    gold_amount = ChestSystem._roll_gold(loot_tier)
                    player.add_gold(gold_amount)
                    items_obtained.append(f"{gold_amount} gold")
                else:
                    player.add_item(rolled_item)
                    item_data = game_state.get_item_data(rolled_item)
                    items_obtained.append(item_data.get('name', rolled_item))

        # Mark chest as opened
        room.chest['opened'] = True

        if items_obtained:
            loot_msg = f"You found: {', '.join(items_obtained)}!"
            final_message = trap_message + "You open the chest. " + loot_msg
        else:
            final_message = trap_message + "You open the chest, but it's empty."

        return True, final_message, items_obtained

    @staticmethod
    def _roll_loot(tier: str) -> str | None:
        """Roll for random loot from a tier."""
        table = LOOT_TABLES.get(tier, [])
        if not table:
            return None

        total_weight = sum(entry['weight'] for entry in table)
        roll = random.randint(1, total_weight)

        cumulative = 0
        for entry in table:
            cumulative += entry['weight']
            if roll <= cumulative:
                return entry['item_id']

        return None

    @staticmethod
    def _roll_gold(tier: str) -> int:
        """Roll for gold amount based on tier."""
        ranges = {
            'common': (5, 15),
            'uncommon': (15, 30),
            'rare': (30, 60),
        }
        min_gold, max_gold = ranges.get(tier, (5, 15))
        return random.randint(min_gold, max_gold)

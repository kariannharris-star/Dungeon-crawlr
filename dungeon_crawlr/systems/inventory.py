"""Inventory system - Handles item pickup, drop, use, and equip."""
import random
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..engine.game import GameState


class InventorySystem:
    """Manages inventory operations."""

    @staticmethod
    def take_item(game_state: 'GameState', item_name: str) -> Tuple[bool, str]:
        """
        Pick up an item from the current room.
        Returns (success, message).
        """
        room = game_state.current_room
        player = game_state.player

        if not room or not player:
            return False, "Invalid game state."

        # Find item by name (case-insensitive partial match)
        item_id = None
        for i_id in room.items:
            item_data = game_state.get_item_data(i_id)
            if item_name.lower() in item_data.get('name', i_id).lower():
                item_id = i_id
                break

        if not item_id:
            return False, f"There is no '{item_name}' here."

        if not player.can_add_item():
            return False, "Your inventory is full."

        room.remove_item(item_id)
        player.add_item(item_id)

        item_data = game_state.get_item_data(item_id)
        item_name = item_data.get('name', item_id)

        return True, f"You picked up {item_name}."

    @staticmethod
    def take_all_items(game_state: 'GameState') -> Tuple[bool, str]:
        """
        Pick up all items from the current room.
        Returns (success, message).
        """
        room = game_state.current_room
        player = game_state.player

        if not room or not player:
            return False, "Invalid game state."

        if not room.items:
            return False, "There's nothing here to pick up."

        picked_up = []
        failed = []

        # Make a copy since we're modifying the list
        items_to_take = list(room.items)

        for item_id in items_to_take:
            if not player.can_add_item():
                item_data = game_state.get_item_data(item_id)
                failed.append(item_data.get('name', item_id))
                continue

            room.remove_item(item_id)
            player.add_item(item_id)
            item_data = game_state.get_item_data(item_id)
            picked_up.append(item_data.get('name', item_id))

        if not picked_up:
            return False, "Your inventory is full."

        message = f"You picked up: {', '.join(picked_up)}."
        if failed:
            message += f" (Inventory full, couldn't take: {', '.join(failed)})"

        return True, message

    @staticmethod
    def drop_item(game_state: 'GameState', item_name: str) -> Tuple[bool, str]:
        """
        Drop an item from inventory into the current room.
        Returns (success, message).
        """
        room = game_state.current_room
        player = game_state.player

        if not room or not player:
            return False, "Invalid game state."

        # Find item by name
        item_id = None
        for i_id in player.inventory:
            item_data = game_state.get_item_data(i_id)
            if item_name.lower() in item_data.get('name', i_id).lower():
                item_id = i_id
                break

        if not item_id:
            return False, f"You don't have '{item_name}' in your inventory."

        # Can't drop equipped items
        if item_id == player.equipped_weapon or item_id == player.equipped_armor:
            return False, "You must unequip that item first."

        player.remove_item(item_id)
        room.add_item(item_id)

        item_data = game_state.get_item_data(item_id)
        item_name = item_data.get('name', item_id)

        return True, f"You dropped {item_name}."

    @staticmethod
    def use_item(game_state: 'GameState', item_name: str) -> Tuple[bool, str]:
        """
        Use a consumable item.
        Returns (success, message).
        """
        player = game_state.player

        if not player:
            return False, "Invalid game state."

        # Find item by name
        item_id = None
        for i_id in player.inventory:
            item_data = game_state.get_item_data(i_id)
            if item_name.lower() in item_data.get('name', i_id).lower():
                item_id = i_id
                break

        if not item_id:
            return False, f"You don't have '{item_name}' in your inventory."

        item_data = game_state.get_item_data(item_id)
        item_type = item_data.get('item_type', 'misc')
        name = item_data.get('name', item_id)

        if item_type != 'consumable':
            return False, f"You can't use {name} like that."

        # Apply effect
        effect_type = item_data.get('effect_type', '')
        effect_value = item_data.get('effect_value', 0)

        message = ""
        if effect_type == 'heal':
            healed = player.heal(effect_value)
            message = f"You used {name} and restored {healed} HP."

        elif effect_type == 'damage':
            # Used in combat on enemy
            if game_state.in_combat and game_state.current_enemy:
                damage = game_state.current_enemy.take_damage(effect_value)
                message = f"You used {name} and dealt {damage} damage to {game_state.current_enemy.name}!"
            else:
                return False, "You can only use this in combat."

        elif effect_type == 'lifesteal':
            # Damage enemy and heal self
            if game_state.in_combat and game_state.current_enemy:
                damage = game_state.current_enemy.take_damage(effect_value)
                healed = player.heal(effect_value)
                message = f"You used {name}! Drained {damage} life from {game_state.current_enemy.name} and restored {healed} HP!"
            else:
                return False, "You can only use this in combat."

        elif effect_type == 'teleport':
            # Random teleport to any visited room
            visited_rooms = [r_id for r_id, room in game_state.dungeon.rooms.items() if room.visited]
            if visited_rooms:
                new_room = random.choice(visited_rooms)
                game_state.current_room_id = new_room
                game_state.in_combat = False
                game_state.current_enemy = None
                room_name = game_state.current_room.name
                message = f"You tear open a rift in space! Reality twists and bends... You find yourself in {room_name}!"
            else:
                message = f"You used {name} but nothing happened... the magic fizzles."

        elif effect_type == 'recall':
            # Teleport back to village
            game_state.current_room_id = "village_square"
            game_state.in_combat = False
            game_state.current_enemy = None
            message = f"A shimmering portal opens before you! You step through and emerge in Thornwick Village, safe at last."

        elif effect_type == 'timestop':
            # Guaranteed escape from combat
            if game_state.in_combat:
                game_state.in_combat = False
                game_state.current_enemy = None
                message = f"Time FREEZES! The world turns grey and silent. You walk calmly away from danger as your enemy stands frozen in mid-strike. Time resumes behind you."
            else:
                message = f"You used {name}, but there was nothing to escape from. The magic fades unused."

        elif effect_type == 'chaos':
            # Random effect!
            chaos_effects = ['heal_big', 'heal_small', 'damage_big', 'damage_small', 'teleport', 'gold', 'nothing', 'hurt_self']
            effect = random.choice(chaos_effects)

            if effect == 'heal_big':
                healed = player.heal(100)
                message = f"CHAOS MAGIC surges! A wave of healing energy washes over you! Restored {healed} HP!"
            elif effect == 'heal_small':
                healed = player.heal(25)
                message = f"Chaos magic fizzles... but you feel slightly better. Restored {healed} HP."
            elif effect == 'damage_big' and game_state.in_combat and game_state.current_enemy:
                damage = game_state.current_enemy.take_damage(80)
                message = f"CHAOS ERUPTS! Reality tears apart around your enemy! {damage} damage!"
            elif effect == 'damage_small' and game_state.in_combat and game_state.current_enemy:
                damage = game_state.current_enemy.take_damage(20)
                message = f"Chaos sparks! A small explosion hits your enemy for {damage} damage."
            elif effect == 'teleport':
                visited_rooms = [r_id for r_id, room in game_state.dungeon.rooms.items() if room.visited]
                if visited_rooms:
                    new_room = random.choice(visited_rooms)
                    game_state.current_room_id = new_room
                    game_state.in_combat = False
                    game_state.current_enemy = None
                    message = f"CHAOS TELEPORT! The world spins and you appear somewhere else entirely!"
                else:
                    message = f"Chaos swirls around you... then dissipates harmlessly."
            elif effect == 'gold':
                gold_gained = random.randint(10, 100)
                player.gold += gold_gained
                message = f"CHAOS becomes ORDER! Gold coins materialize from thin air! +{gold_gained} gold!"
            elif effect == 'hurt_self':
                damage = random.randint(10, 30)
                player.take_damage(damage)
                message = f"CHAOS BACKFIRES! The magic turns against you! You take {damage} damage!"
            else:
                message = f"Chaos swirls... and fades. Nothing happens. How anticlimactic."

        elif effect_type == 'cure':
            message = f"You used {name} and feel refreshed."

        elif effect_type == 'drink':
            # Flavor text for drinks - they don't do anything mechanical
            drink_messages = [
                f"You drink the {name}. It goes down smooth. Or rough. Either way, it's gone now.",
                f"You savor the {name}. For a moment, you forget you're about to fight monsters.",
                f"The {name} warms your belly. Or was that heartburn? Hard to tell.",
                f"You raise the {name} in a silent toast to fallen adventurers, then drink deep.",
                f"Ahh, {name}. Just what you needed. Does it help in combat? No. Does it help your mood? Absolutely.",
            ]
            message = random.choice(drink_messages)

        else:
            message = f"You used {name}."

        # Remove item from inventory
        player.remove_item(item_id)

        return True, message

    @staticmethod
    def equip_item(game_state: 'GameState', item_name: str) -> Tuple[bool, str]:
        """
        Equip a weapon or armor.
        Returns (success, message).
        """
        player = game_state.player

        if not player:
            return False, "Invalid game state."

        # Find item by name
        item_id = None
        for i_id in player.inventory:
            item_data = game_state.get_item_data(i_id)
            if item_name.lower() in item_data.get('name', i_id).lower():
                item_id = i_id
                break

        if not item_id:
            return False, f"You don't have '{item_name}' in your inventory."

        item_data = game_state.get_item_data(item_id)
        item_type = item_data.get('item_type', 'misc')
        name = item_data.get('name', item_id)

        if item_type == 'weapon':
            old_weapon = player.equipped_weapon
            player.equipped_weapon = item_id
            msg = f"You equipped {name}."
            if old_weapon:
                old_data = game_state.get_item_data(old_weapon)
                msg += f" (Unequipped {old_data.get('name', old_weapon)})"
            return True, msg

        elif item_type == 'armor':
            old_armor = player.equipped_armor
            player.equipped_armor = item_id
            msg = f"You equipped {name}."
            if old_armor:
                old_data = game_state.get_item_data(old_armor)
                msg += f" (Unequipped {old_data.get('name', old_armor)})"
            return True, msg

        return False, f"You can't equip {name}."

    @staticmethod
    def get_weapon_damage(game_state: 'GameState') -> int:
        """Get the damage bonus from equipped weapon."""
        player = game_state.player
        if not player or not player.equipped_weapon:
            return 0

        item_data = game_state.get_item_data(player.equipped_weapon)
        return item_data.get('damage', 0)

    @staticmethod
    def get_armor_defense(game_state: 'GameState') -> int:
        """Get the defense bonus from equipped armor."""
        player = game_state.player
        if not player or not player.equipped_armor:
            return 0

        item_data = game_state.get_item_data(player.equipped_armor)
        return item_data.get('defense_bonus', 0)

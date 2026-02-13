"""Fountain system - Handles magical fountain interactions."""
import random
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..engine.game import GameState


class FountainSystem:
    """Manages magical fountain interactions."""

    # Track which fountains have been used (by room_id)
    used_fountains: set = set()

    @staticmethod
    def has_fountain(game_state: 'GameState') -> bool:
        """Check if current room has a fountain."""
        room = game_state.current_room
        if room:
            room_dict = room.to_dict()
            return room_dict.get('has_fountain', False)
        return False

    @staticmethod
    def is_fountain_used(room_id: str) -> bool:
        """Check if a fountain has already been used."""
        return room_id in FountainSystem.used_fountains

    @staticmethod
    def drink_from_fountain(game_state: 'GameState') -> Tuple[bool, str]:
        """
        Drink from the fountain in the current room.
        Returns (success, message).
        """
        room = game_state.current_room
        player = game_state.player

        if not room or not player:
            return False, "Invalid game state."

        room_dict = room.to_dict()
        if not room_dict.get('has_fountain', False):
            return False, "There's no fountain here."

        room_id = room.id
        if room_id in FountainSystem.used_fountains:
            return False, "The fountain's magic has been depleted. The water is now ordinary."

        # Mark fountain as used
        FountainSystem.used_fountains.add(room_id)

        # Get possible effects
        effects = room_dict.get('fountain_effects', ['heal'])

        # Choose random effect
        effect = random.choice(effects)

        # Apply effect
        return FountainSystem._apply_effect(game_state, effect, room.name)

    @staticmethod
    def _apply_effect(game_state: 'GameState', effect: str, fountain_name: str) -> Tuple[bool, str]:
        """Apply a fountain effect to the player."""
        player = game_state.player

        if effect == 'heal':
            heal_amount = random.randint(30, 60)
            actual_heal = player.heal(heal_amount)
            return True, f"The water fills you with warmth. You feel restored! (+{actual_heal} HP)"

        elif effect == 'major_heal':
            actual_heal = player.heal(player.max_hp)
            return True, f"Divine energy surges through you! Your wounds close completely! (+{actual_heal} HP)"

        elif effect == 'full_heal':
            old_hp = player.hp
            player.hp = player.max_hp
            player.max_hp += 20
            player.hp = player.max_hp
            return True, f"The starlight water transforms you! Full heal and +20 max HP!"

        elif effect == 'damage':
            damage = random.randint(10, 25)
            player.hp = max(1, player.hp - damage)
            return True, f"The water burns like acid! (-{damage} HP) You barely survive..."

        elif effect == 'major_damage':
            damage = random.randint(30, 50)
            player.hp = max(1, player.hp - damage)
            return True, f"The blood fountain demands sacrifice! (-{damage} HP)"

        elif effect == 'buff_attack':
            buff = random.randint(2, 5)
            player.attack += buff
            return True, f"Power flows into your arms! (+{buff} Attack permanently!)"

        elif effect == 'buff_attack_large':
            buff = random.randint(5, 10)
            player.attack += buff
            return True, f"Unholy strength surges through you! (+{buff} Attack permanently!)"

        elif effect == 'buff_defense':
            buff = random.randint(1, 3)
            player.defense += buff
            return True, f"Your skin hardens like stone! (+{buff} Defense permanently!)"

        elif effect == 'gold':
            gold = random.randint(25, 75)
            player.gold += gold
            return True, f"Gold coins materialize in your hands! (+{gold} gold!)"

        elif effect == 'gold_large':
            gold = random.randint(75, 150)
            player.gold += gold
            return True, f"A fortune appears before you! (+{gold} gold!)"

        elif effect == 'gold_massive':
            gold = random.randint(200, 500)
            player.gold += gold
            return True, f"Treasure beyond imagining materializes! (+{gold} gold!)"

        elif effect == 'level_up':
            player._level_up()
            return True, f"The fountain grants you wisdom! You gained a level! (Now level {player.level})"

        elif effect == 'curse':
            curse_type = random.choice(['attack', 'defense', 'hp'])
            if curse_type == 'attack':
                loss = random.randint(1, 3)
                player.attack = max(1, player.attack - loss)
                return True, f"A curse weakens you! (-{loss} Attack permanently...)"
            elif curse_type == 'defense':
                loss = random.randint(1, 2)
                player.defense = max(0, player.defense - loss)
                return True, f"A curse weakens you! (-{loss} Defense permanently...)"
            else:
                loss = random.randint(10, 20)
                player.max_hp = max(20, player.max_hp - loss)
                player.hp = min(player.hp, player.max_hp)
                return True, f"A curse weakens you! (-{loss} Max HP permanently...)"

        elif effect == 'curse_or_blessing':
            if random.random() < 0.7:  # 70% blessing
                player.attack += 5
                player.defense += 3
                player.max_hp += 25
                player.hp = player.max_hp
                return True, "The stars bless you! +5 ATK, +3 DEF, +25 Max HP, full heal!"
            else:
                player.attack = max(1, player.attack - 3)
                player.defense = max(0, player.defense - 2)
                return True, "The stars curse you! -3 ATK, -2 DEF..."

        elif effect == 'random_weapon':
            weapons = ['iron_sword', 'battle_axe', 'war_hammer', 'silver_rapier',
                      'executioners_sword', 'dwarven_axe', 'flamberge', 'shadow_blade']
            weapon = random.choice(weapons)
            if player.can_add_item():
                player.add_item(weapon)
                item_data = game_state.get_item_data(weapon)
                name = item_data.get('name', weapon)
                return True, f"A weapon materializes in your hands: {name}!"
            return True, "A weapon appears but you can't carry it... (inventory full)"

        elif effect == 'random_armor':
            armors = ['leather_armor', 'chainmail', 'scale_mail', 'iron_shield', 'shadow_cloak']
            armor = random.choice(armors)
            if player.can_add_item():
                player.add_item(armor)
                item_data = game_state.get_item_data(armor)
                name = item_data.get('name', armor)
                return True, f"Armor materializes before you: {name}!"
            return True, "Armor appears but you can't carry it... (inventory full)"

        elif effect == 'random':
            # Pick any random effect
            all_effects = ['heal', 'damage', 'buff_attack', 'buff_defense', 'gold', 'curse']
            return FountainSystem._apply_effect(game_state, random.choice(all_effects), fountain_name)

        return True, "The water has no effect..."

    @staticmethod
    def reset_fountains():
        """Reset all fountains (for new game)."""
        FountainSystem.used_fountains.clear()

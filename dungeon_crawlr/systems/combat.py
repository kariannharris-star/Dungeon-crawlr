"""Combat system - Handles turn-based combat."""
import random
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..engine.game import GameState
    from ..entities.player import Player
    from ..entities.enemy import Enemy


class CombatSystem:
    """Manages combat between player and enemies."""

    CRIT_CHANCE = 0.10
    CRIT_MULTIPLIER = 1.5
    FLEE_CHANCE = 0.50

    @staticmethod
    def calculate_player_damage(game_state: 'GameState') -> Tuple[int, bool]:
        """
        Calculate player's damage for an attack.
        Returns (damage, is_critical).
        """
        from .inventory import InventorySystem

        player = game_state.player
        weapon_damage = InventorySystem.get_weapon_damage(game_state)

        base_damage = player.attack + weapon_damage
        is_crit = random.random() < CombatSystem.CRIT_CHANCE

        if is_crit:
            base_damage = int(base_damage * CombatSystem.CRIT_MULTIPLIER)

        return base_damage, is_crit

    @staticmethod
    def calculate_enemy_damage(enemy: 'Enemy') -> int:
        """Calculate enemy's damage for an attack."""
        return enemy.attack

    @staticmethod
    def player_attack(game_state: 'GameState') -> Tuple[bool, str]:
        """
        Execute player's attack against current enemy.
        Returns (enemy_defeated, message).
        """
        if not game_state.in_combat or not game_state.current_enemy:
            return False, "You're not in combat."

        enemy = game_state.current_enemy
        damage, is_crit = CombatSystem.calculate_player_damage(game_state)
        actual_damage = enemy.take_damage(damage)

        crit_text = " CRITICAL HIT!" if is_crit else ""
        message = f"You attack the {enemy.name} for {actual_damage} damage!{crit_text}"

        if not enemy.is_alive():
            return True, message + f" The {enemy.name} has been defeated!"

        return False, message

    @staticmethod
    def enemy_attack(game_state: 'GameState') -> Tuple[bool, str]:
        """
        Execute enemy's attack against player.
        Returns (player_died, message).
        """
        from .inventory import InventorySystem

        if not game_state.in_combat or not game_state.current_enemy:
            return False, ""

        enemy = game_state.current_enemy
        player = game_state.player

        if not enemy.is_alive():
            return False, ""

        damage = CombatSystem.calculate_enemy_damage(enemy)
        armor_bonus = InventorySystem.get_armor_defense(game_state)
        actual_damage = max(1, damage - player.defense - armor_bonus)
        player.hp = max(0, player.hp - actual_damage)

        message = f"The {enemy.name} attacks you for {actual_damage} damage!"

        if not player.is_alive():
            return True, message + " You have been slain!"

        return False, message

    @staticmethod
    def attempt_flee(game_state: 'GameState') -> Tuple[bool, str]:
        """
        Attempt to flee from combat.
        Returns (success, message).
        """
        if not game_state.in_combat:
            return False, "You're not in combat."

        enemy = game_state.current_enemy

        if random.random() < CombatSystem.FLEE_CHANCE:
            game_state.end_combat()
            return True, "You successfully flee from combat!"
        else:
            # Enemy gets a free attack
            player_died, attack_msg = CombatSystem.enemy_attack(game_state)
            message = f"You failed to escape! {attack_msg}"
            return False, message

    @staticmethod
    def process_victory(game_state: 'GameState') -> str:
        """
        Process enemy defeat - award XP, gold, and drops.
        Returns message describing rewards.
        """
        if not game_state.current_enemy:
            return ""

        enemy = game_state.current_enemy
        player = game_state.player

        # Award XP
        leveled_up = player.gain_xp(enemy.xp_reward)

        # Award gold
        player.add_gold(enemy.gold_reward)

        # Check for drops
        drops = enemy.get_drops()
        drop_messages = []
        for item_id in drops:
            if player.can_add_item():
                player.add_item(item_id)
                item_data = game_state.get_item_data(item_id)
                drop_messages.append(item_data.get('name', item_id))

        # Build message
        message = f"You gained {enemy.xp_reward} XP and {enemy.gold_reward} gold."

        if leveled_up:
            message += f" LEVEL UP! You are now level {player.level}!"

        if drop_messages:
            message += f" The enemy dropped: {', '.join(drop_messages)}."

        # End combat
        game_state.end_combat()

        # Check for boss defeat / victory
        if enemy.id == 'dungeon_warlord':
            # Add warlord's amulet if not already there
            if 'warlord_amulet' not in player.inventory:
                if player.can_add_item():
                    player.add_item('warlord_amulet')
                    message += " You obtained the Warlord's Amulet!"

        return message

    @staticmethod
    def combat_round(game_state: 'GameState', action: str, args: list = None) -> Tuple[str, bool, bool]:
        """
        Execute a full combat round.
        Returns (message, combat_ended, player_died).
        """
        if args is None:
            args = []

        messages = []

        if action == 'attack':
            enemy_defeated, msg = CombatSystem.player_attack(game_state)
            messages.append(msg)

            if enemy_defeated:
                victory_msg = CombatSystem.process_victory(game_state)
                messages.append(victory_msg)
                return '\n'.join(messages), True, False

            # Enemy counterattack
            player_died, enemy_msg = CombatSystem.enemy_attack(game_state)
            messages.append(enemy_msg)

            if player_died:
                game_state.game_over = True
                return '\n'.join(messages), True, True

            return '\n'.join(messages), False, False

        elif action == 'flee':
            fled, msg = CombatSystem.attempt_flee(game_state)
            messages.append(msg)

            if fled:
                return '\n'.join(messages), True, False

            # Check if player died from counter attack
            if game_state.player and not game_state.player.is_alive():
                game_state.game_over = True
                return '\n'.join(messages), True, True

            return '\n'.join(messages), False, False

        elif action == 'use':
            from .inventory import InventorySystem
            if args:
                item_name = ' '.join(args)
                success, msg = InventorySystem.use_item(game_state, item_name)
                messages.append(msg)

                if success:
                    # Check if enemy was killed by item
                    if game_state.current_enemy and not game_state.current_enemy.is_alive():
                        victory_msg = CombatSystem.process_victory(game_state)
                        messages.append(victory_msg)
                        return '\n'.join(messages), True, False

                    # Enemy counterattack if still alive
                    if game_state.current_enemy and game_state.current_enemy.is_alive():
                        player_died, enemy_msg = CombatSystem.enemy_attack(game_state)
                        messages.append(enemy_msg)

                        if player_died:
                            game_state.game_over = True
                            return '\n'.join(messages), True, True

                return '\n'.join(messages), False, False
            else:
                return "Use what?", False, False

        else:
            return "Invalid combat action. Use: attack, use <item>, or flee", False, False

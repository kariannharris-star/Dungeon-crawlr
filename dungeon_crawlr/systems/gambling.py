"""Gambling system - Dice games in the tavern."""
import random
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..engine.game import GameState


class GamblingSystem:
    """Manages gambling mini-games."""

    @staticmethod
    def is_in_tavern(game_state: 'GameState') -> bool:
        """Check if player is in the tavern."""
        return game_state.current_room_id == "tavern"

    @staticmethod
    def roll_dice(num_dice: int = 2, sides: int = 6) -> list:
        """Roll dice and return results."""
        return [random.randint(1, sides) for _ in range(num_dice)]

    @staticmethod
    def play_high_low(game_state: 'GameState', bet: int, choice: str) -> Tuple[bool, str]:
        """
        Play high/low dice game.
        Bet on whether 2d6 will be high (8-12), low (2-6), or seven (exactly 7).
        Returns (won, message).
        """
        player = game_state.player

        if not player:
            return False, "Invalid game state."

        if bet <= 0:
            return False, "You need to bet at least 1 gold."

        if player.gold < bet:
            return False, f"You don't have enough gold. You have {player.gold}g."

        choice = choice.lower()
        if choice not in ['high', 'low', 'seven', '7']:
            return False, "Choose 'high' (8-12), 'low' (2-6), or 'seven' (exactly 7)."

        if choice == '7':
            choice = 'seven'

        # Roll the dice
        dice = GamblingSystem.roll_dice(2, 6)
        total = sum(dice)

        # Determine result
        if total <= 6:
            result = 'low'
        elif total >= 8:
            result = 'high'
        else:
            result = 'seven'

        # Build dramatic message
        dice_str = f"[{dice[0]}] [{dice[1]}]"

        won = False
        winnings = 0

        if choice == result:
            won = True
            if choice == 'seven':
                # Lucky 7 pays 4x
                winnings = bet * 4
                player.gold += winnings - bet  # They already bet, so add net winnings
                msg = f"\n  The dice tumble across the table...\n  {dice_str} = {total}\n\n  LUCKY SEVEN! The crowd erupts!\n  You win {winnings} gold! (+{winnings - bet} net)"
            else:
                # High/Low pays 2x
                winnings = bet * 2
                player.gold += winnings - bet
                msg = f"\n  The dice tumble across the table...\n  {dice_str} = {total}\n\n  {result.upper()}! You called it!\n  You win {winnings} gold! (+{winnings - bet} net)"
        else:
            player.gold -= bet
            msg = f"\n  The dice tumble across the table...\n  {dice_str} = {total}\n\n  {result.upper()}. You bet {choice}.\n  You lose {bet} gold. Better luck next time."

        return won, msg

    @staticmethod
    def play_skull_dice(game_state: 'GameState', bet: int) -> Tuple[bool, str]:
        """
        Play Skull Dice - roll 3d6, get three of a kind to win big.
        Pair pays 1.5x, three of a kind pays 5x, all 6s pays 10x.
        """
        player = game_state.player

        if not player:
            return False, "Invalid game state."

        if bet <= 0:
            return False, "You need to bet at least 1 gold."

        if player.gold < bet:
            return False, f"You don't have enough gold. You have {player.gold}g."

        # Roll three dice
        dice = GamblingSystem.roll_dice(3, 6)
        dice_sorted = sorted(dice)

        dice_str = f"[{dice[0]}] [{dice[1]}] [{dice[2]}]"

        # Check for matches
        if dice[0] == dice[1] == dice[2] == 6:
            # TRIPLE SKULLS (all 6s)
            winnings = bet * 10
            player.gold += winnings - bet
            msg = f"\n  The skull dice clatter ominously...\n  {dice_str}\n\n  TRIPLE SKULLS! The tavern goes silent in awe!\n  You win {winnings} gold! (+{winnings - bet} net)"
            return True, msg

        elif dice[0] == dice[1] == dice[2]:
            # Three of a kind
            winnings = bet * 5
            player.gold += winnings - bet
            msg = f"\n  The skull dice clatter ominously...\n  {dice_str}\n\n  THREE OF A KIND! Impressive!\n  You win {winnings} gold! (+{winnings - bet} net)"
            return True, msg

        elif dice_sorted[0] == dice_sorted[1] or dice_sorted[1] == dice_sorted[2]:
            # Pair - pays 1.5x (rounded down)
            winnings = int(bet * 1.5)
            player.gold += winnings - bet
            msg = f"\n  The skull dice clatter ominously...\n  {dice_str}\n\n  A pair! Not bad.\n  You win {winnings} gold! (+{winnings - bet} net)"
            return True, msg

        else:
            # Nothing
            player.gold -= bet
            msg = f"\n  The skull dice clatter ominously...\n  {dice_str}\n\n  Nothing. The bones weren't with you tonight.\n  You lose {bet} gold."
            return False, msg

    @staticmethod
    def play_death_or_glory(game_state: 'GameState', bet: int) -> Tuple[bool, str]:
        """
        Death or Glory - High risk, high reward.
        Roll 1d20. 1 = lose triple bet. 2-10 = lose bet. 11-19 = win bet. 20 = win triple bet.
        """
        player = game_state.player

        if not player:
            return False, "Invalid game state."

        if bet <= 0:
            return False, "You need to bet at least 1 gold."

        max_loss = bet * 3
        if player.gold < max_loss:
            return False, f"Death or Glory requires {max_loss}g available (3x your bet). You have {player.gold}g."

        # Roll d20
        roll = random.randint(1, 20)

        if roll == 1:
            # DEATH - lose triple
            loss = bet * 3
            player.gold -= loss
            msg = f"\n  You blow on the d20 for luck...\n  [{roll}]\n\n  DEATH! The dice gods are cruel!\n  You lose {loss} gold (3x your bet)!"
            return False, msg

        elif roll <= 10:
            # Lose bet
            player.gold -= bet
            msg = f"\n  You blow on the d20 for luck...\n  [{roll}]\n\n  Not enough. You needed 11+.\n  You lose {bet} gold."
            return False, msg

        elif roll < 20:
            # Win bet
            player.gold += bet
            msg = f"\n  You blow on the d20 for luck...\n  [{roll}]\n\n  Victory! The dice favor you!\n  You win {bet} gold!"
            return True, msg

        else:
            # GLORY - win triple
            winnings = bet * 3
            player.gold += winnings
            msg = f"\n  You blow on the d20 for luck...\n  [{roll}]\n\n  GLORY! A NATURAL 20! The tavern ERUPTS!\n  You win {winnings} gold (3x your bet)!"
            return True, msg

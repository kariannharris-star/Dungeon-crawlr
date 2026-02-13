"""Shop system - Handles buying and selling items."""
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..engine.game import GameState


class ShopSystem:
    """Manages shop interactions."""

    @staticmethod
    def is_in_shop(game_state: 'GameState') -> bool:
        """Check if player is currently in a shop."""
        room = game_state.current_room
        return room and room.to_dict().get('is_shop', False)

    @staticmethod
    def get_shop_inventory(game_state: 'GameState') -> list:
        """Get the current shop's inventory."""
        room = game_state.current_room
        if room:
            room_dict = room.to_dict()
            return room_dict.get('shop_inventory', [])
        return []

    @staticmethod
    def buy_item(game_state: 'GameState', item_name: str) -> Tuple[bool, str]:
        """
        Buy an item from the current shop.
        Returns (success, message).
        """
        player = game_state.player
        room = game_state.current_room

        if not player or not room:
            return False, "Invalid game state."

        room_dict = room.to_dict()
        if not room_dict.get('is_shop', False):
            return False, "There's no shop here."

        shop_inventory = room_dict.get('shop_inventory', [])

        # Find item by name
        item_id = None
        for i_id in shop_inventory:
            item_data = game_state.get_item_data(i_id)
            if item_name.lower() in item_data.get('name', i_id).lower():
                item_id = i_id
                break

        if not item_id:
            return False, f"The shop doesn't sell '{item_name}'."

        item_data = game_state.get_item_data(item_id)
        price = item_data.get('value', 10)
        name = item_data.get('name', item_id)

        if player.gold < price:
            return False, f"You can't afford {name}. It costs {price} gold and you have {player.gold}."

        if not player.can_add_item():
            return False, "Your inventory is full!"

        # Complete purchase
        player.gold -= price
        player.add_item(item_id)

        return True, f"You bought {name} for {price} gold."

    @staticmethod
    def sell_item(game_state: 'GameState', item_name: str) -> Tuple[bool, str]:
        """
        Sell an item to the current shop.
        Returns (success, message).
        """
        player = game_state.player
        room = game_state.current_room

        if not player or not room:
            return False, "Invalid game state."

        room_dict = room.to_dict()
        if not room_dict.get('is_shop', False):
            return False, "There's no shop here."

        # Find item by name in player inventory
        item_id = None
        for i_id in player.inventory:
            item_data = game_state.get_item_data(i_id)
            if item_name.lower() in item_data.get('name', i_id).lower():
                item_id = i_id
                break

        if not item_id:
            return False, f"You don't have '{item_name}' to sell."

        # Can't sell equipped items
        if item_id == player.equipped_weapon or item_id == player.equipped_armor:
            return False, "You can't sell equipped items. Unequip first."

        # Can't sell quest items
        item_data = game_state.get_item_data(item_id)
        if item_data.get('item_type') == 'quest':
            return False, "You can't sell quest items."

        name = item_data.get('name', item_id)
        sell_price = item_data.get('value', 0) // 2  # Sell for half value

        if sell_price <= 0:
            return False, f"{name} has no value to the shopkeeper."

        # Complete sale
        player.remove_item(item_id)
        player.gold += sell_price

        return True, f"You sold {name} for {sell_price} gold."

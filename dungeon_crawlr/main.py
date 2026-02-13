#!/usr/bin/env python3
"""
Dungeon Crawlr - A Text-Based Dungeon Adventure
Main entry point and game loop.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dungeon_crawlr.engine.game import GameState
from dungeon_crawlr.engine.parser import parse_command, get_item_name_from_args, validate_direction
from dungeon_crawlr.engine.display import Display
from dungeon_crawlr.systems.combat import CombatSystem
from dungeon_crawlr.systems.inventory import InventorySystem
from dungeon_crawlr.systems.chest import ChestSystem
from dungeon_crawlr.systems.save_load import SaveLoadSystem
from dungeon_crawlr.systems.shop import ShopSystem
from dungeon_crawlr.systems.fountain import FountainSystem


def get_data_path(filename: str) -> str:
    """Get the full path to a data file."""
    return os.path.join(os.path.dirname(__file__), 'data', filename)


def initialize_game() -> GameState:
    """Initialize a new GameState with loaded data."""
    game_state = GameState()

    # Load data files
    if not game_state.dungeon.load_from_file(get_data_path('rooms.json')):
        print("Error: Could not load rooms data.")
        sys.exit(1)

    if not game_state.load_items_data(get_data_path('items.json')):
        print("Error: Could not load items data.")
        sys.exit(1)

    if not game_state.load_enemies_data(get_data_path('enemies.json')):
        print("Error: Could not load enemies data.")
        sys.exit(1)

    return game_state


def main_menu() -> str:
    """Display main menu and get user choice."""
    Display.title_screen()

    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return choice
            print("Please enter 1, 2, or 3.")
        except (EOFError, KeyboardInterrupt):
            return '3'


def get_player_name() -> str:
    """Get player name from input."""
    print()
    while True:
        try:
            name = input("Enter your name, adventurer: ").strip()
            if name:
                return name
            print("Please enter a name.")
        except (EOFError, KeyboardInterrupt):
            return "Unknown Hero"


def handle_exploration_command(game_state: GameState, command: str, args: list) -> bool:
    """
    Handle a command during exploration.
    Returns True if game should continue, False if quitting.
    """
    if command == 'move':
        if not args:
            Display.show_error("Move where? Specify a direction (north, south, east, west, up, down).")
            return True

        direction = args[0]
        if not validate_direction(direction):
            Display.show_error(f"'{direction}' is not a valid direction.")
            return True

        success, message = game_state.try_move(direction)
        if message:
            if success:
                Display.show_success(message)
            else:
                Display.show_error(message)

        return True

    elif command == 'look':
        if args:
            # Look at specific target
            target = ' '.join(args)
            # Check if target is an item in the room
            room = game_state.current_room
            for item_id in room.items:
                item_data = game_state.get_item_data(item_id)
                if target.lower() in item_data.get('name', item_id).lower():
                    Display.show_info(item_data.get('description', 'Nothing special.'))
                    return True
            # Check if target is the current enemy
            enemy = game_state.get_room_enemy()
            if enemy and target.lower() in enemy.name.lower():
                Display.show_info(enemy.description)
                return True
            Display.show_error(f"You don't see '{target}' here.")
        else:
            # Re-render room
            room = game_state.current_room
            enemy = game_state.get_room_enemy()
            Display.render_room(room, game_state.items_data, enemy if enemy and enemy.is_alive() else None)
        return True

    elif command == 'take':
        if not args:
            Display.show_error("Take what? Try 'take <item>' or 'take all'.")
            return True
        item_name = get_item_name_from_args(args)
        if item_name == 'all':
            success, message = InventorySystem.take_all_items(game_state)
        else:
            success, message = InventorySystem.take_item(game_state, item_name)
        if success:
            Display.show_success(message)
        else:
            Display.show_error(message)
        return True

    elif command == 'drop':
        if not args:
            Display.show_error("Drop what?")
            return True
        item_name = get_item_name_from_args(args)
        success, message = InventorySystem.drop_item(game_state, item_name)
        if success:
            Display.show_success(message)
        else:
            Display.show_error(message)
        return True

    elif command == 'use':
        if not args:
            Display.show_error("Use what?")
            return True
        item_name = get_item_name_from_args(args)
        success, message = InventorySystem.use_item(game_state, item_name)
        if success:
            Display.show_success(message)
        else:
            Display.show_error(message)
        return True

    elif command == 'equip':
        if not args:
            Display.show_error("Equip what?")
            return True
        item_name = get_item_name_from_args(args)
        success, message = InventorySystem.equip_item(game_state, item_name)
        if success:
            Display.show_success(message)
        else:
            Display.show_error(message)
        return True

    elif command == 'open':
        if args and 'chest' in ' '.join(args).lower():
            success, message, items = ChestSystem.open_chest(game_state)
            if success:
                Display.show_success(message)
            else:
                if game_state.in_combat:
                    Display.show_warning(message)
                else:
                    Display.show_error(message)
        else:
            Display.show_error("Open what? Try 'open chest'.")
        return True

    elif command == 'inventory':
        Display.render_inventory(game_state.player, game_state.items_data)
        return True

    elif command == 'stats':
        Display.render_stats(game_state.player)
        return True

    elif command == 'map':
        discovered = {room_id for room_id, room in game_state.dungeon.rooms.items() if room.visited}
        Display.render_map(game_state.dungeon.rooms, game_state.current_room_id, discovered)
        return True

    elif command == 'save':
        success, message = SaveLoadSystem.save_game(game_state)
        if success:
            Display.show_success(message)
        else:
            Display.show_error(message)
        return True

    elif command == 'help':
        Display.show_help()
        return True

    elif command == 'quit':
        print()
        try:
            confirm = input("Are you sure you want to quit? (y/n): ").strip().lower()
            if confirm == 'y':
                return False
        except (EOFError, KeyboardInterrupt):
            return False
        return True

    elif command == 'buy':
        if not args:
            Display.show_error("Buy what?")
            return True
        if not ShopSystem.is_in_shop(game_state):
            Display.show_error("There's no shop here.")
            return True
        item_name = get_item_name_from_args(args)
        success, message = ShopSystem.buy_item(game_state, item_name)
        if success:
            Display.show_success(message)
        else:
            Display.show_error(message)
        return True

    elif command == 'sell':
        if not args:
            Display.show_error("Sell what?")
            return True
        if not ShopSystem.is_in_shop(game_state):
            Display.show_error("There's no shop here.")
            return True
        item_name = get_item_name_from_args(args)
        success, message = ShopSystem.sell_item(game_state, item_name)
        if success:
            Display.show_success(message)
        else:
            Display.show_error(message)
        return True

    elif command == 'shop':
        if ShopSystem.is_in_shop(game_state):
            shop_inv = ShopSystem.get_shop_inventory(game_state)
            Display.render_shop(shop_inv, game_state.items_data, game_state.player.gold)
        else:
            Display.show_error("There's no shop here.")
        return True

    elif command == 'drink':
        if FountainSystem.has_fountain(game_state):
            success, message = FountainSystem.drink_from_fountain(game_state)
            if success:
                Display.show_success(message)
            else:
                Display.show_warning(message)
        else:
            Display.show_error("There's no fountain here to drink from.")
        return True

    elif command == 'attack':
        enemy = game_state.get_room_enemy()
        if enemy and enemy.is_alive():
            game_state.in_combat = True
            game_state.current_enemy = enemy
            Display.show_warning(f"You engage the {enemy.name} in combat!")
        else:
            Display.show_error("There's nothing to attack here.")
        return True

    elif command == '':
        return True

    else:
        Display.show_error("I don't understand that command. Type 'help' for a list of commands.")
        return True


def handle_combat_command(game_state: GameState, command: str, args: list) -> bool:
    """
    Handle a command during combat.
    Returns True if game should continue, False if quitting.
    """
    if command in ['attack', 'flee', 'use']:
        message, combat_ended, player_died = CombatSystem.combat_round(game_state, command, args)

        for line in message.split('\n'):
            Display.show_combat_message(line)

        if player_died:
            game_state.game_over = True
            return True

        if combat_ended:
            # Check victory condition
            if game_state.player.has_item('warlord_amulet'):
                game_state.game_won = True

        return True

    elif command == 'inventory':
        Display.render_inventory(game_state.player, game_state.items_data)
        return True

    elif command == 'stats':
        Display.render_stats(game_state.player)
        return True

    elif command == 'help':
        Display.show_help()
        return True

    elif command == 'quit':
        print()
        try:
            confirm = input("Are you sure you want to quit? (y/n): ").strip().lower()
            if confirm == 'y':
                return False
        except (EOFError, KeyboardInterrupt):
            return False
        return True

    elif command == '':
        return True

    else:
        Display.show_error("In combat! Use: attack, use <item>, flee, inventory, stats")
        return True


def game_loop(game_state: GameState) -> None:
    """Main game loop."""
    Display.clear_screen()

    # Initial room display
    room = game_state.current_room
    enemy = game_state.get_room_enemy()
    Display.render_room(room, game_state.items_data, enemy if enemy and enemy.is_alive() else None)

    # Check for enemy in starting room
    if enemy and enemy.is_alive():
        game_state.in_combat = True
        game_state.current_enemy = enemy

    running = True
    while running:
        # Check game over conditions
        if game_state.is_over():
            Display.game_over_screen(game_state.player)
            break

        if game_state.is_won():
            Display.victory_screen(game_state.player)
            break

        # Show combat status if in combat
        if game_state.in_combat and game_state.current_enemy:
            Display.render_combat_status(game_state.player, game_state.current_enemy)

        # Get input
        try:
            prompt = "(combat) > " if game_state.in_combat else "> "
            raw_input = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        # Parse command
        command, args = parse_command(raw_input)

        # Handle command based on game state
        if game_state.in_combat:
            running = handle_combat_command(game_state, command, args)
        else:
            running = handle_exploration_command(game_state, command, args)

            # After exploration command, check if entering combat
            if game_state.in_combat and game_state.current_enemy:
                continue

            # Render room after movement or relevant actions
            if command in ['move', 'look'] and not args:
                pass  # Already handled
            elif command == 'move':
                room = game_state.current_room
                enemy = game_state.get_room_enemy()
                Display.render_room(room, game_state.items_data, enemy if enemy and enemy.is_alive() else None)

                # Start combat if enemy present
                if enemy and enemy.is_alive():
                    game_state.in_combat = True
                    game_state.current_enemy = enemy


def main():
    """Main entry point."""
    try:
        while True:
            choice = main_menu()

            if choice == '1':  # New Game
                game_state = initialize_game()
                player_name = get_player_name()
                game_state.initialize_new_game(player_name)
                Display.show_success(f"Welcome, {player_name}! Your adventure begins...")
                game_loop(game_state)

            elif choice == '2':  # Load Game
                game_state = initialize_game()
                if SaveLoadSystem.save_exists():
                    success, message = SaveLoadSystem.load_game(game_state)
                    if success:
                        Display.show_success(message)
                        game_loop(game_state)
                    else:
                        Display.show_error(message)
                        input("Press Enter to continue...")
                else:
                    Display.show_error("No save file found.")
                    input("Press Enter to continue...")

            elif choice == '3':  # Quit
                print("\nFarewell, adventurer!\n")
                break

    except KeyboardInterrupt:
        print("\n\nFarewell, adventurer!\n")


if __name__ == '__main__':
    main()

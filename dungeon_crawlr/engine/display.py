"""Display module - All print/formatting functions."""
import textwrap
import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.player import Player
    from ..entities.enemy import Enemy
    from ..world.room import Room


class Display:
    """Handles all game output and formatting."""

    WIDTH = 70
    BORDER_CHAR = "="
    USE_COLOR = True

    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'orange': '\033[38;5;208m',
        'purple': '\033[38;5;129m',
        'gold': '\033[38;5;220m',
    }

    @classmethod
    def clear_screen(cls) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @classmethod
    def color(cls, text: str, color_name: str) -> str:
        """Apply color to text if colors are enabled."""
        if cls.USE_COLOR and color_name in cls.COLORS:
            return f"{cls.COLORS[color_name]}{text}{cls.COLORS['reset']}"
        return text

    @classmethod
    def wrap_text(cls, text: str, width: Optional[int] = None) -> str:
        """Wrap text to specified width."""
        if width is None:
            width = cls.WIDTH - 4

        # Handle multi-paragraph text
        paragraphs = text.split('\n\n')
        wrapped = []
        for para in paragraphs:
            # Preserve single line breaks within paragraphs
            lines = para.split('\n')
            wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
            wrapped.append('\n'.join(wrapped_lines))
        return '\n\n'.join(wrapped)

    @classmethod
    def border(cls, char: Optional[str] = None) -> str:
        """Generate a border line."""
        if char is None:
            char = cls.BORDER_CHAR
        return char * cls.WIDTH

    @classmethod
    def centered(cls, text: str, width: Optional[int] = None) -> str:
        """Center text within the display width."""
        if width is None:
            width = cls.WIDTH
        return text.center(width)

    @classmethod
    def hp_bar(cls, current: int, maximum: int, width: int = 20) -> str:
        """Generate an HP bar visualization."""
        ratio = current / maximum if maximum > 0 else 0
        filled = int(width * ratio)
        empty = width - filled

        # Color based on health percentage
        if ratio > 0.6:
            bar_color = 'green'
        elif ratio > 0.3:
            bar_color = 'yellow'
        else:
            bar_color = 'red'

        bar = "[" + cls.color("@" * filled, bar_color) + cls.color("." * empty, 'dim') + "]"
        return f"{bar} {current}/{maximum} HP"

    @classmethod
    def render_room(cls, room: 'Room', items_data: dict, enemy: Optional['Enemy'] = None) -> None:
        """Render a room description with full formatting."""
        print()
        print(cls.color(cls.border(), 'cyan'))
        print(cls.color(cls.centered(room.name.upper()), 'bold'))
        print(cls.color(cls.border(), 'cyan'))
        print()

        # Room description
        description = room.get_description()
        print(cls.wrap_text(description))
        print()

        # Section divider
        print(cls.color("-" * cls.WIDTH, 'dim'))
        print()

        # Items in room
        if room.has_items():
            print(cls.color("  ITEMS ON THE GROUND:", 'gold'))
            for item_id in room.items:
                item_data = items_data.get(item_id, {})
                name = item_data.get('name', item_id)
                item_type = item_data.get('item_type', 'misc')
                # Show damage/defense for weapons/armor
                if item_type == 'weapon':
                    damage = item_data.get('damage', 0)
                    print(f"    - {cls.color(name, 'yellow')} (weapon, +{damage} damage)")
                elif item_type == 'armor':
                    defense = item_data.get('defense_bonus', 0)
                    print(f"    - {cls.color(name, 'yellow')} (armor, +{defense} defense)")
                elif item_type == 'consumable':
                    effect = item_data.get('effect_type', '')
                    value = item_data.get('effect_value', 0)
                    if effect == 'heal':
                        print(f"    - {cls.color(name, 'green')} (restores {value} HP)")
                    elif effect == 'damage':
                        print(f"    - {cls.color(name, 'magenta')} (deals {value} magic damage)")
                    else:
                        print(f"    - {cls.color(name, 'green')} ({effect})")
                else:
                    print(f"    - {cls.color(name, 'yellow')}")
            print()

        # Chest
        if room.has_chest():
            chest = room.chest
            if not chest.get('opened', False):
                state = chest.get('state', 'closed')
                if state == 'locked':
                    key = chest.get('key_required', 'a key')
                    print(cls.color(f"  CHEST: A locked chest sits here. It requires the {key}.", 'orange'))
                elif state == 'trapped':
                    print(cls.color("  CHEST: A chest sits here. Something seems off about it...", 'orange'))
                else:
                    print(cls.color("  CHEST: An unlocked chest awaits opening.", 'orange'))
                print()

        # Exits with clearer formatting
        if room.exits:
            print(cls.color("  EXITS:", 'cyan'))
            for direction, room_id in room.exits.items():
                locked = ""
                if room.is_exit_locked(direction):
                    key = room.get_required_key(direction)
                    locked = cls.color(f" [LOCKED - need {key}]", 'red')
                arrow = cls.color("->", 'dim')
                print(f"    {direction.upper():8} {arrow} {room_id.replace('_', ' ').title()}{locked}")
            print()

        # Enemy
        if enemy and enemy.is_alive():
            print(cls.color(cls.border("!"), 'red'))
            print(cls.color(f"  DANGER: A {enemy.name} blocks your path!", 'red'))
            print(cls.color(f"  {enemy.description}", 'dim'))
            print(cls.color(f"  HP: {enemy.hp}/{enemy.max_hp}  ATK: {enemy.attack}  DEF: {enemy.defense}", 'red'))
            print(cls.color(cls.border("!"), 'red'))
            print()

        # Available actions box
        cls.show_available_actions(room, enemy, items_data)

        print(cls.color(cls.border(), 'cyan'))

    @classmethod
    def show_available_actions(cls, room: 'Room', enemy: Optional['Enemy'], items_data: dict) -> None:
        """Show a clear list of available actions."""
        print(cls.color("  WHAT WOULD YOU LIKE TO DO?", 'bold'))
        print()

        room_dict = room.to_dict()
        is_shop = room_dict.get('is_shop', False)
        has_fountain = room_dict.get('has_fountain', False)

        if enemy and enemy.is_alive():
            print(f"    {cls.color('attack', 'red')}         - Fight the {enemy.name}")
            print(f"    {cls.color('flee', 'yellow')}           - Attempt to escape (50% chance)")
            print(f"    {cls.color('use <item>', 'green')}     - Use an item in combat")
        else:
            # Movement
            if room.exits:
                dirs = ', '.join(room.exits.keys())
                print(f"    {cls.color('move <dir>', 'cyan')}    - Move to another room ({dirs})")

            # Items
            if room.has_items():
                print(f"    {cls.color('take <item>', 'yellow')}   - Pick up an item from the ground")

            # Chest
            if room.has_chest() and not room.chest.get('opened', False):
                print(f"    {cls.color('open chest', 'orange')}    - Open the chest")

            # Shop commands
            if is_shop:
                print(f"    {cls.color('shop', 'gold')}          - View items for sale")
                print(f"    {cls.color('buy <item>', 'green')}    - Purchase an item")
                print(f"    {cls.color('sell <item>', 'yellow')}   - Sell an item")

            # Fountain
            if has_fountain:
                print(f"    {cls.color('drink', 'magenta')}         - Drink from the magical fountain")

            # Always available
            print(f"    {cls.color('look', 'white')}          - Examine the room again")
            print(f"    {cls.color('look <thing>', 'white')}  - Examine something specific")

        # Always available
        print()
        print(f"    {cls.color('inventory', 'magenta')}     - View your items and equipment")
        print(f"    {cls.color('stats', 'green')}         - View your character stats")
        print(f"    {cls.color('map', 'blue')}           - View the dungeon map")
        print(f"    {cls.color('help', 'dim')}          - Show all commands")
        print()

    @classmethod
    def render_combat_status(cls, player: 'Player', enemy: 'Enemy') -> None:
        """Render combat status display."""
        print()
        print(cls.color(cls.border("!"), 'red'))
        print(cls.color(cls.centered("=== COMBAT ==="), 'red'))
        print(cls.color(cls.border("!"), 'red'))
        print()
        print(f"  {cls.color('YOU:', 'green')} {player.name}")
        print(f"       {cls.hp_bar(player.hp, player.max_hp)}")
        print(f"       ATK: {player.attack}  DEF: {player.defense}")
        print()
        print(f"  {cls.color('ENEMY:', 'red')} {enemy.name}")
        print(f"       {cls.hp_bar(enemy.hp, enemy.max_hp)}")
        print(f"       ATK: {enemy.attack}  DEF: {enemy.defense}")
        print()
        print(cls.color("-" * cls.WIDTH, 'red'))
        print()
        print(f"  {cls.color('YOUR OPTIONS:', 'bold')}")
        print(f"    {cls.color('attack', 'red')}       - Strike with your weapon")
        print(f"    {cls.color('use <item>', 'green')}  - Use a potion or scroll")
        print(f"    {cls.color('flee', 'yellow')}         - Try to escape (50% chance, enemy attacks if fail)")
        print()
        print(cls.color(cls.border("!"), 'red'))

    @classmethod
    def render_inventory(cls, player: 'Player', items_data: dict) -> None:
        """Render player inventory."""
        print()
        print(cls.color(cls.border("-"), 'gold'))
        print(cls.color(cls.centered("=== INVENTORY ==="), 'gold'))
        print(cls.color(cls.border("-"), 'gold'))
        print()

        if not player.inventory:
            print("  Your inventory is empty.")
        else:
            print(cls.color("  CARRIED ITEMS:", 'bold'))
            print(cls.color("  (Use slot number: 'drop 1', 'use 2', 'equip 3')", 'dim'))
            print()
            for slot, item_id in enumerate(player.inventory, 1):
                item_data = items_data.get(item_id, {})
                name = item_data.get('name', item_id)
                item_type = item_data.get('item_type', 'misc')

                # Slot number
                slot_num = cls.color(f"[{slot}]", 'white')

                # Mark equipped items
                equipped = ""
                if item_id == player.equipped_weapon:
                    equipped = cls.color(" [EQUIPPED]", 'green')
                elif item_id == player.equipped_armor:
                    equipped = cls.color(" [EQUIPPED]", 'green')

                # Show stats
                if item_type == 'weapon':
                    damage = item_data.get('damage', 0)
                    print(f"    {slot_num} {cls.color(name, 'yellow')} (+{damage} damage){equipped}")
                elif item_type == 'armor':
                    defense = item_data.get('defense_bonus', 0)
                    print(f"    {slot_num} {cls.color(name, 'cyan')} (+{defense} defense){equipped}")
                elif item_type == 'consumable':
                    effect = item_data.get('effect_type', '')
                    value = item_data.get('effect_value', 0)
                    if effect == 'heal':
                        print(f"    {slot_num} {cls.color(name, 'green')} (restores {value} HP)")
                    elif effect == 'damage':
                        print(f"    {slot_num} {cls.color(name, 'magenta')} (deals {value} magic damage)")
                    else:
                        print(f"    {slot_num} {cls.color(name, 'green')}")
                else:
                    print(f"    {slot_num} {name}")

        print()
        print(cls.color("  EQUIPMENT:", 'bold'))

        # Weapon
        if player.equipped_weapon:
            wpn_data = items_data.get(player.equipped_weapon, {})
            wpn_name = wpn_data.get('name', 'Unknown')
            wpn_dmg = wpn_data.get('damage', 0)
            print(f"    Weapon: {cls.color(wpn_name, 'yellow')} (+{wpn_dmg} damage)")
        else:
            print(f"    Weapon: {cls.color('Bare Fists', 'dim')} (+0 damage)")

        # Armor
        if player.equipped_armor:
            arm_data = items_data.get(player.equipped_armor, {})
            arm_name = arm_data.get('name', 'Unknown')
            arm_def = arm_data.get('defense_bonus', 0)
            print(f"    Armor:  {cls.color(arm_name, 'cyan')} (+{arm_def} defense)")
        else:
            print(f"    Armor:  {cls.color('None', 'dim')} (+0 defense)")

        print()
        print(f"  {cls.color('Gold:', 'gold')} {player.gold}")
        print(f"  Inventory: {len(player.inventory)}/{player.max_inventory} slots")
        print()
        print(cls.color("  COMMANDS:", 'dim'))
        print(f"    {cls.color('equip <item>', 'yellow')}  - Equip a weapon or armor")
        print(f"    {cls.color('use <item>', 'green')}    - Use a consumable item")
        print(f"    {cls.color('drop <item>', 'red')}   - Drop an item")
        print(cls.color(cls.border("-"), 'gold'))

    @classmethod
    def render_stats(cls, player: 'Player') -> None:
        """Render player stats."""
        print()
        print(cls.color(cls.border("-"), 'green'))
        print(cls.color(cls.centered(f"=== {player.name.upper()}'S STATS ==="), 'green'))
        print(cls.color(cls.border("-"), 'green'))
        print()
        print(f"  Level:   {cls.color(str(player.level), 'bold')}")
        print(f"  HP:      {cls.hp_bar(player.hp, player.max_hp)}")
        print(f"  Attack:  {player.attack}")
        print(f"  Defense: {player.defense}")
        print()

        # XP bar
        xp_ratio = player.xp / player.xp_to_next if player.xp_to_next > 0 else 0
        xp_filled = int(20 * xp_ratio)
        xp_empty = 20 - xp_filled
        xp_bar = "[" + cls.color("=" * xp_filled, 'cyan') + cls.color("-" * xp_empty, 'dim') + "]"
        print(f"  XP:      {xp_bar} {player.xp}/{player.xp_to_next}")
        print()
        print(f"  {cls.color('Gold:', 'gold')} {player.gold}")
        print(cls.color(cls.border("-"), 'green'))

    @classmethod
    def render_map(cls, rooms: dict, current_room_id: str, discovered: set) -> None:
        """Render a visual ASCII map of the dungeon."""
        print()
        print(cls.color(cls.border("-"), 'blue'))
        print(cls.color(cls.centered("=== DUNGEON MAP ==="), 'blue'))
        print(cls.color(cls.border("-"), 'blue'))
        print()

        # Define map layout with coordinates
        map_layout = """
                          THORNWICK VILLAGE
                                 |
       [APOTHECARY]----[VILLAGE SQUARE]----[BLACKSMITH]
                                 |
                            [TAVERN]
                                 |
                        [DUNGEON ENTRANCE]
                                 |
                         [ENTRANCE HALL]
                                 |
                       [MOSSY ANTECHAMBER]
                         /      |       \\
          [ARMORY]------       |        [CORRIDOR]------[CRYSTAL]
              |                |           |     \\       FOUNTAIN
       [FLOODED]-----[BLOOD]   |      [HIDDEN]---[STARLIGHT]
        CELLAR      FOUNTAIN   |       ALCOVE      GROTTO
              |                |
          [CRYPT]              |
                               |
                    [THRONE ROOM APPROACH]
                      /        |        \\
             [GOLEM]          |        [TRAP CORRIDOR]
            CHAMBER           |
                              |
                     [WARLORD'S LAIR]
        """

        # Room ID to display name mapping
        room_names = {
            'village_square': 'VILLAGE SQUARE',
            'blacksmith_shop': 'BLACKSMITH',
            'apothecary': 'APOTHECARY',
            'tavern': 'TAVERN',
            'dungeon_entrance': 'DUNGEON ENTRANCE',
            'entrance_hall': 'ENTRANCE HALL',
            'mossy_antechamber': 'MOSSY ANTECHAMBER',
            'corridor_of_whispers': 'CORRIDOR',
            'armory_ruins': 'ARMORY',
            'flooded_cellar': 'FLOODED',
            'crypt_chamber': 'CRYPT',
            'throne_room_approach': 'THRONE ROOM APPROACH',
            'hidden_alcove': 'HIDDEN',
            'trap_corridor': 'TRAP CORRIDOR',
            'boss_lair': "WARLORD'S LAIR",
            'golem_chamber': 'GOLEM',
            'crystal_fountain': 'CRYSTAL',
            'blood_fountain': 'BLOOD',
            'starlight_fountain': 'STARLIGHT',
        }

        # Print simple map
        for line in map_layout.split('\n'):
            # Color the current room
            display_line = line
            for room_id, name in room_names.items():
                if name in display_line:
                    if room_id == current_room_id:
                        display_line = display_line.replace(f'[{name}]', cls.color(f'[*{name}*]', 'green'))
                    elif room_id in discovered:
                        display_line = display_line.replace(f'[{name}]', cls.color(f'[{name}]', 'cyan'))
                    else:
                        display_line = display_line.replace(f'[{name}]', cls.color(f'[???]', 'dim'))
            print(display_line)

        print()
        print(f"  {cls.color('[*NAME*]', 'green')} = Your location")
        print(f"  {cls.color('[NAME]', 'cyan')} = Discovered")
        print(f"  {cls.color('[???]', 'dim')} = Undiscovered")
        print()
        print(cls.color(cls.border("-"), 'blue'))

    @classmethod
    def render_shop(cls, shop_inventory: list, items_data: dict, player_gold: int) -> None:
        """Render shop interface."""
        print()
        print(cls.color(cls.border("$"), 'gold'))
        print(cls.color(cls.centered("=== SHOP ==="), 'gold'))
        print(cls.color(cls.border("$"), 'gold'))
        print()
        print(f"  Your Gold: {cls.color(str(player_gold), 'gold')}")
        print()
        print(cls.color("  FOR SALE:", 'bold'))

        for i, item_id in enumerate(shop_inventory, 1):
            item_data = items_data.get(item_id, {})
            name = item_data.get('name', item_id)
            price = item_data.get('value', 10)
            item_type = item_data.get('item_type', 'misc')

            # Can afford?
            affordable = player_gold >= price
            price_color = 'green' if affordable else 'red'

            if item_type == 'weapon':
                damage = item_data.get('damage', 0)
                print(f"    {i}. {name} - {cls.color(f'{price}g', price_color)} (+{damage} damage)")
            elif item_type == 'armor':
                defense = item_data.get('defense_bonus', 0)
                print(f"    {i}. {name} - {cls.color(f'{price}g', price_color)} (+{defense} defense)")
            elif item_type == 'consumable':
                effect = item_data.get('effect_type', '')
                value = item_data.get('effect_value', 0)
                if effect == 'heal':
                    print(f"    {i}. {name} - {cls.color(f'{price}g', price_color)} (heals {value} HP)")
                elif effect == 'damage':
                    print(f"    {i}. {name} - {cls.color(f'{price}g', price_color)} ({value} magic dmg)")
                else:
                    print(f"    {i}. {name} - {cls.color(f'{price}g', price_color)}")
            else:
                print(f"    {i}. {name} - {cls.color(f'{price}g', price_color)}")

        print()
        print(cls.color("  COMMANDS:", 'dim'))
        print(f"    {cls.color('buy <item>', 'green')}  - Purchase an item")
        print(f"    {cls.color('sell <item>', 'yellow')} - Sell an item from inventory")
        print(f"    {cls.color('leave', 'cyan')}        - Leave the shop")
        print()
        print(cls.color(cls.border("$"), 'gold'))

    @classmethod
    def show_message(cls, message: str, color: str = 'white') -> None:
        """Display a simple message."""
        print(cls.color(message, color))

    @classmethod
    def show_combat_message(cls, message: str) -> None:
        """Display a combat message."""
        print(cls.color(f"  >> {message}", 'red'))

    @classmethod
    def show_success(cls, message: str) -> None:
        """Display a success message."""
        print(cls.color(f"  >> {message}", 'green'))

    @classmethod
    def show_warning(cls, message: str) -> None:
        """Display a warning message."""
        print(cls.color(f"  >> {message}", 'yellow'))

    @classmethod
    def show_error(cls, message: str) -> None:
        """Display an error message."""
        print(cls.color(f"  >> {message}", 'red'))

    @classmethod
    def show_info(cls, message: str) -> None:
        """Display an info message."""
        print(cls.color(f"  {message}", 'cyan'))

    @classmethod
    def title_screen(cls) -> None:
        """Display the title screen."""
        cls.clear_screen()
        print()
        print(cls.color(cls.border(), 'cyan'))
        print()
        title = """
    ____                                      ______                    __
   / __ \\__  ______  ____ ____  ____  ____   / ____/________ __      __/ /____
  / / / / / / / __ \\/ __ `/ _ \\/ __ \\/ __ \\ / /   / ___/ __ `/ | /| / / / ___/
 / /_/ / /_/ / / / / /_/ /  __/ /_/ / / / // /___/ /  / /_/ /| |/ |/ / / /
/_____/\\__,_/_/ /_/\\__, /\\___/\\____/_/ /_/ \\____/_/   \\__,_/ |__/|__/_/_/
                  /____/
        """
        for line in title.split('\n'):
            print(cls.color(line, 'cyan'))
        print()
        print(cls.color(cls.centered("A Text-Based Dungeon Adventure"), 'dim'))
        print(cls.color(cls.centered("Explore, Fight, Survive"), 'dim'))
        print()
        print(cls.color(cls.border(), 'cyan'))
        print()
        print(cls.centered(cls.color("1.", 'bold') + " New Game"))
        print(cls.centered(cls.color("2.", 'bold') + " Load Game"))
        print(cls.centered(cls.color("3.", 'bold') + " Quit"))
        print()

    @classmethod
    def game_over_screen(cls, player: 'Player') -> None:
        """Display game over screen."""
        cls.clear_screen()
        print()
        print(cls.color(cls.border(), 'red'))
        print()
        print(cls.color(cls.centered("YOU HAVE DIED"), 'red'))
        print()
        print(cls.centered(f"{player.name} has fallen in the dungeon."))
        print(cls.centered("The darkness claims another soul..."))
        print()
        print(cls.centered(f"Level Reached: {player.level}"))
        print(cls.centered(f"Gold Collected: {player.gold}"))
        print()
        print(cls.color(cls.border(), 'red'))
        print()

    @classmethod
    def victory_screen(cls, player: 'Player') -> None:
        """Display victory screen."""
        cls.clear_screen()
        print()
        print(cls.color(cls.border(), 'gold'))
        print()
        print(cls.color(cls.centered("=== VICTORY ==="), 'gold'))
        print()
        print(cls.centered(f"{player.name} has defeated the Dungeon Warlord!"))
        print(cls.centered("The dungeon's evil is vanquished... for now."))
        print()
        print(cls.centered(f"Final Level: {player.level}"))
        print(cls.centered(f"Gold Collected: {player.gold}"))
        print()
        print(cls.color(cls.border(), 'gold'))
        print()

    @classmethod
    def show_help(cls) -> None:
        """Display help/commands screen."""
        print()
        print(cls.color(cls.border("-"), 'cyan'))
        print(cls.color(cls.centered("=== ALL COMMANDS ==="), 'cyan'))
        print(cls.color(cls.border("-"), 'cyan'))
        print()

        print(cls.color("  MOVEMENT:", 'bold'))
        print(f"    {cls.color('move <dir>', 'cyan'):20} Move north/south/east/west/up/down")
        print(f"    {cls.color('n / s / e / w', 'cyan'):20} Quick movement shortcuts")
        print()

        print(cls.color("  EXPLORATION:", 'bold'))
        print(f"    {cls.color('look', 'white'):20} Examine the current room")
        print(f"    {cls.color('look <target>', 'white'):20} Examine something specific")
        print(f"    {cls.color('map', 'blue'):20} View discovered locations")
        print()

        print(cls.color("  ITEMS:", 'bold'))
        print(f"    {cls.color('take <item>', 'yellow'):20} Pick up an item")
        print(f"    {cls.color('drop <item>', 'yellow'):20} Drop an item")
        print(f"    {cls.color('use <item>', 'green'):20} Use a consumable")
        print(f"    {cls.color('equip <item>', 'yellow'):20} Equip weapon/armor")
        print(f"    {cls.color('open chest', 'orange'):20} Open a chest")
        print()

        print(cls.color("  SHOPS:", 'bold'))
        print(f"    {cls.color('shop', 'gold'):20} View shop inventory")
        print(f"    {cls.color('buy <item>', 'green'):20} Buy an item")
        print(f"    {cls.color('sell <item>', 'yellow'):20} Sell an item")
        print()

        print(cls.color("  SPECIAL:", 'bold'))
        print(f"    {cls.color('drink', 'magenta'):20} Drink from a fountain")
        print()

        print(cls.color("  COMBAT:", 'bold'))
        print(f"    {cls.color('attack', 'red'):20} Attack an enemy")
        print(f"    {cls.color('flee', 'yellow'):20} Attempt to escape")
        print()

        print(cls.color("  INFORMATION:", 'bold'))
        print(f"    {cls.color('inventory / i', 'magenta'):20} View inventory")
        print(f"    {cls.color('stats', 'green'):20} View character stats")
        print()

        print(cls.color("  SYSTEM:", 'bold'))
        print(f"    {cls.color('save', 'dim'):20} Save your game")
        print(f"    {cls.color('load', 'dim'):20} Load a saved game")
        print(f"    {cls.color('help / ?', 'dim'):20} Show this help")
        print(f"    {cls.color('quit', 'dim'):20} Exit the game")
        print()
        print(cls.color(cls.border("-"), 'cyan'))

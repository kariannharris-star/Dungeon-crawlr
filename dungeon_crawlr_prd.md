# Product Requirements Document
# Dungeon Crawlr

**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-02-11  
**Language:** Python  

---

## Table of Contents

1. [Overview](#overview)
2. [Goals & Non-Goals](#goals--non-goals)
3. [User Experience](#user-experience)
4. [Game Architecture](#game-architecture)
5. [Core Systems](#core-systems)
6. [Content Requirements](#content-requirements)
7. [Technical Requirements](#technical-requirements)
8. [Data Structures](#data-structures)
9. [File Structure](#file-structure)
10. [Milestones](#milestones)

---

## 1. Overview

### 1.1 Product Summary

**Dungeon Crawlr** is a text-based dungeon exploration game written in Python, inspired by the Alexa skill *Dungeon Adventure*. Players navigate a procedurally described dungeon, discovering rooms with rich narrative descriptions, collecting items, opening chests, and battling enemies — all through a command-line interface.

### 1.2 Vision

Deliver a compelling, replayable dungeon crawler experience entirely in the terminal, with enough depth in its systems (combat, inventory, exploration) to reward multiple playthroughs without requiring graphics or a GUI.

### 1.3 Target Audience

- Fans of classic text-adventure and roguelike games
- Python developers and hobbyists who enjoy playable CLI projects
- Players who enjoyed the Alexa *Dungeon Adventure* skill and want a keyboard-driven equivalent

---

## 2. Goals & Non-Goals

### 2.1 Goals

- Provide a playable, complete dungeon-crawl experience from the terminal
- Include at minimum 10 unique room types with distinct descriptions
- Implement a real-time inventory, item pickup, and item use system
- Include at least 6 enemy types with varying stats and behaviors
- Include chests that can be locked, trapped, or contain random loot
- Support a simple save/load system using JSON
- Make the codebase clean, modular, and easy to extend

### 2.2 Non-Goals

- No graphical user interface (GUI) — CLI only for v1.0
- No multiplayer or networked play
- No procedural dungeon *generation* in v1.0 (hand-crafted maps only)
- No audio

---

## 3. User Experience

### 3.1 Game Flow

```
Start Game
    │
    ├── New Game ──► Choose Name ──► Enter Dungeon (Room 1)
    │
    └── Load Game ──► Resume from saved state
                           │
                    ┌──────▼──────────────────────────────────────┐
                    │              Main Game Loop                  │
                    │                                              │
                    │  Describe Room ──► Show Exits & Contents     │
                    │       │                                      │
                    │  Player Input                                │
                    │       │                                      │
                    │  ┌────┴──────────────────────┐              │
                    │  │ move / look / take / use   │              │
                    │  │ open / attack / inventory  │              │
                    │  │ save / quit / help         │              │
                    └──┴───────────────────────────┴──────────────┘
                                    │
                           Enemy Encountered?
                               │       │
                              Yes      No
                               │       │
                          Combat Loop  Continue Exploring
                               │
                         Win ──┴── Lose
                          │           │
                    Continue        Game Over Screen
```

### 3.2 Commands

| Command | Aliases | Description |
|---|---|---|
| `move <direction>` | `go`, `walk`, `n/s/e/w` | Move to an adjacent room |
| `look` | `l`, `examine` | Re-describe the current room |
| `look <target>` | `examine <target>` | Examine a specific object or enemy |
| `take <item>` | `pick up`, `grab` | Add an item to inventory |
| `drop <item>` | — | Remove an item from inventory |
| `use <item>` | — | Use a consumable item |
| `equip <item>` | — | Equip a weapon or armor |
| `open <chest>` | — | Attempt to open a chest |
| `attack` | `fight`, `a` | Initiate or continue combat |
| `flee` | `run`, `escape` | Attempt to flee combat |
| `inventory` | `inv`, `i` | Show current inventory |
| `stats` | `status` | Show player stats |
| `map` | — | Show a simple ASCII map of discovered rooms |
| `save` | — | Save the game to a JSON file |
| `load` | — | Load a saved game |
| `help` | `?` | Show command list |
| `quit` | `exit` | Quit the game |

### 3.3 Sample Room Description

```
═══════════════════════════════════════════════════════
  THE MOSSY ANTECHAMBER
═══════════════════════════════════════════════════════
  Damp stone walls close in around you. Torchlight flickers
  across patches of dark green moss. The smell of rot and
  old iron fills the air.

  You see: a wooden chest (closed), a rusted sword
  Exits:   [NORTH] Corridor of Whispers  |  [EAST] Dead End

  ⚠  A goblin scout watches you from the shadows.
═══════════════════════════════════════════════════════
```

---

## 4. Game Architecture

### 4.1 Module Overview

```
dungeon_crawlr/
├── main.py              # Entry point, main game loop
├── engine/
│   ├── game.py          # Game state manager
│   ├── parser.py        # Command parser / input handler
│   └── display.py       # All print/formatting functions
├── world/
│   ├── dungeon.py       # Dungeon map, room graph
│   ├── room.py          # Room class
│   └── rooms_data.py    # Hand-crafted room definitions (dict/JSON)
├── entities/
│   ├── player.py        # Player class
│   ├── enemy.py         # Enemy base class + subclasses
│   └── npc.py           # Non-combat NPCs (optional v1.1)
├── items/
│   ├── item.py          # Base Item class
│   ├── weapon.py        # Weapon subclass
│   ├── armor.py         # Armor subclass
│   ├── consumable.py    # Potions, food, scrolls
│   └── items_data.py    # All item definitions
├── systems/
│   ├── combat.py        # Combat loop logic
│   ├── inventory.py     # Inventory management
│   ├── chest.py         # Chest interaction logic
│   └── save_load.py     # JSON save/load system
└── data/
    ├── rooms.json        # Room definitions
    ├── items.json        # Item definitions
    └── enemies.json      # Enemy definitions
```

### 4.2 Core Loop (Pseudocode)

```python
def main_loop(game_state):
    while game_state.player.is_alive():
        current_room = game_state.current_room
        display.render_room(current_room, game_state)

        if current_room.has_enemy() and not current_room.enemy.is_defeated():
            combat.initiate(game_state)
            continue

        raw_input = input("> ").strip().lower()
        action, args = parser.parse(raw_input)
        game_state = engine.execute(action, args, game_state)

        if game_state.is_won():
            display.victory_screen()
            break

    if not game_state.player.is_alive():
        display.game_over_screen(game_state)
```

---

## 5. Core Systems

### 5.1 Room System

Each room is a node in a directed graph. Rooms have:

- **ID** — unique string key (e.g., `"mossy_antechamber"`)
- **Name** — short display title
- **Description** — 2–4 sentence atmospheric text (shown on first visit or `look`)
- **Short description** — 1 sentence (shown on revisit)
- **Exits** — dict of `{direction: room_id}` (directions: `north`, `south`, `east`, `west`, `up`, `down`)
- **Items** — list of item IDs present in the room (mutable)
- **Enemy** — optional single enemy instance
- **Chest** — optional chest instance
- **Visited flag** — boolean, controls description length

Locked exits are supported: an exit can require a key item to pass.

### 5.2 Player System

The player has the following stats:

| Stat | Description | Default |
|---|---|---|
| `name` | Player-chosen name | — |
| `hp` | Current health points | 100 |
| `max_hp` | Maximum health points | 100 |
| `attack` | Base attack damage | 10 |
| `defense` | Damage reduction | 2 |
| `level` | Player level | 1 |
| `xp` | Experience points | 0 |
| `xp_to_next` | XP needed for next level | 50 |
| `gold` | Currency | 0 |
| `inventory` | List of Item objects | [] |
| `equipped_weapon` | Currently equipped weapon | bare hands |
| `equipped_armor` | Currently equipped armor | None |
| `max_inventory` | Inventory slot limit | 10 |

**Leveling:** Every level grants +10 max HP, +2 attack, +1 defense. XP requirement increases by 50% per level.

### 5.3 Combat System

Combat is turn-based. Each round:

1. Player chooses `attack`, `use <item>`, or `flee`
2. Player damage = `(player.attack + weapon.damage) - enemy.defense` (minimum 1)
3. Enemy attacks if alive — enemy damage = `enemy.attack - player.defense` (minimum 1)
4. Critical hits (10% chance) deal 1.5× damage
5. Enemy is defeated → award XP and gold, possibly drop items
6. Player HP ≤ 0 → game over
7. `flee` has a 50% success rate; on failure, enemy gets a free attack

### 5.4 Inventory System

- Players carry up to 10 items (stackable consumables count as 1 slot per stack)
- `take <item>` — pick up an item from the current room
- `drop <item>` — place item back in the current room
- `use <item>` — triggers the item's effect (heal, buff, unlock, etc.)
- `equip <item>` — sets weapon or armor slot; previous item goes back to inventory
- Items have `weight` (future use) and `value` (gold value if sold)

### 5.5 Chest System

Chests have four states:

| State | Behavior |
|---|---|
| **Unlocked** | Opens immediately on `open chest` |
| **Locked** | Requires the correct key item in inventory |
| **Trapped** | Opens but triggers a damage/debuff effect first |
| **Mimic** | Initiates combat instead of opening |

Chest loot is defined per-chest in the room data, with optional random loot rolls from a loot table tier (`common`, `uncommon`, `rare`).

### 5.6 Save / Load System

Game state is serialized to JSON and saved to `save_game.json` in the working directory.

Saved data includes: player stats, inventory (item IDs + quantities), current room ID, all room visited flags, defeated enemies, opened chests, and collected items.

---

## 6. Content Requirements

### 6.1 Rooms (Minimum 10)

| Room ID | Name | Notable Feature |
|---|---|---|
| `entrance_hall` | Entrance Hall | Starting room, locked north door |
| `mossy_antechamber` | Mossy Antechamber | Goblin scout enemy, wooden chest |
| `corridor_of_whispers` | Corridor of Whispers | Flavor text triggers, no enemy |
| `armory_ruins` | Ruined Armory` | Weapon item spawns, skeleton enemy |
| `flooded_cellar` | Flooded Cellar | Slows movement, rare chest |
| `crypt_chamber` | Crypt Chamber | Two skeleton enemies, locked chest |
| `throne_room_approach` | Throne Room Approach | Boss gate, requires crypt key |
| `hidden_alcove` | Hidden Alcove | Secret room via `look wall`, potion cache |
| `trap_corridor` | Trap Corridor | Floor trap deals damage on entry |
| `boss_lair` | The Warlord's Lair` | Boss enemy, final room, victory trigger |

### 6.2 Enemies (Minimum 6)

| Enemy | HP | Attack | Defense | XP | Gold | Drop |
|---|---|---|---|---|---|---|
| Goblin Scout | 20 | 5 | 1 | 15 | 5 | Short Sword (20%) |
| Skeleton Warrior | 35 | 8 | 3 | 25 | 10 | Bone Shield (15%) |
| Giant Rat | 15 | 4 | 0 | 10 | 2 | Rat Tail (50%) |
| Dark Mage | 25 | 12 | 1 | 35 | 15 | Spell Scroll (30%) |
| Stone Golem | 80 | 14 | 8 | 60 | 20 | Stone Fragment (40%) |
| Dungeon Warlord *(boss)* | 150 | 20 | 10 | 200 | 100 | Warlord's Amulet (100%) |

### 6.3 Items (Minimum 12)

| Item | Type | Effect |
|---|---|---|
| Health Potion | Consumable | Restore 30 HP |
| Greater Health Potion | Consumable | Restore 75 HP |
| Short Sword | Weapon | +5 attack |
| Iron Sword | Weapon | +10 attack |
| Warlord's Blade | Weapon | +20 attack, boss drop |
| Leather Armor | Armor | +3 defense |
| Iron Shield | Armor | +5 defense |
| Crypt Key | Key | Unlocks Crypt Chamber door |
| Torch | Utility | Reveals hidden room description |
| Antidote | Consumable | Cures poison status |
| Spell Scroll | Consumable | Deals 25 magic damage to enemy |
| Warlord's Amulet | Quest Item | Required to trigger victory |
| Gold Coin (stack) | Currency | Adds to gold counter |

### 6.4 Chest Loot Tables

| Tier | Items Pool |
|---|---|
| Common | Health Potion, Gold (5–15), Short Sword |
| Uncommon | Greater Health Potion, Leather Armor, Spell Scroll, Gold (15–30) |
| Rare | Iron Sword, Iron Shield, Gold (30–60), Antidote ×2 |

---

## 7. Technical Requirements

### 7.1 Python Version

Python **3.10+** is required. No third-party packages for the base game — standard library only (`json`, `os`, `sys`, `random`, `textwrap`, `copy`).

### 7.2 Input Handling

The command parser must:
- Be case-insensitive
- Support aliases (e.g., `n` = `go north` = `move north`)
- Provide a helpful "I don't understand that." message for unknown commands
- Never crash on empty input or special characters

### 7.3 Display

- All output uses `print()` with `textwrap.fill()` for word-wrapping at 60 characters
- Room headers use a decorative ASCII border
- Player HP shown as a bar: `[██████░░░░] 60/100 HP`
- Color is optional (via ANSI escape codes, toggled by a config flag)

### 7.4 Performance

- All room transitions must complete in < 100ms
- Save/load must complete in < 500ms
- No blocking I/O other than `input()`

### 7.5 Error Handling

- All file I/O (save/load) wrapped in try/except with user-friendly error messages
- Invalid save files must not crash the game — display error and return to main menu
- All enemy and item lookups use `.get()` with safe defaults

---

## 8. Data Structures

### 8.1 Room (Python dataclass)

```python
@dataclass
class Room:
    id: str
    name: str
    description: str
    short_description: str
    exits: dict[str, str]           # {"north": "room_id", ...}
    items: list[str]                # item IDs present
    enemy_id: str | None            # enemy ID or None
    chest: dict | None              # chest data or None
    visited: bool = False
    locked_exits: dict[str, str]    # {"north": "crypt_key"}
```

### 8.2 Player (Python dataclass)

```python
@dataclass
class Player:
    name: str
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 2
    level: int = 1
    xp: int = 0
    xp_to_next: int = 50
    gold: int = 0
    inventory: list = field(default_factory=list)
    equipped_weapon: str | None = None
    equipped_armor: str | None = None
```

### 8.3 Enemy (Python dataclass)

```python
@dataclass
class Enemy:
    id: str
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    xp_reward: int
    gold_reward: int
    drop_table: list[dict]          # [{"item_id": "short_sword", "chance": 0.2}]
    description: str
    defeated: bool = False
```

### 8.4 Chest (dict schema)

```json
{
  "id": "chest_crypt_01",
  "state": "locked",
  "key_required": "crypt_key",
  "trap_damage": 0,
  "loot_tier": "rare",
  "fixed_loot": ["iron_sword"],
  "opened": false
}
```

### 8.5 Save File Schema

```json
{
  "version": "1.0",
  "player": { "...player fields..." },
  "current_room": "mossy_antechamber",
  "room_states": {
    "entrance_hall": { "visited": true, "items": [], "chest_opened": false, "enemy_defeated": false }
  }
}
```

---

## 9. File Structure

```
dungeon_crawlr/
├── README.md
├── main.py
├── requirements.txt          # empty for v1.0 (stdlib only)
├── engine/
│   ├── __init__.py
│   ├── game.py
│   ├── parser.py
│   └── display.py
├── world/
│   ├── __init__.py
│   ├── dungeon.py
│   └── room.py
├── entities/
│   ├── __init__.py
│   ├── player.py
│   └── enemy.py
├── items/
│   ├── __init__.py
│   ├── item.py
│   ├── weapon.py
│   ├── armor.py
│   └── consumable.py
├── systems/
│   ├── __init__.py
│   ├── combat.py
│   ├── inventory.py
│   ├── chest.py
│   └── save_load.py
├── data/
│   ├── rooms.json
│   ├── items.json
│   └── enemies.json
└── tests/
    ├── test_combat.py
    ├── test_inventory.py
    ├── test_parser.py
    └── test_save_load.py
```

---

## 10. Milestones

| Milestone | Deliverables | Target |
|---|---|---|
| **M1 — Foundation** | Project structure, Room/Player/Item dataclasses, CLI display, basic movement between 3 rooms | Week 1 |
| **M2 — World** | All 10 rooms with descriptions and exits, ASCII map, room revisit logic, JSON data loading | Week 2 |
| **M3 — Items & Inventory** | Full inventory system, item pickup/drop/use/equip, chest system (all 4 states), loot tables | Week 3 |
| **M4 — Combat** | All 6 enemies, full combat loop, XP/leveling, flee mechanic, item drops | Week 4 |
| **M5 — Save/Load & Polish** | Save/load (JSON), main menu, help system, win/lose screens, ANSI color (optional) | Week 5 |
| **M6 — Testing & Release** | Unit tests for all systems, bug fixes, README, playtest pass | Week 6 |

---

## Appendix A — Design Principles

**Atmosphere first.** Every room description should evoke dread, wonder, or tension. Resist the urge to be purely functional.

**Fair, not easy.** Players should be able to lose, but never feel cheated. Sufficient healing items should always be obtainable before the boss.

**Extensible by design.** New rooms, items, and enemies should only require adding entries to the JSON data files — no code changes needed for content additions.

**Respect the player's time.** Revisited rooms use short descriptions. All output is concise. No padding.

---

*End of Document — Dungeon Crawlr PRD v1.0*

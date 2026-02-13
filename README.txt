==============================================================================
                         DUNGEON CRAWLR
                  A Text-Based Dungeon Adventure
==============================================================================

HOW TO PLAY
-----------

OPTION 1: Double-click the executable (EASIEST)
    Just double-click: dist/DungeonCrawlr.exe

    You can copy this .exe file anywhere and it will work!

OPTION 2: Double-click the batch file (requires Python)
    Double-click: play.bat

OPTION 3: Run from command line (requires Python)
    Open a terminal in this folder and type:
        python run_game.py

OPTION 4: Chromebook (requires Python)
    1. Copy the entire "Dungeon crawler" folder to your Chromebook
    2. Open the Linux terminal (Settings > Advanced > Developers > Linux)
    3. Navigate to the folder and run:
        chmod +x play_chromebook.sh
        ./play_chromebook.sh

    Or just run directly:
        python3 run_game.py


REQUIREMENTS
------------
- For the .exe: Nothing! It's standalone.
- For Python version: Python 3.10 or higher


GAME COMMANDS
-------------
Movement:       move north/south/east/west  (or just n/s/e/w)
Look around:    look
Pick up items:  take <item>  (or 'take all' to grab everything)
Use items:      use <item>
Equip gear:     equip <item>
Open chests:    open chest
Attack enemies: attack
Run away:       flee
View inventory: inventory (or i)
View stats:     stats
View map:       map
Shop commands:  shop, buy <item>, sell <item>
Drink fountain: drink
Save game:      save
Load game:      load
Help:           help
Quit:           quit


TIPS
----
- Start in the village - buy gear before entering the dungeon!
- The Blacksmith sells weapons and armor
- The Apothecary sells potions and magic scrolls
- Mystery fountains can help or hurt - drink at your own risk!
- Save often!
- Explore everywhere for the best loot
- The Warlord awaits in the depths...


REBUILDING THE EXECUTABLE
-------------------------
If you modify the game and want to rebuild the .exe:
    python build_exe.py


==============================================================================
                         Good luck, adventurer!
==============================================================================

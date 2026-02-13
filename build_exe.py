"""
Build script to create Dungeon Crawlr executable.
Run: python build_exe.py
"""
import os
import subprocess
import sys

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("Building Dungeon Crawlr executable...")
    print("This may take a few minutes...")
    print()

    # PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Single executable
        '--console',                    # Console application (needed for text game)
        '--name', 'DungeonCrawlr',      # Name of the executable
        '--add-data', 'dungeon_crawlr/data;dungeon_crawlr/data',  # Include data files
        '--clean',                      # Clean cache
        'run_game.py'                   # Entry point
    ]

    try:
        subprocess.run(cmd, check=True)
        print()
        print("=" * 50)
        print("BUILD SUCCESSFUL!")
        print("=" * 50)
        print()
        print("Your executable is located at:")
        print(f"  {os.path.join(script_dir, 'dist', 'DungeonCrawlr.exe')}")
        print()
        print("You can move DungeonCrawlr.exe anywhere and run it!")
        print()
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return 1
    except FileNotFoundError:
        print("PyInstaller not found. Install it with:")
        print("  python -m pip install pyinstaller")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())

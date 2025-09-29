import importlib
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class BotConfig(BaseModel):
    name: str
    description: str
    author: str = "Anonymous"
    version: str = "1.0.0"
    enabled: bool = True

class BotManager:
    def __init__(self):
        self.bots_dir = Path("bots")
        self.bots_dir.mkdir(exist_ok=True)
        self.bots: Dict[str, Any] = {}
        self.load_bots()

    def load_bots(self):
        """Load all bots from the bots directory"""
        self.bots = {}
        # Ensure 'bots' is importable by adding project root to sys.path
        project_root = Path(__file__).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        for init_file in self.bots_dir.glob("*/__init__.py"):
            bot_name = init_file.parent.name
            try:
                module = importlib.import_module(f"bots.{bot_name}")
                if hasattr(module, "Bot"):
                    self.bots[bot_name] = module.Bot()
            except Exception as e:
                print(f"Error loading bot {bot_name}: {e}")

    def list_bots(self) -> List[Dict[str, Any]]:
        """List all available bots with their metadata"""
        return [
            {
                "name": name,
                "description": getattr(bot, "description", "No description"),
                "author": getattr(bot, "author", "Unknown"),
                "version": getattr(bot, "version", "1.0.0"),
                "commands": [m for m in dir(bot) if not m.startswith('_') and callable(getattr(bot, m))]
            }
            for name, bot in self.bots.items()
        ]

    def run_bot(self, bot_name: str, *args, **kwargs):
        """Run a specific bot"""
        if bot_name not in self.bots:
            raise ValueError(f"Bot '{bot_name}' not found")
        return self.bots[bot_name].run(*args, **kwargs)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Scraping and RPA Station")
    subparsers = parser.add_subparsers(dest="command")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all available bots")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a specific bot")
    run_parser.add_argument("bot_name", help="Name of the bot to run")
    run_parser.add_argument("--params", nargs="*", help="Parameters for the bot")
    
    args = parser.parse_args()
    
    manager = BotManager()
    
    if args.command == "list":
        bots = manager.list_bots()
        print("\nAvailable Bots:" + "="*50)
        for bot in bots:
            print(f"\nName: {bot['name']}")
            print(f"Description: {bot['description']}")
            print(f"Author: {bot['author']}")
            print(f"Version: {bot['version']}")
            commands = ", ".join(bot['commands']) if bot['commands'] else "No commands defined"
            print(f"Available commands: {commands}")
            print("-"*60)
    
    elif args.command == "run":
        try:
            print(f"Running bot: {args.bot_name}")
            raw_params = args.params or []
            coerced_params = []
            for p in raw_params:
                # Try int
                try:
                    coerced_params.append(int(p))
                    continue
                except ValueError:
                    pass
                # Leave as string fallback
                coerced_params.append(p)
            result = manager.run_bot(args.bot_name, *coerced_params)
            print(f"Bot completed. Result: {result}")
        except Exception as e:
            print(f"Error running bot: {e}")
    else:
        parser.print_help()

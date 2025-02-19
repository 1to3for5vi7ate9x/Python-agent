import os
import json
from typing import Dict, List, Optional
from loguru import logger

class CharacterManager:
    def __init__(self, templates_dir: str = "characters/templates", prompt_file: str = None):
        self.templates_dir = templates_dir
        self.characters: Dict[str, Dict] = {}
        self._load_characters(prompt_file=prompt_file)

    def _load_characters(self, prompt_file: str = None) -> None:
        """Load all character templates from the templates directory or environment variables.
        prompt_file argument overrides environment variable.
        """
        # Load character from environment variables if CHARACTER_NAME is set
        try:
            # prompt_file must be provided
            # prompt_file must be provided
            if not prompt_file:
                logger.error("prompt_file must be provided")
                return

            username = os.environ.get("CHARACTER_USERNAME")
            clients_str = os.environ.get("CHARACTER_CLIENTS")
            if not clients_str:
                logger.error("Missing information for character configuration. Need clients")
                return
            clients = clients_str.split(',')

            character = {
                "name": prompt_file,  # Use prompt_file as a unique identifier
                "username": username,  # Keep username from environment if available
                "clients": clients,
                "prompt_file": prompt_file
            }
            self.characters[prompt_file] = character  # Use prompt_file as key
            logger.info(f"Loaded character from prompt file: {prompt_file}")

        except Exception as e:
            logger.error(f"Error loading character: {e}")
            return

    def get_character_names(self) -> List[str]:
        """Get list of available character names"""
        return list(self.characters.keys())
    
    def get_character(self, name: str) -> Optional[Dict]:
        """Get character configuration by name"""
        return self.characters.get(name)
    
    def print_available_characters(self) -> None:
        """Print available characters in a formatted way"""
        print("\nAvailable Characters:")
        print("-" * 50)
        for name in self.get_character_names():
            character = self.characters[name]
            print(f"Name: {name}")
            print(f"Role: {character.get('username', 'N/A')}")
            print("-" * 50)
    
    def select_character(self) -> Optional[Dict]:
        """Interactive character selection"""
        self.print_available_characters()
        
        while True:
            try:
                names = self.get_character_names()
                if not names:
                    logger.error("No characters available")
                    return None
                    
                print("\nSelect a character by number:")
                for i, name in enumerate(names, 1):
                    print(f"{i}. {name}")
                
                choice = input("\nEnter number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    return None
                    
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(names):
                        selected_name = names[index]
                        return self.get_character(selected_name)  # Return the entire character dictionary
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
                    
            except KeyboardInterrupt:
                print("\nCharacter selection cancelled.")
                return None

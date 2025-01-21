"""
Advanced template usage example for Promptix library.

This example demonstrates advanced templating features:
1. Conditional blocks (if/else/elif)
2. Loops and list handling (for loops)
3. Nested conditional logic
4. Numeric comparisons
5. Dynamic content generation
6. Custom data structures
"""

from typing import Any, Dict, List, Optional

from promptix import Promptix


def generate_rpg_scenario(
    game_style: str,
    party_level: int,
    party_classes: List[str],
    environment: str,
    quest_type: str,
    difficulty: str,
    magical_elements: Optional[List[str]] = None,
    environment_details: Optional[Dict[str, Any]] = None,
    special_conditions: Optional[List[str]] = None,
) -> str:
    """
    Generate a dynamic RPG scenario using advanced template features.
    """
    env_details = environment_details or {}

    context = {
        "game_style": game_style,
        "party_level": party_level,
        "party_classes": party_classes,
        "environment": environment,
        "quest_type": quest_type,
        "difficulty": difficulty,
        "magical_elements": magical_elements,
        # environment-specific flags
        "has_traps": env_details.get("has_traps", False),
        "has_crime": env_details.get("has_crime", False),
        "has_monsters": env_details.get("has_monsters", False),
        # environment details
        "city_type": env_details.get("city_type", "medieval"),
        "atmosphere": env_details.get("atmosphere", "mysterious"),
        "terrain_type": env_details.get("terrain_type", "forest"),
        # special conditions in custom data
        "custom_data": {"special_conditions": special_conditions} if special_conditions else {},
    }

    return Promptix.get_prompt(prompt_template="DungeonMaster", **context)

def main():
    print("Advanced Template Usage Examples\n")

    # Example 1: Beginner dungeon crawl
    print("\nExample 1: Beginner Dungeon Crawl")
    print("-" * 50)
    prompt1 = generate_rpg_scenario(
        game_style="heroic",
        party_level=3,
        party_classes=["Warrior", "Cleric", "Rogue"],
        environment="dungeon",
        quest_type="combat",
        difficulty="easy",
        environment_details={"has_traps": True},
        magical_elements=["Ancient Runes", "Magical Barriers"],
    )
    print(prompt1)

    # Example 2: Complex city intrigue
    print("\nExample 2: Complex City Intrigue")
    print("-" * 50)
    prompt2 = generate_rpg_scenario(
        game_style="mystery",
        party_level=8,
        party_classes=["Bard", "Rogue", "Wizard", "Paladin"],
        environment="city",
        quest_type="diplomacy",
        difficulty="hard",
        environment_details={
            "has_crime": True,
            "city_type": "merchant",
            "atmosphere": "tense",
        },
        magical_elements=["Dark Magic", "Illusion Magic", "Forbidden Arts"],
        special_conditions=[
            "Political uprising imminent",
            "Hidden cult influence",
            "Corrupt city guard",
        ],
    )
    print(prompt2)

    # Example 3: Epic wilderness adventure
    print("\nExample 3: Epic Wilderness Adventure")
    print("-" * 50)
    prompt3 = generate_rpg_scenario(
        game_style="epic",
        party_level=15,
        party_classes=["Druid", "Ranger", "Barbarian", "Shaman"],
        environment="wilderness",
        quest_type="mystery",
        difficulty="medium",
        environment_details={"has_monsters": True, "terrain_type": "mountain"},
        magical_elements=["Ancient Ley Lines", "Natural Magic", "Elemental Powers"],
    )
    print(prompt3)

    # Example 4: Minimal configuration
    print("\nExample 4: Minimal Required Configuration")
    print("-" * 50)
    prompt4 = generate_rpg_scenario(
        game_style="gritty",
        party_level=1,
        party_classes=["Fighter"],
        environment="city",
        quest_type="combat",
        difficulty="medium",
        magical_elements=["Street Magic", "Common Spells"]
    )
    print(prompt4)


if __name__ == "__main__":
    main()

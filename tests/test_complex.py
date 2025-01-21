"""
Tests for advanced Promptix functionality.
"""

import pytest
from typing import Dict, List, Any
from promptix import Promptix

def test_rpg_scenario_basic():
    """Test basic RPG scenario generation."""
    prompt = Promptix.get_prompt(
        prompt_template="DungeonMaster",
        game_style="heroic",
        party_level=3,
        party_classes=["Warrior", "Cleric", "Rogue"],
        environment="dungeon",
        quest_type="combat",
        difficulty="easy",
        custom_data={}  # Empty custom data to avoid undefined error
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_rpg_scenario_with_environment_details():
    """Test RPG scenario with detailed environment settings."""
    env_details = {
        "has_traps": True,
        "city_type": "merchant",
        "atmosphere": "tense"
    }
    prompt = Promptix.get_prompt(
        prompt_template="DungeonMaster",
        game_style="mystery",
        party_level=8,
        party_classes=["Bard", "Rogue"],
        environment="city",
        quest_type="diplomacy",
        difficulty="hard",
        environment_details=env_details,
        custom_data={}  # Empty custom data to avoid undefined error
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_rpg_scenario_with_magical_elements():
    """Test RPG scenario with magical elements."""
    magical_elements = ["Ancient Ley Lines", "Natural Magic"]
    prompt = Promptix.get_prompt(
        prompt_template="DungeonMaster",
        game_style="epic",
        party_level=15,
        party_classes=["Druid", "Ranger"],
        environment="wilderness",
        quest_type="mystery",
        difficulty="medium",
        magical_elements=magical_elements,
        custom_data={}  # Empty custom data to avoid undefined error
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_rpg_scenario_with_special_conditions():
    """Test RPG scenario with special conditions."""
    special_conditions = [
        "Political uprising imminent",
        "Hidden cult influence"
    ]
    prompt = Promptix.get_prompt(
        prompt_template="DungeonMaster",
        game_style="mystery",  # Changed from 'intrigue' to valid 'mystery'
        party_level=10,
        party_classes=["Rogue", "Wizard"],
        environment="city",
        quest_type="diplomacy",
        difficulty="hard",
        custom_data={"special_conditions": special_conditions}
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_rpg_scenario_invalid_difficulty():
    """Test error handling for invalid difficulty level."""
    with pytest.raises(ValueError):
        Promptix.get_prompt(
            prompt_template="DungeonMaster",
            game_style="heroic",
            party_level=1,
            party_classes=["Warrior"],
            environment="dungeon",
            quest_type="combat",
            difficulty="impossible"  # invalid difficulty
        )

def test_rpg_scenario_full_configuration():
    """Test RPG scenario with all possible configurations."""
    env_details = {
        "has_traps": True,
        "has_crime": True,
        "has_monsters": True,
        "city_type": "merchant",
        "atmosphere": "tense",
        "terrain_type": "urban"
    }
    magical_elements = ["Dark Magic", "Illusion Magic"]
    special_conditions = ["Corrupt city guard", "Hidden cult influence"]
    
    prompt = Promptix.get_prompt(
        prompt_template="DungeonMaster",
        game_style="mystery",
        party_level=12,
        party_classes=["Bard", "Rogue", "Wizard", "Paladin"],
        environment="city",
        quest_type="diplomacy",
        difficulty="hard",
        environment_details=env_details,
        magical_elements=magical_elements,
        custom_data={"special_conditions": special_conditions}
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0 
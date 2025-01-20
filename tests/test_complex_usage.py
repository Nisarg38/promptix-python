"""Tests for complex usage of Promptix library."""

from examples.complex_usage import generate_rpg_scenario


def test_basic_scenario():
    """Test basic RPG scenario generation."""
    prompt = generate_rpg_scenario(
        game_style="heroic",
        party_level=1,
        party_classes=["Fighter"],
        environment="city",
        quest_type="combat",
        difficulty="medium",
    )
    assert prompt is not None


def test_scenario_with_optional_params():
    """Test RPG scenario with optional parameters."""
    prompt = generate_rpg_scenario(
        game_style="mystery",
        party_level=8,
        party_classes=["Bard", "Rogue"],
        environment="city",
        quest_type="diplomacy",
        difficulty="hard",
        environment_details={"has_crime": True, "city_type": "merchant"},
        special_conditions=["Hidden cult influence"],
    )
    assert prompt is not None


def test_environment_details_defaults():
    """Test environment details defaults."""
    prompt = generate_rpg_scenario(
        game_style="epic",
        party_level=5,
        party_classes=["Warrior"],
        environment="dungeon",
        quest_type="combat",
        difficulty="easy",
    )
    assert prompt is not None


def test_magical_elements():
    """Test scenario with magical elements."""
    prompt = generate_rpg_scenario(
        game_style="epic",
        party_level=15,
        party_classes=["Wizard", "Sorcerer"],
        environment="wilderness",
        quest_type="mystery",
        difficulty="hard",
        magical_elements=["Ancient Magic", "Elemental Powers"],
    )
    assert prompt is not None

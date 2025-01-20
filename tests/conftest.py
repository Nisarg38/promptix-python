"""Configuration for Promptix tests."""

import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment with test prompts."""
    # Get paths
    root_dir = Path(__file__).parent.parent
    fixture_prompts = root_dir / "tests" / "fixtures" / "prompts.json"
    test_prompts = root_dir / "prompts.json"

    # Backup existing prompts.json if it exists
    if test_prompts.exists():
        backup_path = test_prompts.with_suffix(".json.bak")
        shutil.copy2(test_prompts, backup_path)

    # Copy test prompts to root directory
    shutil.copy2(fixture_prompts, test_prompts)

    yield

    # Cleanup: Remove test prompts
    if test_prompts.exists():
        os.remove(test_prompts)

    # Restore backup if it existed
    backup_path = test_prompts.with_suffix(".json.bak")
    if backup_path.exists():
        shutil.move(backup_path, test_prompts)

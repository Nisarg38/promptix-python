#!/usr/bin/env python3
"""
Script to check for duplicate version files in the prompts directory.
This helps identify version files that are exact duplicates of each other.
"""

import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def find_duplicate_versions(prompts_dir: Path) -> Dict[str, Dict[str, List[str]]]:
    """
    Find duplicate version files across all agents.
    
    Returns:
        Dict mapping agent_name -> {hash -> [version_files]}
    """
    results = {}
    
    # Iterate through all agent directories
    for agent_dir in prompts_dir.iterdir():
        if not agent_dir.is_dir():
            continue
            
        versions_dir = agent_dir / "versions"
        if not versions_dir.exists():
            continue
            
        # Build hash map for this agent's versions
        hash_map = defaultdict(list)
        version_files = sorted(versions_dir.glob("*.md"))
        
        for version_file in version_files:
            file_hash = get_file_hash(version_file)
            hash_map[file_hash].append(version_file.name)
        
        # Only include agents with duplicates
        duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
        if duplicates:
            results[agent_dir.name] = duplicates
    
    return results


def print_report(duplicates: Dict[str, Dict[str, List[str]]]):
    """Print a formatted report of duplicate versions."""
    if not duplicates:
        print("✅ No duplicate version files found!")
        return
    
    print("⚠️  Duplicate Version Files Detected\n")
    print("=" * 70)
    
    for agent_name, hash_groups in duplicates.items():
        print(f"\n📁 Agent: {agent_name}")
        print("-" * 70)
        
        for file_hash, version_files in hash_groups.items():
            print(f"\n  Hash: {file_hash}")
            print(f"  Duplicate versions ({len(version_files)}):")
            for version_file in sorted(version_files):
                print(f"    - {version_file}")
    
    print("\n" + "=" * 70)
    print("\n💡 Recommendation: Review these duplicates and ensure each version")
    print("   represents a meaningful change from the previous version.")


def main():
    """Main entry point."""
    # Find prompts directory
    script_dir = Path(__file__).parent
    prompts_dir = script_dir / "prompts"
    
    if not prompts_dir.exists():
        print(f"❌ Error: Prompts directory not found at {prompts_dir}")
        return 1
    
    print(f"🔍 Scanning for duplicate versions in: {prompts_dir}\n")
    
    duplicates = find_duplicate_versions(prompts_dir)
    print_report(duplicates)
    
    return 0 if not duplicates else 1


if __name__ == "__main__":
    exit(main())

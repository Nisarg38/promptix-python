# src/promptix/core/loaders.py
from abc import ABC, abstractmethod
import json
import yaml
from pathlib import Path
from typing import Dict, Any

class PromptLoader(ABC):
    @abstractmethod
    def load(self, file_path: Path) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        pass

class JSONPromptLoader(PromptLoader):
    def load(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

class YAMLPromptLoader(PromptLoader):
    def load(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)

class PromptLoaderFactory:
    @staticmethod
    def get_loader(file_path: Path) -> PromptLoader:
        if file_path.suffix.lower() == '.json':
            return JSONPromptLoader()
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            return YAMLPromptLoader()
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
# src/promptix/core/loaders.py
from abc import ABC, abstractmethod
import yaml
from pathlib import Path
from typing import Dict, Any
from ..exceptions import UnsupportedFormatError
from ..validation import get_validation_engine, ValidationType

class InvalidPromptSchemaError(ValueError):
    """Raised when prompt data fails schema validation"""
    def __init__(self, message: str):
        super().__init__(f"Prompt schema validation error: {message}")
        self.validation_message = message

class SchemaValidator:
    """Schema validation using the centralized validation engine."""
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> None:
        """Validate data against the default prompt schema."""
        try:
            validation_engine = get_validation_engine()
            validation_engine.validate_structure(data)
        except Exception as e:
            # Convert validation engine exceptions to the expected format for backward compatibility
            raise InvalidPromptSchemaError(str(e)) from e

class PromptLoader(ABC):
    @abstractmethod
    def load(self, file_path: Path) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        pass

    @abstractmethod
    def validate_loaded(self, data: Dict[str, Any]) -> None:
        """Validate loaded data against schema"""
        pass

class YAMLPromptLoader(PromptLoader):
    def load(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        self.validate_loaded(data)
        return data
    
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    def validate_loaded(self, data: Dict[str, Any]) -> None:
        """Validate loaded data against schema"""
        SchemaValidator.validate(data)

class PromptLoaderFactory:
    @staticmethod
    def get_loader(file_path) -> PromptLoader:
        # Convert string to Path if needed
        if isinstance(file_path, str):
            from pathlib import Path
            file_path = Path(file_path)
        
        if file_path.suffix.lower() in ['.yml', '.yaml']:
            return YAMLPromptLoader()
        elif file_path.suffix.lower() == '.json':
            raise UnsupportedFormatError(
                str(file_path),
                "json",
                ["yaml", "yml"]
            )
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}. Only YAML (.yaml, .yml) files are supported.")
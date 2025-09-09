# src/promptix/core/loaders.py
from abc import ABC, abstractmethod
import yaml
from pathlib import Path
from typing import Dict, Any
from jsonschema import Draft7Validator, ValidationError

class InvalidPromptSchemaError(ValueError):
    """Raised when prompt data fails schema validation"""
    def __init__(self, message: str):
        super().__init__(f"Prompt schema validation error: {message}")
        self.validation_message = message

class SchemaValidator:
    """Base class for schema validation"""
    
    _schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "schema": {"type": "number"}  # Schema version as a number
        },
        "additionalProperties": {  # All other properties (prompt definitions)
            "type": "object",
            "required": ["versions"],
            "properties": {
                "versions": {
                    "type": "object",
                    "patternProperties": {
                        r"^v\d+$": {
                            "type": "object",
                            "required": ["config"],
                            "properties": {
                                "config": {
                                    "type": "object",
                                    "required": ["system_instruction"],
                                    "properties": {
                                        "system_instruction": {"type": "string"},
                                        "model": {"type": "string"},
                                        "tools": {
                                            "type": "array",
                                            "items": {"type": "object"},
                                            "default": []
                                        }
                                    }
                                },
                                "tools_config": {
                                    "type": "object",
                                    "properties": {
                                        "tools_template": {"type": "string"},
                                        "tools": {
                                            "type": "object",
                                            "additionalProperties": {
                                                "type": "object",
                                                "properties": {
                                                    "description": {"type": "string"},
                                                    "parameters": {"type": "object"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    validator = Draft7Validator(_schema)

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> None:
        """Validate data against the schema"""
        try:
            cls.validator.validate(data)
        except ValidationError as e:
            error_path = ".".join(map(str, e.path))
            error_msg = f"Validation error at {error_path}: {e.message}"
            raise InvalidPromptSchemaError(error_msg) from e

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

class UnsupportedFormatError(ValueError):
    """Raised when trying to use an unsupported or deprecated file format"""
    def __init__(self, file_path: Path, message: str = None):
        if message is None:
            message = f"JSON format is no longer supported. Please convert {file_path} to YAML format (.yaml or .yml)"
        super().__init__(message)
        self.file_path = file_path

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
    def get_loader(file_path: Path) -> PromptLoader:
        if file_path.suffix.lower() in ['.yml', '.yaml']:
            return YAMLPromptLoader()
        elif file_path.suffix.lower() == '.json':
            raise UnsupportedFormatError(
                file_path, 
                f"JSON format is no longer supported. Please convert '{file_path}' to YAML format. "
                f"You can rename it to '{file_path.with_suffix('.yaml')}' and update the syntax if needed."
            )
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}. Only YAML (.yaml, .yml) files are supported.")
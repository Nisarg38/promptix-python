"""
Centralized Validation Engine for Promptix.

This module provides a unified validation system that consolidates all validation
logic previously scattered across multiple files. It provides:

1. Variable validation against prompt schemas
2. Structural validation using JSON Schema
3. Type validation for builder patterns
4. Extensible validation strategies

This replaces the scattered validation logic from:
- components/variable_validator.py
- storage/loaders.py (SchemaValidator) 
- builder.py (_validate_type)
- base.py (_validate_variables)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type
from enum import Enum
from jsonschema import Draft7Validator, ValidationError as JsonSchemaValidationError

from .exceptions import (
    VariableValidationError,
    RequiredVariableError,
    create_validation_error,
    SchemaValidationError,
)


class ValidationType(Enum):
    """Types of validation that can be performed."""
    VARIABLE = "variable"
    STRUCTURAL = "structural" 
    TYPE = "type"
    BUILDER = "builder"


class ValidationStrategy(ABC):
    """Abstract base class for different validation strategies."""
    
    @abstractmethod
    def validate(self, data: Any, schema: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Perform validation on the provided data."""
        pass


class VariableValidationStrategy(ValidationStrategy):
    """Strategy for validating prompt variables against their schema."""
    
    def __init__(self, logger=None):
        self._logger = logger
    
    def validate(self, data: Any, schema: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Validate user variables against the prompt's schema.
        
        Args:
            data: User variables to validate
            schema: The prompt schema definition
            context: Additional context (should contain 'prompt_name')
        """
        if not isinstance(data, dict):
            raise VariableValidationError(
                prompt_name=context.get('prompt_name', 'unknown'),
                variable_name="root",
                error_message="Variables must be provided as a dictionary",
                provided_value=data
            )
        
        prompt_name = context.get('prompt_name', 'unknown')
        self._validate_required_variables(data, schema, prompt_name)
        self._validate_variable_types(data, schema, prompt_name)
    
    def _validate_required_variables(
        self, 
        user_vars: Dict[str, Any], 
        schema: Dict[str, Any], 
        prompt_name: str
    ) -> None:
        """Check that all required variables are present."""
        required = schema.get("required", [])
        missing_required = [r for r in required if r not in user_vars]
        
        if missing_required:
            provided_vars = list(user_vars.keys())
            raise RequiredVariableError(
                prompt_name=prompt_name,
                missing_variables=missing_required,
                provided_variables=provided_vars
            )
    
    def _validate_variable_types(
        self, 
        user_vars: Dict[str, Any], 
        schema: Dict[str, Any], 
        prompt_name: str
    ) -> None:
        """Validate variable types and enumerations."""
        types_dict = schema.get("types", {})
        
        for var_name, var_value in user_vars.items():
            if var_name not in types_dict:
                continue  # Skip variables not defined in schema
            
            expected_type = types_dict[var_name]
            
            # Handle enumeration constraints (list of allowed values)
            if isinstance(expected_type, list):
                if var_value not in expected_type:
                    raise create_validation_error(
                        prompt_name=prompt_name,
                        field=var_name,
                        value=var_value,
                        enum_values=expected_type
                    )
            
            # Handle type constraints (string type names)
            elif isinstance(expected_type, str):
                self._validate_type_constraint(
                    var_name, var_value, expected_type, prompt_name
                )
    
    def _validate_type_constraint(
        self, 
        var_name: str, 
        var_value: Any, 
        expected_type: str, 
        prompt_name: str
    ) -> None:
        """Validate a single variable against its type constraint."""
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, (list, tuple)),
            "object": lambda v: isinstance(v, dict),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        
        if expected_type in type_checks:
            if not type_checks[expected_type](var_value):
                raise create_validation_error(
                    prompt_name=prompt_name,
                    field=var_name,
                    value=var_value,
                    expected_type=expected_type
                )
        elif self._logger:
            self._logger.warning(
                f"Unknown type constraint '{expected_type}' for variable '{var_name}' "
                f"in prompt '{prompt_name}'. Skipping type validation."
            )


class StructuralValidationStrategy(ValidationStrategy):
    """Strategy for JSON Schema-based structural validation."""
    
    # Default schema for prompt files
    DEFAULT_PROMPT_SCHEMA = {
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
    
    def __init__(self, custom_schema: Optional[Dict[str, Any]] = None):
        """Initialize with optional custom schema."""
        schema = custom_schema or self.DEFAULT_PROMPT_SCHEMA
        self._validator = Draft7Validator(schema)
    
    def validate(self, data: Any, schema: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Validate data against JSON schema."""
        try:
            # Use provided schema or fall back to default
            if schema:
                validator = Draft7Validator(schema)
                validator.validate(data)
            else:
                self._validator.validate(data)
        except JsonSchemaValidationError as e:
            error_path = ".".join(map(str, e.path))
            error_msg = f"Validation error at {error_path}: {e.message}"
            raise SchemaValidationError(
                prompt_name=context.get('prompt_name', 'unknown'),
                schema_errors=[error_msg]
            ) from e


class BuilderValidationStrategy(ValidationStrategy):
    """Strategy for validating builder pattern fields."""
    
    def validate(self, data: Any, schema: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Validate a builder field against its schema properties."""
        field = context.get('field')
        properties = schema.get('properties', {})
        
        if not field:
            raise ValueError("Builder validation requires 'field' in context")
        
        self._validate_field(field, data, properties)
    
    def _validate_field(self, field: str, value: Any, properties: Dict[str, Any]) -> None:
        """Validate a single field against its schema properties."""
        if field not in properties:
            return  # Skip validation for undefined fields
        
        prop = properties[field]
        expected_type = prop.get("type")
        enum_values = prop.get("enum")
        
        # Type validation
        if expected_type:
            self._validate_type(field, value, expected_type)
        
        # Enumeration validation
        if enum_values is not None and value not in enum_values:
            raise create_validation_error(
                prompt_name="builder",
                field=field,
                value=value,
                enum_values=enum_values
            )
    
    def _validate_type(self, field: str, value: Any, expected_type: str) -> None:
        """Validate value type."""
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, (list, tuple)),
            "object": lambda v: isinstance(v, dict)
        }
        
        if expected_type in type_checks and not type_checks[expected_type](value):
            raise VariableValidationError(
                prompt_name="builder",
                variable_name=field,
                error_message=f"must be a {expected_type}, got {type(value).__name__}",
                provided_value=value,
                expected_type=expected_type
            )


class ValidationEngine:
    """
    Centralized validation engine that consolidates all validation logic.
    
    This class provides a unified interface for all validation operations,
    replacing the scattered validation logic throughout the codebase.
    """
    
    def __init__(self, logger=None):
        """Initialize the validation engine."""
        self._logger = logger
        self._strategies = {
            ValidationType.VARIABLE: VariableValidationStrategy(logger),
            ValidationType.STRUCTURAL: StructuralValidationStrategy(),
            ValidationType.BUILDER: BuilderValidationStrategy(),
        }
    
    def register_strategy(self, validation_type: ValidationType, strategy: ValidationStrategy) -> None:
        """Register a custom validation strategy."""
        self._strategies[validation_type] = strategy
    
    def validate(
        self, 
        data: Any, 
        schema: Dict[str, Any], 
        validation_type: ValidationType,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Perform validation using the specified strategy.
        
        Args:
            data: Data to validate
            schema: Schema to validate against
            validation_type: Type of validation to perform
            context: Additional context for validation
        """
        if validation_type not in self._strategies:
            raise ValueError(f"Unknown validation type: {validation_type}")
        
        context = context or {}
        strategy = self._strategies[validation_type]
        strategy.validate(data, schema, context)
    
    # Convenience methods for backward compatibility
    
    def validate_variables(
        self, 
        schema: Dict[str, Any], 
        user_vars: Dict[str, Any],
        prompt_name: str
    ) -> None:
        """Validate user variables against prompt schema (backward compatibility)."""
        self.validate(
            data=user_vars,
            schema=schema,
            validation_type=ValidationType.VARIABLE,
            context={'prompt_name': prompt_name}
        )
    
    def validate_structure(self, data: Dict[str, Any], custom_schema: Optional[Dict[str, Any]] = None) -> None:
        """Validate data structure using JSON Schema (backward compatibility)."""
        # For structural validation, we use the schema as validation target
        validation_schema = custom_schema or {}
        self.validate(
            data=data,
            schema=validation_schema,
            validation_type=ValidationType.STRUCTURAL,
            context={'prompt_name': 'structure'}
        )
    
    def validate_builder_field(
        self, 
        field: str, 
        value: Any, 
        properties: Dict[str, Any]
    ) -> None:
        """Validate a builder field (backward compatibility)."""
        self.validate(
            data=value,
            schema={'properties': properties},
            validation_type=ValidationType.BUILDER,
            context={'field': field}
        )


# Global instance for backward compatibility
_default_engine = None

def get_validation_engine(logger=None) -> ValidationEngine:
    """Get the default validation engine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = ValidationEngine(logger)
    return _default_engine


# Backward compatibility functions
def validate_variables(schema: Dict[str, Any], user_vars: Dict[str, Any], prompt_name: str) -> None:
    """Validate variables using the default validation engine."""
    engine = get_validation_engine()
    engine.validate_variables(schema, user_vars, prompt_name)


def validate_structure(data: Dict[str, Any], custom_schema: Optional[Dict[str, Any]] = None) -> None:
    """Validate structure using the default validation engine."""
    engine = get_validation_engine()
    engine.validate_structure(data, custom_schema)


def validate_builder_field(field: str, value: Any, properties: Dict[str, Any]) -> None:
    """Validate builder field using the default validation engine."""
    engine = get_validation_engine()
    engine.validate_builder_field(field, value, properties)

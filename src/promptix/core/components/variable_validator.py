"""
VariableValidator component for validating variables against schemas.

This component handles validation of user-provided variables against
prompt schemas, including type checking and required field validation.

DEPRECATED: This class is maintained for backward compatibility only.
New code should use the centralized ValidationEngine from core.validation.
"""

from typing import Any, Dict, List
from ..exceptions import (
    VariableValidationError, 
    RequiredVariableError, 
    create_validation_error
)
from ..validation import get_validation_engine


class VariableValidator:
    """
    Handles validation of variables against prompt schemas.
    
    DEPRECATED: This is a backward compatibility wrapper around the centralized ValidationEngine.
    """
    
    def __init__(self, logger=None):
        """Initialize the variable validator.
        
        Args:
            logger: Optional logger instance for dependency injection.
        """
        self._logger = logger
        self._validation_engine = get_validation_engine(logger)
    
    def validate_variables(
        self, 
        schema: Dict[str, Any], 
        user_vars: Dict[str, Any],
        prompt_name: str
    ) -> None:
        """
        Validate user variables against the prompt's schema.
        
        DEPRECATED: Uses centralized ValidationEngine internally.
        
        Args:
            schema: The prompt schema definition.
            user_vars: Variables provided by the user.
            prompt_name: Name of the prompt template for error reporting.
            
        Raises:
            RequiredVariableError: If required variables are missing.
            VariableValidationError: If variable validation fails.
        """
        # Delegate to centralized validation engine
        self._validation_engine.validate_variables(schema, user_vars, prompt_name)

    
    def validate_builder_type(self, field: str, value: Any, properties: Dict[str, Any]) -> None:
        """
        Validate a single field against its schema properties (for builder pattern).
        
        DEPRECATED: Uses centralized ValidationEngine internally.
        
        Args:
            field: Name of the field.
            value: Value to validate.
            properties: Schema properties definition.
            
        Raises:
            VariableValidationError: If validation fails.
        """
        # Delegate to centralized validation engine
        self._validation_engine.validate_builder_field(field, value, properties)

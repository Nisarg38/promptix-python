"""
VariableValidator component for validating variables against schemas.

This component handles validation of user-provided variables against
prompt schemas, including type checking and required field validation.
"""

from typing import Any, Dict, List
from ..exceptions import (
    VariableValidationError, 
    RequiredVariableError, 
    create_validation_error
)


class VariableValidator:
    """Handles validation of variables against prompt schemas."""
    
    def __init__(self, logger=None):
        """Initialize the variable validator.
        
        Args:
            logger: Optional logger instance for dependency injection.
        """
        self._logger = logger
    
    def validate_variables(
        self, 
        schema: Dict[str, Any], 
        user_vars: Dict[str, Any],
        prompt_name: str
    ) -> None:
        """
        Validate user variables against the prompt's schema.
        
        Performs the following validations:
        1. Check required variables are present
        2. Check variable types match expected types
        3. Check enumeration constraints
        
        Args:
            schema: The prompt schema definition.
            user_vars: Variables provided by the user.
            prompt_name: Name of the prompt template for error reporting.
            
        Raises:
            RequiredVariableError: If required variables are missing.
            VariableValidationError: If variable validation fails.
        """
        required = schema.get("required", [])
        optional = schema.get("optional", [])
        types_dict = schema.get("types", {})

        # --- 1) Check required variables ---
        missing_required = [r for r in required if r not in user_vars]
        if missing_required:
            provided_vars = list(user_vars.keys())
            raise RequiredVariableError(
                prompt_name=prompt_name,
                missing_variables=missing_required,
                provided_variables=provided_vars
            )

        # --- 2) Check for unknown variables (optional check) ---
        # Currently disabled to allow flexibility, but can be enabled by uncommenting:
        # allowed_vars = set(required + optional)
        # unknown_vars = [k for k in user_vars if k not in allowed_vars]
        # if unknown_vars:
        #     raise VariableValidationError(
        #         prompt_name=prompt_name,
        #         variable_name=','.join(unknown_vars),
        #         error_message=f"unknown variables not allowed",
        #         provided_value=unknown_vars
        #     )
        
        # --- 3) Type checking and enumeration checks ---
        for var_name, var_value in user_vars.items():
            if var_name not in types_dict:
                # Not specified in the schema, skip type check
                continue

            expected_type = types_dict[var_name]
            
            # 3.1) If it's a list, treat it as enumeration of allowed values
            if isinstance(expected_type, list):
                if var_value not in expected_type:
                    raise create_validation_error(
                        prompt_name=prompt_name,
                        field=var_name,
                        value=var_value,
                        enum_values=expected_type
                    )
            
            # 3.2) If it's a string specifying a type name
            elif isinstance(expected_type, str):
                self._validate_type_constraint(
                    var_name=var_name,
                    var_value=var_value,
                    expected_type=expected_type,
                    prompt_name=prompt_name
                )

    def _validate_type_constraint(
        self, 
        var_name: str, 
        var_value: Any, 
        expected_type: str, 
        prompt_name: str
    ) -> None:
        """Validate a single variable against its type constraint.
        
        Args:
            var_name: Name of the variable.
            var_value: Value of the variable.
            expected_type: Expected type as string.
            prompt_name: Name of the prompt template for error reporting.
            
        Raises:
            VariableValidationError: If type validation fails.
        """
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
        # If type is not recognized, we skip validation with a warning
        elif self._logger:
            self._logger.warning(
                f"Unknown type constraint '{expected_type}' for variable '{var_name}' "
                f"in prompt '{prompt_name}'. Skipping type validation."
            )
    
    def validate_builder_type(self, field: str, value: Any, properties: Dict[str, Any]) -> None:
        """Validate a single field against its schema properties (for builder pattern).
        
        Args:
            field: Name of the field.
            value: Value to validate.
            properties: Schema properties definition.
            
        Raises:
            VariableValidationError: If validation fails.
        """
        if field not in properties:
            # If additional properties are not allowed, this should be checked
            # at the builder level
            return

        prop = properties[field]
        expected_type = prop.get("type")
        enum_values = prop.get("enum")

        # Type validation
        if expected_type == "string":
            if not isinstance(value, str):
                raise VariableValidationError(
                    prompt_name="builder",
                    variable_name=field,
                    error_message=f"must be a string, got {type(value).__name__}",
                    provided_value=value,
                    expected_type="string"
                )
        elif expected_type == "number":
            if not (isinstance(value, (int, float)) and not isinstance(value, bool)):
                raise VariableValidationError(
                    prompt_name="builder",
                    variable_name=field,
                    error_message=f"must be a number, got {type(value).__name__}",
                    provided_value=value,
                    expected_type="number"
                )
        elif expected_type == "integer":
            if not (isinstance(value, int) and not isinstance(value, bool)):
                raise VariableValidationError(
                    prompt_name="builder",
                    variable_name=field,
                    error_message=f"must be an integer, got {type(value).__name__}",
                    provided_value=value,
                    expected_type="integer"
                )
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                raise VariableValidationError(
                    prompt_name="builder",
                    variable_name=field,
                    error_message=f"must be a boolean, got {type(value).__name__}",
                    provided_value=value,
                    expected_type="boolean"
                )

        # Enumeration validation
        if enum_values is not None and value not in enum_values:
            raise create_validation_error(
                prompt_name="builder",
                field=field,
                value=value,
                enum_values=enum_values
            )

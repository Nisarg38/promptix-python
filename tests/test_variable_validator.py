# flake8: noqa
# Auto-generated tests for VariableValidator component.
# Framework: pytest
import os
import sys
import types
from typing import Any

# Best-effort import shim: try common roots under src/ and package dirs
# This avoids brittle relative imports while keeping tests runnable in CI and locally.
_CANDIDATE_ROOTS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
]
for _root in _CANDIDATE_ROOTS:
    if _root not in sys.path and os.path.isdir(_root):
        sys.path.insert(0, _root)

# Try a set of possible module paths
_VAR_VALIDATOR = None
_EXC = None
_MODULE_CANDIDATES = [
    # common paths
    "variable_validator",
    "validator.variable_validator",
    "components.variable_validator",
    "core.variable_validator",
    "src.variable_validator",
    "app.variable_validator",
    # deeper paths (based on relative import '..exceptions' seen in snippet)
    "prompt.variable_validator",
    "prompt.validation.variable_validator",
    "prompting.variable_validator",
]

_EXC_CANDIDATES = [
    "exceptions",
    "core.exceptions",
    "components.exceptions",
    "src.exceptions",
    "prompt.exceptions",
    "prompt.validation.exceptions",
    "app.exceptions",
]

VariableValidator = None
create_validation_error = None
VariableValidationError = None
RequiredVariableError = None

for mod_name in _MODULE_CANDIDATES:
    try:
        _mod = __import__(mod_name, fromlist=["VariableValidator"])
        if hasattr(_mod, "VariableValidator"):
            VariableValidator = getattr(_mod, "VariableValidator")
            _VAR_VALIDATOR = _mod
            break
    except Exception:
        continue

for exc_name in _EXC_CANDIDATES:
    try:
        _ex = __import__(exc_name, fromlist=["VariableValidationError", "RequiredVariableError", "create_validation_error"])
        if hasattr(_ex, "VariableValidationError") and hasattr(_ex, "RequiredVariableError") and hasattr(_ex, "create_validation_error"):
            VariableValidationError = getattr(_ex, "VariableValidationError")
            RequiredVariableError = getattr(_ex, "RequiredVariableError")
            create_validation_error = getattr(_ex, "create_validation_error")
            _EXC = _ex
            break
    except Exception:
        continue

assert VariableValidator is not None, "Could not import VariableValidator module. Adjust _MODULE_CANDIDATES to match actual path."
assert VariableValidationError is not None and RequiredVariableError is not None and create_validation_error is not None, "Could not import exceptions. Adjust _EXC_CANDIDATES to match actual path."

class DummyLogger:
    def __init__(self):
        self.warnings = []
    def warning(self, msg: str):
        self.warnings.append(msg)

def test_required_variables_missing_raises_required_variable_error():
    validator = VariableValidator()
    schema = {
        "required": ["name", "age"],
        "types": {"name": "string", "age": "integer"},
    }
    user_vars = {"name": "Alice"}  # missing age
    try:
        validator.validate_variables(schema, user_vars, prompt_name="signup")
        assert False, "Expected RequiredVariableError"
    except RequiredVariableError as e:
        # Basic assertions; exact attributes may vary by implementation
        msg = str(e)
        assert "signup" in msg
        assert "age" in msg
        assert "name" in msg

def test_no_required_missing_and_unspecified_type_is_ignored():
    validator = VariableValidator()
    schema = {
        "required": ["name"],
        "types": {"name": "string"},  # 'nickname' not in types -> skip
    }
    user_vars = {"name": "Bob", "nickname": 123}
    validator.validate_variables(schema, user_vars, prompt_name="profile")  # should not raise

def test_type_string_valid_and_invalid():
    validator = VariableValidator()
    schema = {"required": ["x"], "types": {"x": "string"}}
    validator.validate_variables(schema, {"x": "ok"}, "t1")  # pass
    try:
        validator.validate_variables(schema, {"x": 123}, "t1")
        assert False, "Expected VariableValidationError for non-string"
    except VariableValidationError as e:
        assert "x" in str(e)

def test_type_integer_accepts_int_and_bool_semantics_edge():
    validator = VariableValidator()
    schema = {"required": ["n"], "types": {"n": "integer"}}
    # int passes
    validator.validate_variables(schema, {"n": 7}, "t2")
    # bool is instance of int in Python; current implementation will accept it. Document that behavior.
    validator.validate_variables(schema, {"n": True}, "t2")  # should not raise by current implementation

def test_type_boolean_valid_and_invalid():
    validator = VariableValidator()
    schema = {"required": ["b"], "types": {"b": "boolean"}}
    validator.validate_variables(schema, {"b": False}, "t3")
    try:
        validator.validate_variables(schema, {"b": 0}, "t3")
        assert False, "Expected VariableValidationError for non-boolean"
    except VariableValidationError as e:
        assert "b" in str(e)

def test_type_array_and_object():
    validator = VariableValidator()
    schema = {
        "required": ["arr", "obj"],
        "types": {"arr": "array", "obj": "object"},
    }
    validator.validate_variables(schema, {"arr": [1,2], "obj": {"k": "v"}}, "t4")
    # invalid array
    try:
        validator.validate_variables(schema, {"arr": "notlist", "obj": {}}, "t4")
        assert False, "Expected VariableValidationError for array"
    except VariableValidationError:
        pass
    # invalid object
    try:
        validator.validate_variables(schema, {"arr": [], "obj": ["notdict"]}, "t4")
        assert False, "Expected VariableValidationError for object"
    except VariableValidationError:
        pass

def test_type_number_accepts_int_and_float_rejects_str():
    validator = VariableValidator()
    schema = {"required": ["v"], "types": {"v": "number"}}
    validator.validate_variables(schema, {"v": 1}, "t5")
    validator.validate_variables(schema, {"v": 3.14}, "t5")
    try:
        validator.validate_variables(schema, {"v": "3.14"}, "t5")
        assert False, "Expected VariableValidationError for number"
    except VariableValidationError:
        pass

def test_enumeration_string_and_int_values():
    validator = VariableValidator()
    schema = {
        "required": ["color", "retries"],
        "types": {
            "color": ["red", "green", "blue"],
            "retries": [0, 1, 2, 3],
        },
    }
    # valid enums
    validator.validate_variables(schema, {"color": "red", "retries": 2}, "t6")
    # invalid enum string
    try:
        validator.validate_variables(schema, {"color": "purple", "retries": 1}, "t6")
        assert False, "Expected VariableValidationError for enum (color)"
    except VariableValidationError as e:
        assert "color" in str(e)
    # invalid enum int
    try:
        validator.validate_variables(schema, {"color": "blue", "retries": 5}, "t6")
        assert False, "Expected VariableValidationError for enum (retries)"
    except VariableValidationError as e:
        assert "retries" in str(e)

def test_unknown_type_constraint_logs_warning_and_skips():
    logger = DummyLogger()
    validator = VariableValidator(logger=logger)
    schema = {"required": ["z"], "types": {"z": "uuid"}}
    # Should not raise, but log a warning
    validator.validate_variables(schema, {"z": "anything"}, "t7")
    assert any("Unknown type constraint 'uuid'" in w for w in logger.warnings)

# --- validate_builder_type tests ---

def test_validate_builder_type_skips_when_field_not_in_properties():
    validator = VariableValidator()
    validator.validate_builder_type("absent", 123, properties={"present": {"type": "number"}})  # no raise

def test_validate_builder_type_type_enforcement_and_messages():
    validator = VariableValidator()
    props = {
        "s": {"type": "string"},
        "n": {"type": "number"},
        "i": {"type": "integer"},
        "b": {"type": "boolean"},
    }
    # valid cases
    validator.validate_builder_type("s", "ok", props)
    validator.validate_builder_type("n", 1.2, props)
    validator.validate_builder_type("i", 3, props)
    validator.validate_builder_type("b", True, props)

    # invalid string
    try:
        validator.validate_builder_type("s", 10, props)
        assert False, "Expected VariableValidationError for string"
    except VariableValidationError as e:
        text = str(e)
        assert "builder" in text and "string" in text

    # invalid number
    try:
        validator.validate_builder_type("n", "NaN", props)
        assert False, "Expected VariableValidationError for number"
    except VariableValidationError as e:
        text = str(e)
        assert "number" in text

    # invalid integer (note: bool is instance of int; test non-int)
    try:
        validator.validate_builder_type("i", 3.3, props)
        assert False, "Expected VariableValidationError for integer"
    except VariableValidationError as e:
        text = str(e)
        assert "integer" in text

    # invalid boolean
    try:
        validator.validate_builder_type("b", "false", props)
        assert False, "Expected VariableValidationError for boolean"
    except VariableValidationError as e:
        text = str(e)
        assert "boolean" in text

def test_validate_builder_type_enum_enforcement():
    validator = VariableValidator()
    props = {
        "mode": {"type": "string", "enum": ["fast", "accurate"]},
        "count": {"type": "integer", "enum": [1, 2, 3]},
    }
    # valid enums
    validator.validate_builder_type("mode", "fast", props)
    validator.validate_builder_type("count", 2, props)

    # invalid enums
    try:
        validator.validate_builder_type("mode", "turbo", props)
        assert False, "Expected VariableValidationError for enum mode"
    except VariableValidationError as e:
        assert "mode" in str(e)

    try:
        validator.validate_builder_type("count", 5, props)
        assert False, "Expected VariableValidationError for enum count"
    except VariableValidationError as e:
        assert "count" in str(e)

# --- Supplemental tests appended by CI agent (pytest) ---

def test_required_variables_with_multiple_missing_are_reported():
    validator = VariableValidator()
    schema = {"required": ["a", "b", "c"], "types": {"a": "string", "b": "number"}}
    user_vars = {"a": "x"}  # b and c missing
    import pytest
    with pytest.raises(RequiredVariableError) as ei:
        validator.validate_variables(schema, user_vars, "multi")
    msg = str(ei.value)
    assert "b" in msg and "c" in msg
    assert "a" in msg  # provided vars reflected

def test_types_not_specified_in_schema_are_skipped_no_raise():
    validator = VariableValidator()
    schema = {"required": [], "types": {}}
    validator.validate_variables(schema, {"free": object()}, "freeform")

def test_enumeration_with_mixed_types():
    validator = VariableValidator()
    schema = {"required": ["v"], "types": {"v": [1, "two", 3]}}
    # valid mixed-type enum values
    validator.validate_variables(schema, {"v": 1}, "enum-mix")
    validator.validate_variables(schema, {"v": "two"}, "enum-mix")
    # invalid value not in enum
    import pytest
    with pytest.raises(VariableValidationError):
        validator.validate_variables(schema, {"v": 2}, "enum-mix")
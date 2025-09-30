import pytest
from promptix import Promptix

def test_variables_with_with_var():
    """Test that variables set with with_var are stored in the _data dictionary."""
    # Use the existing ComplexCodeReviewer prompt
    builder = Promptix.builder("ComplexCodeReviewer")
    
    # Set variables with with_var
    test_vars = {
        'programming_language': 'Python',
        'severity': 'high',
        'review_focus': 'security and performance'
    }
    builder.with_var(test_vars)
    
    # Verify all variables from with_var are stored in _data
    for key, value in test_vars.items():
        assert key in builder._data
        assert builder._data[key] == value

def test_with_tool_activates_tool():
    """Test that with_tool properly activates tools."""
    # Use the existing ComplexCodeReviewer prompt
    builder = Promptix.builder("ComplexCodeReviewer")
    
    # Explicitly activate tools
    tool_name = "complexity_analyzer"
    builder.with_tool(tool_name)
    
    # Verify the tool is activated in _data
    assert f"use_{tool_name}" in builder._data
    assert builder._data[f"use_{tool_name}"] is True

def test_with_tool_parameter_sets_parameter():
    """Test that with_tool_parameter correctly sets tool parameters."""
    # Use the existing ComplexCodeReviewer prompt
    builder = Promptix.builder("ComplexCodeReviewer")
    
    # Set variables with with_var
    builder.with_var({
        'programming_language': 'Python',
        'severity': 'high',
        'review_focus': 'security'
    })
    
    # Activate a tool and set a parameter
    tool_name = "complexity_analyzer"
    param_name = "thresholds"
    param_value = {"cyclomatic": 8, "cognitive": 5}
    
    builder.with_tool(tool_name)
    builder.with_tool_parameter(tool_name, param_name, param_value)
    
    # Verify the tool parameter is set in _data
    # The parameters are stored in a nested structure under 'tool_params_{tool_name}'
    tool_params_key = f"tool_params_{tool_name}"
    assert tool_params_key in builder._data
    assert param_name in builder._data[tool_params_key]
    assert builder._data[tool_params_key][param_name] == param_value 
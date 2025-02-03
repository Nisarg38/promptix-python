import pytest
from promptix import Promptix

def test_prepare_model_config_basic():
    memory = [
        {"role": "user", "content": "Test message"},
        {"role": "assistant", "content": "Test response"}
    ]
    
    model_config = Promptix.prepare_model_config(
        prompt_template="CustomerSupport",
        user_name="Test User",
        issue_type="test",
        technical_level="beginner",
        interaction_history="none",
        product_version="1.0.0",
        issue_description="Test description",
        custom_data={"product_version": "1.0.0", "subscription_tier": "standard"},
        memory=memory,
    )
    
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 0

def test_prepare_model_config_memory_validation():
    with pytest.raises(ValueError):
        Promptix.prepare_model_config(
            prompt_template="CustomerSupport",
            user_name="Test User",
            memory=[{"invalid": "format"}]  # Invalid memory format
        )

def test_prepare_model_config_required_fields():
    with pytest.raises(ValueError, match="missing required variables"):
        Promptix.prepare_model_config(
            prompt_template="CustomerSupport",
            version="v3",
            memory=[],
            user_name="Test User"  # Missing other required fields
        )

def test_prepare_model_config_custom_data():
    memory = [
        {"role": "user", "content": "Test message"}
    ]
    
    model_config = Promptix.prepare_model_config(
        prompt_template="CustomerSupport",
        user_name="Test User",
        issue_type="general",
        issue_description="Test issue",
        technical_level="intermediate",
        memory=memory,
        custom_data={
            "special_field": "test_value",
            "priority": "high"
        }
    )
    
    assert isinstance(model_config, dict)
    assert "messages" in model_config 
# Dynamic Prompt Generation

## Overview
The dynamic prompt generation system enhances Promptix's prompt management capabilities by introducing flexible, template-based prompt creation with conditional logic and runtime customization.

## Key Features

### Template-Based Design
- Templates use a familiar Jinja-like syntax with `{{variable}}` placeholders
- Support for nested structures and complex data types
- Built-in validation for required variables

### Dynamic Content Insertion
```python
# Example usage
prompt = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    context={
        "user_name": "John Doe",
        "issue_type": "technical",
        "priority": "high",
        "custom_data": {
            "product_version": "2.1.0",
            "subscription_tier": "premium"
        }
    }
)
```

### Conditional Logic
Templates support conditional blocks for content variation:
```
{% if priority == "high" %}
Urgent: Immediate attention required for {{issue_type}} issue
{% else %}
Standard support request for {{issue_type}} issue
{% endif %}

User: {{user_name}}
Product Version: {{custom_data.product_version}}
```

### Version Control Integration
- Seamless integration with existing version control
- Access to specific versions using the `version` parameter
- Automatic tracking of template modifications

### Template Structure
```json
{
    "CustomerSupport": {
        "versions": {
            "v1": {
                "system_message": "Template content with {{variables}}",
                "metadata": {
                    "created_at": "timestamp",
                    "author": "user",
                    "description": "Template description"
                },
                "is_live": true
            }
        },
        "schema": {
            "required": ["user_name", "issue_type"],
            "optional": ["priority", "custom_data"],
            "types": {
                "priority": ["high", "medium", "low"],
                "custom_data": "object"
            }
        }
    }
}
```

## Best Practices
1. Always define required variables in the schema
2. Use descriptive variable names
3. Include template documentation
4. Test conditional logic with different inputs
5. Maintain backward compatibility when updating templates

## Error Handling
The system provides clear error messages for:
- Missing required variables
- Invalid variable types
- Unknown template references
- Version conflicts
- Schema validation failures 
User Guide
==========

This comprehensive guide covers all aspects of using Promptix effectively.

.. contents::
   :local:
   :depth: 2

Getting Started
---------------

After installation, Promptix is ready to use with minimal setup. The library follows a simple workflow:

1. **Define prompts** in YAML files
2. **Load prompts** using the Promptix class
3. **Render prompts** with variables
4. **Use results** in your application

Project Structure
~~~~~~~~~~~~~~~~~

A typical Promptix project structure:

.. code-block::

   my-project/
   ├── prompts.yaml          # Main prompt definitions
   ├── app.py               # Your application
   ├── .env                 # Environment variables (optional)
   └── templates/           # Additional prompt files (optional)
       ├── emails.yaml
       └── notifications.yaml

Prompt File Format
------------------

Promptix uses YAML for prompt definitions. Here's the complete format:

Basic Structure
~~~~~~~~~~~~~~~

.. code-block:: yaml

   prompt_name:
     name: prompt_name
     description: "Description of what this prompt does"
     versions:
       version_name:
         is_live: true|false
         config:
           system_instruction: "Your template content here"
           temperature: 0.7
           max_tokens: 1000
           model: gpt-4o|claude-3-5-sonnet-20241022
           provider: openai|anthropic
         metadata:
           created_at: '2024-01-01'
           author: 'Author Name'
           last_modified: '2024-01-01'
           last_modified_by: 'Author Name'
         schema:
           required:
             - variable_name
           optional:
             - optional_variable
           properties:
             variable_name:
               type: string|integer|number|boolean|array|object
               description: "Variable description"
               default: default_value  # optional
               enum: [list, of, allowed, values]  # optional
               validation:  # optional
                 min: minimum_value
                 max: maximum_value
                 pattern: "regex_pattern"
           additionalProperties: false

Complete Example
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   user_onboarding:
     name: user_onboarding
     description: Comprehensive user onboarding prompt with conditional logic and loops
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Welcome {{user_name}}!
             
             Your account type: {{account_type}}
             {% if is_trial %}
             You have {{trial_days}} days remaining in your trial.
             {% endif %}
             
             Next steps:
             {% for step in next_steps %}
             {{loop.index}}. {{step}}
             {% endfor %}
           temperature: 0.7
           max_tokens: 500
           top_p: 1
           frequency_penalty: 0
           presence_penalty: 0
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
           last_modified: '2024-01-01'
           last_modified_by: Promptix Team
         schema:
           required:
             - user_name
             - account_type
             - next_steps
           optional:
             - is_trial
             - trial_days
           properties:
             user_name:
               type: string
               description: "The user's display name"
             account_type:
               type: string
               description: "User's subscription tier"
               enum: ["free", "pro", "enterprise"]
             is_trial:
               type: boolean
               description: "Whether user is on trial"
               default: false
             trial_days:
               type: integer
               description: "Days remaining in trial"
               validation:
                 min: 0
                 max: 30
             next_steps:
               type: array
               description: "List of onboarding steps"
           additionalProperties: false

Advanced Template Features
--------------------------

Jinja2 Integration
~~~~~~~~~~~~~~~~~~

Promptix uses Jinja2 as its template engine, providing powerful features:

**Variables and Expressions**:

.. code-block:: yaml

   math_prompt:
     name: math_prompt
     description: Prompt demonstrating mathematical expressions in templates
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Result: {{(value1 + value2) * multiplier}}
             Percentage: {{(score / total) * 100}}%
           temperature: 0.3
           max_tokens: 150
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - value1
             - value2
             - multiplier
             - score
             - total
           optional: []
           properties:
             value1:
               type: number
               description: "First numerical value"
             value2:
               type: number
               description: "Second numerical value"
             multiplier:
               type: number
               description: "Multiplication factor"
             score:
               type: number
               description: "Score value for percentage calculation"
             total:
               type: number
               description: "Total value for percentage calculation"
           additionalProperties: false

**Filters**:

.. code-block:: yaml

   formatted_prompt:
     name: formatted_prompt
     description: Prompt demonstrating various Jinja2 filters for data formatting
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Hello {{name|title}}!
             Price: ${{price|round(2)}}
             Date: {{timestamp}}
             Items: {{items|join(', ')}}
           temperature: 0.7
           max_tokens: 200
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - name
             - price
             - timestamp
             - items
           optional: []
           properties:
             name:
               type: string
               description: "User's name to be formatted"
             price:
               type: number
               description: "Price value to be rounded"
             timestamp:
               type: string
               description: "Date/time string"
             items:
               type: array
               description: "List of items to be joined with commas"
           additionalProperties: false

**Macros**:

.. code-block:: yaml

   macro_prompt:
     name: macro_prompt
     description: Prompt demonstrating Jinja2 macros for reusable template components
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             {% macro greeting(name, formal=false) %}
             {% if formal %}
             Dear {{name}},
             {% else %}
             Hi {{name}}!
             {% endif %}
             {% endmacro %}
             
             {{greeting(user_name, is_formal)}}
             
             Your order details:
             {{greeting("Customer", true)}}
           temperature: 0.7
           max_tokens: 300
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - user_name
             - is_formal
           optional: []
           properties:
             user_name:
               type: string
               description: "User's name for personalized greeting"
             is_formal:
               type: boolean
               description: "Whether to use formal greeting style"
           additionalProperties: false

Custom Filters
~~~~~~~~~~~~~~

You can register custom Jinja2 filters:

.. code-block:: python

   from promptix import Promptix
   from promptix.core.components.template_renderer import TemplateRenderer

   def currency_filter(value, currency='USD'):
       return f"{value:.2f} {currency}"

   # Register custom filter
   renderer = TemplateRenderer()
   renderer.register_filter('currency', currency_filter)

   px = Promptix()
   # Use in templates: {{price|currency('EUR')}}

Variable Validation
-------------------

Promptix provides comprehensive variable validation:

Type Validation
~~~~~~~~~~~~~~~

.. code-block:: yaml

   typed_prompt:
     name: typed_prompt
     description: Prompt demonstrating comprehensive type validation for all data types
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Count: {{count}}
             Percentage: {{percentage}}%
             Status: {{is_active}}
             Tags: {{tags|join(', ')}}
             Config: {{config}}
           temperature: 0.7
           max_tokens: 300
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - count
             - percentage
             - is_active
             - tags
             - config
           optional: []
           properties:
             count:
               type: integer
               description: "Integer count value"
             percentage:
               type: number
               description: "Percentage value (allows both int and float)"
             is_active:
               type: boolean
               description: "Boolean status flag"
             tags:
               type: array
               description: "Array of tag strings"
             config:
               type: object
               description: "Configuration object with key-value pairs"
           additionalProperties: false

Range Validation
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   range_prompt:
     name: range_prompt
     description: Prompt demonstrating min/max validation for numeric values
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             User Profile:
             Age: {{age}} years old
             Test Score: {{score}}/100
           temperature: 0.7
           max_tokens: 200
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - age
             - score
           optional: []
           properties:
             age:
               type: integer
               description: "Person's age in years"
               validation:
                 min: 0
                 max: 150
             score:
               type: number
               description: "Test score as a percentage"
               validation:
                 min: 0.0
                 max: 100.0
           additionalProperties: false

Pattern Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   pattern_prompt:
     name: pattern_prompt
     description: Prompt demonstrating regex pattern validation for string formats
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Contact Information:
             Email: {{email}}
             Phone: {{phone}}
           temperature: 0.7
           max_tokens: 150
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - email
             - phone
           optional: []
           properties:
             email:
               type: string
               description: "Valid email address"
               validation:
                 pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
             phone:
               type: string
               description: "Valid phone number with optional country code"
               validation:
                 pattern: "^\\+?1?\\d{9,15}$"
           additionalProperties: false

Enum Validation
~~~~~~~~~~~~~~~

.. code-block:: yaml

   enum_prompt:
     name: enum_prompt
     description: Prompt demonstrating enum validation with predefined value lists
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Task Management:
             Priority: {{priority}}
             Status: {{status}}
           temperature: 0.7
           max_tokens: 200
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - priority
             - status
           optional: []
           properties:
             priority:
               type: string
               description: "Task priority level"
               enum: ["low", "medium", "high", "urgent"]
             status:
               type: string
               description: "Current task status"
               enum: ["draft", "pending", "approved", "rejected"]
           additionalProperties: false

Version Management
------------------

Best Practices for Versioning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Use semantic versioning concepts**:

.. code-block:: yaml

   my_prompt:
     versions:
       v1_0:     # Initial version
         prompt: "Basic template"
       v1_1:     # Minor improvements (backward compatible)
         prompt: "Improved template with better formatting"
       v2_0:     # Major changes (breaking changes)
         prompt: "Completely rewritten template"
         variables:  # Different variable structure
           new_var: {type: string, required: true}

2. **Document version changes**:

.. code-block:: yaml

   documented_prompt:
     versions:
       v1:
         prompt: "Original version"
         # comments: "Initial implementation"
       v2:
         prompt: "Updated version with {{new_feature}}"
         variables:
           new_feature: {type: string, required: true}
         # comments: "Added new_feature variable for customization"

Version Selection
~~~~~~~~~~~~~~~~~

.. code-block:: python

   px = Promptix()

   # Use latest version (default)
   result = px.render_prompt("my_prompt", **variables)

   # Use specific version
   result = px.render_prompt("my_prompt", version="v1", **variables)

   # Set default version globally
   from promptix.core.builder import PromptixBuilder
   px = PromptixBuilder().with_default_version("v2").build()

Configuration Management
------------------------

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use environment variables or ``.env`` files:

.. code-block:: bash

   # .env file
   PROMPTIX_PROMPT_FILE=./prompts/main.yaml
   PROMPTIX_LOG_LEVEL=DEBUG
   PROMPTIX_DEFAULT_VERSION=v2
   PROMPTIX_STORAGE_FORMAT=yaml

Programmatic Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from promptix.core.config import PromptixConfig
   from pathlib import Path

   # Custom configuration
   config = PromptixConfig(working_directory=Path("./custom_prompts"))
   
   # Use with Promptix
   px = Promptix(config=config)

Builder Pattern
~~~~~~~~~~~~~~~

.. code-block:: python

   from promptix.core.builder import PromptixBuilder

   px = (PromptixBuilder()
         .with_working_directory("./prompts")
         .with_default_version("v2")
         .with_validation_enabled(True)
         .with_caching_enabled(True)
         .build())

Integration Patterns
--------------------

Web Applications
~~~~~~~~~~~~~~~~

**Flask Integration**:

.. code-block:: python

   from flask import Flask, render_template_string
   from promptix import Promptix

   app = Flask(__name__)
   px = Promptix()

   @app.route('/email/<template_name>')
   def generate_email(template_name):
       try:
           email_content = px.render_prompt(
               template_name,
               user_name=request.args.get('name'),
               subject=request.args.get('subject')
           )
           return {'content': email_content}
       except Exception as e:
           return {'error': str(e)}, 400

**Django Integration**:

.. code-block:: python

   # settings.py
   PROMPTIX_CONFIG = {
       'working_directory': BASE_DIR / 'prompts',
       'default_version': 'v1'
   }

   # views.py
   from django.conf import settings
   from promptix import Promptix

   px = Promptix(working_directory=settings.PROMPTIX_CONFIG['working_directory'])

   def email_view(request):
       content = px.render_prompt('welcome_email', user=request.user.name)
       return HttpResponse(content)

API Development
~~~~~~~~~~~~~~~

**FastAPI Integration**:

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   from promptix import Promptix

   app = FastAPI()
   px = Promptix()

   class PromptRequest(BaseModel):
       template: str
       variables: dict
       version: str = None

   @app.post("/render")
   async def render_prompt(request: PromptRequest):
       try:
           result = px.render_prompt(
               request.template,
               version=request.version,
               **request.variables
           )
           return {"content": result}
       except Exception as e:
           raise HTTPException(status_code=400, detail=str(e))

Background Tasks
~~~~~~~~~~~~~~~~

**Celery Integration**:

.. code-block:: python

   from celery import Celery
   from promptix import Promptix

   app = Celery('tasks')
   px = Promptix()

   @app.task
   def send_notification(template_name, user_data):
       message = px.render_prompt(template_name, **user_data)
       # Send notification using your preferred service
       return message

AI Model Integration
--------------------

OpenAI Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from promptix import Promptix
   import openai

   px = Promptix()

   # Render prompt for OpenAI
   system_prompt = px.render_prompt(
       "ai_assistant_system",
       role="helpful coding assistant",
       rules=["be concise", "provide examples"]
   )

   user_prompt = px.render_prompt(
       "coding_question",
       language="Python",
       question="How do I handle exceptions?"
   )

   response = openai.ChatCompletion.create(
       model="gpt-3.5-turbo",
       messages=[
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": user_prompt}
       ]
   )

Anthropic Integration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import anthropic
   from promptix import Promptix

   px = Promptix()
   client = anthropic.Anthropic()

   prompt = px.render_prompt(
       "analysis_prompt",
       data_type="sales data",
       analysis_type="trend analysis",
       time_period="last quarter"
   )

   response = client.messages.create(
       model="claude-3-sonnet-20240229",
       max_tokens=1000,
       messages=[{"role": "user", "content": prompt}]
   )

Error Handling and Debugging
-----------------------------

Exception Types
~~~~~~~~~~~~~~~

Promptix provides specific exceptions for different error scenarios:

.. code-block:: python

   from promptix.core.exceptions import (
       PromptNotFoundError,      # Prompt doesn't exist
       RequiredVariableError,    # Missing required variable
       VariableValidationError,  # Invalid variable value
       TemplateRenderError,      # Template rendering failed
       ConfigurationError,       # Configuration issue
       StorageError             # File system error
   )

Comprehensive Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from promptix import Promptix
   from promptix.core.exceptions import PromptixError
   import logging

   logger = logging.getLogger(__name__)
   px = Promptix()

   def safe_render_prompt(template_name, **variables):
       try:
           return px.render_prompt(template_name, **variables)
       except PromptNotFoundError:
           logger.error(f"Template '{template_name}' not found")
           return None
       except RequiredVariableError as e:
           logger.error(f"Missing required variable: {e}")
           return None
       except VariableValidationError as e:
           logger.error(f"Invalid variable: {e}")
           return None
       except TemplateRenderError as e:
           logger.error(f"Template rendering failed: {e}")
           return None
       except PromptixError as e:
           logger.error(f"Promptix error: {e}")
           return None

Debugging Tips
~~~~~~~~~~~~~~

1. **Enable debug logging**:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)

2. **Validate prompts before use**:

.. code-block:: python

   # Check if prompt exists
   if px.prompt_exists("my_template"):
       result = px.render_prompt("my_template", **variables)

3. **Use the studio for testing**:

.. code-block:: bash

   promptix studio

Performance Optimization
------------------------

Caching
~~~~~~~

Enable caching for better performance:

.. code-block:: python

   from promptix.core.builder import PromptixBuilder

   px = (PromptixBuilder()
         .with_caching_enabled(True)
         .with_cache_size(1000)  # Number of templates to cache
         .build())

Batch Processing
~~~~~~~~~~~~~~~~

Process multiple prompts efficiently:

.. code-block:: python

   px = Promptix()

   # Batch render multiple templates
   templates = [
       ("welcome", {"name": "Alice"}),
       ("newsletter", {"date": "2024-01-01"}),
       ("reminder", {"task": "Review code"})
   ]

   results = []
   for template_name, variables in templates:
       result = px.render_prompt(template_name, **variables)
       results.append(result)

Lazy Loading
~~~~~~~~~~~~

Load prompts on demand:

.. code-block:: python

   px = PromptixBuilder().with_lazy_loading(True).build()

Testing
-------

Unit Testing
~~~~~~~~~~~~

.. code-block:: python

   import unittest
   from promptix import Promptix
   from unittest.mock import patch

   class TestPrompts(unittest.TestCase):
       def setUp(self):
           self.px = Promptix()

       def test_greeting_prompt(self):
           result = self.px.render_prompt("greeting", name="Test User")
           self.assertIn("Test User", result)
           self.assertIn("Hello", result)

       @patch('promptix.core.storage.manager.PromptManager')
       def test_prompt_loading(self, mock_manager):
           # Test with mocked data
           mock_manager.return_value.load_prompt.return_value = "Mocked prompt"
           result = self.px.render_prompt("test_prompt")
           self.assertEqual(result, "Mocked prompt")

Integration Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from promptix import Promptix
   import tempfile
   from pathlib import Path

   @pytest.fixture
   def temp_prompts():
       with tempfile.TemporaryDirectory() as temp_dir:
           prompt_file = Path(temp_dir) / "prompts.yaml"
           prompt_file.write_text("""
           test_prompt:
             versions:
               v1:
                 prompt: "Hello {{name}}"
                 variables:
                   name: {type: string, required: true}
           """)
           yield temp_dir

   def test_prompt_rendering(temp_prompts):
       px = Promptix(working_directory=temp_prompts)
       result = px.render_prompt("test_prompt", name="World")
       assert result == "Hello World"

Best Practices
--------------

Prompt Organization
~~~~~~~~~~~~~~~~~~~

1. **Group related prompts**:

.. code-block:: yaml

   # emails.yaml
   emails:
     welcome: {...}
     password_reset: {...}
     newsletter: {...}

   # notifications.yaml  
   notifications:
     push: {...}
     sms: {...}
     in_app: {...}

2. **Use descriptive names**:

.. code-block:: yaml

   # Good
   user_onboarding_welcome_email: {...}
   password_reset_confirmation: {...}
   
   # Avoid
   email1: {...}
   msg: {...}

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

1. **Validate user inputs**:

.. code-block:: python

   import html

   def safe_render(template_name, **variables):
       # Escape HTML in user inputs
       safe_variables = {
           k: html.escape(str(v)) if isinstance(v, str) else v
           for k, v in variables.items()
       }
       return px.render_prompt(template_name, **safe_variables)

2. **Use environment variables for sensitive data**:

.. code-block:: yaml

   api_request:
     versions:
       v1:
         prompt: |
           API Key: {{api_key}}
           Request: {{request_body}}
         variables:
           api_key:
             type: string
             required: true
             # Use: px.render_prompt("api_request", api_key=os.getenv("API_KEY"))

Maintenance
~~~~~~~~~~~

1. **Regular validation**:

.. code-block:: bash

   # Validate all prompts
   promptix validate

2. **Version cleanup**:

.. code-block:: python

   # Remove old versions periodically
   # Keep only latest 3 versions for each prompt

3. **Performance monitoring**:

.. code-block:: python

   import time
   from promptix.enhancements.logging import PerformanceLogger, get_logger

   logger = get_logger(__name__)

   with PerformanceLogger("prompt_rendering", logger):
       result = px.render_prompt("complex_template", **variables)

Next Steps
----------

* Explore the :doc:`api_reference` for detailed API documentation
* Check out advanced examples in the `GitHub repository <https://github.com/Nisarg38/promptix-python/tree/main/examples>`_
* Learn about :doc:`contributing` to help improve Promptix
* Join our community discussions for tips and best practices

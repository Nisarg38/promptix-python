Quick Start
===========

This guide will get you up and running with Promptix in just a few minutes.

Basic Usage
-----------

1. **Create a prompt file** (``prompts.yaml``):

.. code-block:: yaml

   # prompts.yaml
   greeting:
     name: greeting
     description: A friendly greeting prompt for user interaction
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Hello, {{name}}! How can I help you today?"
           temperature: 0.7
           max_tokens: 200
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
           last_modified: '2024-01-01'
           last_modified_by: Promptix Team
         schema:
           required:
             - name
           optional: []
           properties:
             name:
               type: string
               description: "The user's name"
           additionalProperties: false

   email_template:
     name: email_template
     description: A comprehensive email template for various communications
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Subject: {{subject}}
             
             Dear {{recipient}},
             
             {{message}}
             
             Best regards,
             {{sender}}
           temperature: 0.5
           max_tokens: 500
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
           last_modified: '2024-01-01'
           last_modified_by: Promptix Team
         schema:
           required:
             - subject
             - recipient
             - message
           optional:
             - sender
           properties:
             subject:
               type: string
               description: "Email subject line"
             recipient:
               type: string
               description: "Recipient's name"
             message:
               type: string
               description: "Main email content"
             sender:
               type: string
               description: "Sender's name"
               default: "The Team"
           additionalProperties: false

2. **Use in Python**:

.. code-block:: python

   from promptix import Promptix

   # Initialize Promptix (automatically finds prompts.yaml)
   px = Promptix()

   # Render a simple prompt
   greeting = px.render_prompt("greeting", name="Alice")
   print(greeting)
   # Output: Hello, Alice! How can I help you today?

   # Render a more complex prompt
   email = px.render_prompt(
       "email_template",
       subject="Welcome to our service",
       recipient="Bob",
       message="Thank you for signing up! We're excited to have you on board.",
       sender="Alice from Marketing"
   )
   print(email)

Template Features
-----------------

Promptix uses Jinja2 templating, which provides powerful features:

Variables
~~~~~~~~~

.. code-block:: yaml

   basic_prompt:
     name: basic_prompt
     description: A basic prompt demonstrating variable usage
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Hello {{name}}, you have {{count}} messages."
           temperature: 0.7
           max_tokens: 100
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - name
             - count
           optional: []
           properties:
             name:
               type: string
             count:
               type: integer
           additionalProperties: false

Conditionals
~~~~~~~~~~~~

.. code-block:: yaml

   conditional_prompt:
     name: conditional_prompt
     description: A prompt demonstrating conditional logic based on user status
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Hello {{name}}!
             {% if is_premium %}
             Welcome to your premium account.
             {% else %}
             Consider upgrading to premium for more features.
             {% endif %}
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
             - is_premium
           optional: []
           properties:
             name:
               type: string
             is_premium:
               type: boolean
           additionalProperties: false

Loops
~~~~~

.. code-block:: yaml

   list_prompt:
     name: list_prompt
     description: A prompt demonstrating loops for task lists
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Your tasks for today:
             {% for task in tasks %}
             - {{task}}
             {% endfor %}
           temperature: 0.7
           max_tokens: 300
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - tasks
           optional: []
           properties:
             tasks:
               type: array
               description: "List of tasks to display"
           additionalProperties: false

Usage:

.. code-block:: python

   result = px.render_prompt(
       "list_prompt",
       tasks=["Review code", "Write documentation", "Test features"]
   )

Filters
~~~~~~~

.. code-block:: yaml

   filtered_prompt:
     name: filtered_prompt
     description: A prompt demonstrating Jinja2 filters for data formatting
     versions:
       v1:
         is_live: true
         config:
           system_instruction: |
             Hello {{name|title}}!
             Your score is {{score|round(2)}}.
             Joined on: {{join_date}}  # Note: strftime requires custom filter registration
           temperature: 0.7
           max_tokens: 150
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - name
             - score
           optional:
             - join_date
           properties:
             name:
               type: string
             score:
               type: number
             join_date:
               type: string
           additionalProperties: false

Version Management
------------------

Promptix supports multiple versions of the same prompt:

.. code-block:: yaml

   product_description:
     name: product_description
     description: Product description with multiple versions for different formats
     versions:
       v1:
         is_live: false
         config:
           system_instruction: "{{product_name}} - {{price}}"
           temperature: 0.5
           max_tokens: 100
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
           last_modified: '2024-01-01'
           last_modified_by: Promptix Team
         schema:
           required:
             - product_name
             - price
           optional: []
           properties:
             product_name:
               type: string
             price:
               type: string
           additionalProperties: false
       v2:
         is_live: true
         config:
           system_instruction: |
             🎯 {{product_name}}
             💰 Price: {{price}}
             ⭐ Rating: {{rating}}/5
           temperature: 0.7
           max_tokens: 200
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-02'
           author: Promptix Team
           last_modified: '2024-01-02'
           last_modified_by: Promptix Team
         schema:
           required:
             - product_name
             - price
             - rating
           optional: []
           properties:
             product_name:
               type: string
             price:
               type: string
             rating:
               type: number
           additionalProperties: false

Usage:

.. code-block:: python

   # Use latest version (default)
   desc_v2 = px.render_prompt(
       "product_description",
       product_name="Awesome Widget",
       price="$29.99",
       rating=4.5
   )

   # Use specific version
   desc_v1 = px.render_prompt(
       "product_description",
       version="v1",
       product_name="Awesome Widget",
       price="$29.99"
   )

Error Handling
--------------

Promptix provides specific exceptions for common errors:

.. code-block:: python

   from promptix import Promptix
   from promptix.core.exceptions import (
       PromptNotFoundError,
       RequiredVariableError,
       VariableValidationError
   )

   px = Promptix()

   try:
       result = px.render_prompt("nonexistent_prompt")
   except PromptNotFoundError as e:
       print(f"Prompt not found: {e}")

   try:
       result = px.render_prompt("greeting")  # Missing required 'name'
   except RequiredVariableError as e:
       print(f"Missing required variable: {e}")

   try:
       result = px.render_prompt("greeting", name=123)  # Wrong type
   except VariableValidationError as e:
       print(f"Invalid variable type: {e}")

Configuration
-------------

You can configure Promptix behavior:

.. code-block:: python

   from promptix import Promptix
   from pathlib import Path

   # Custom prompt file location
   px = Promptix(working_directory="/path/to/prompts")

   # Using builder pattern
   from promptix.core.builder import PromptixBuilder

   px = (PromptixBuilder()
         .with_working_directory("/custom/path")
         .with_default_version("v2")
         .build())

Promptix Studio
---------------

Launch the visual interface for managing prompts:

.. code-block:: bash

   promptix studio

This opens a web interface where you can:

* View and edit prompts
* Test prompts with different variables
* Manage versions
* Import/export prompt collections

Command Line Interface
----------------------

Promptix provides a CLI for basic operations:

.. code-block:: bash

   # Show version
   promptix --version

   # Validate prompt file
   promptix validate

   # Render a prompt from command line
   promptix render greeting --name "Alice"

   # List all prompts
   promptix list

Environment Variables
--------------------

Configure Promptix using environment variables:

.. code-block:: bash

   # Set custom prompt file
   export PROMPTIX_PROMPT_FILE="/path/to/custom_prompts.yaml"

   # Set logging level
   export PROMPTIX_LOG_LEVEL="DEBUG"

   # Set log format
   export PROMPTIX_LOG_FORMAT="json"

Or use a ``.env`` file:

.. code-block:: bash

   # .env
   PROMPTIX_PROMPT_FILE=./my_prompts.yaml
   PROMPTIX_LOG_LEVEL=INFO
   OPENAI_API_KEY=your_api_key_here

Best Practices
--------------

1. **Organize prompts by purpose**:

.. code-block:: yaml

   # Group related prompts
   welcome_email:
     name: welcome_email
     description: Welcome email for new users
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Welcome {{user_name}}! ..."
           # ... config details

   password_reset_email:
     name: password_reset_email  
     description: Password reset email template
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Reset your password ..."
           # ... config details

   error_message:
     name: error_message
     description: User interface error message template
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Error: {{error_type}} - {{message}}"
           # ... config details

2. **Use descriptive variable names**:

.. code-block:: yaml

   # Good - descriptive property names
   user_profile:
     name: user_profile
     description: User profile display with clear variable names
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Profile: {{user_first_name}} created on {{account_creation_date}}"
           temperature: 0.7
           model: gpt-4o
           provider: openai
         schema:
           required:
             - user_first_name
             - account_creation_date
           properties:
             user_first_name:
               type: string
               description: "User's first name"
             account_creation_date:
               type: string
               description: "Date when account was created"

   # Avoid - unclear variable names
   user_data:
     name: user_data
     description: Example of poor variable naming (avoid this pattern)
     versions:
       v1:
         is_live: false
         config:
           system_instruction: "Data: {{n}} on {{d}}"
           temperature: 0.7
           model: gpt-4o
           provider: openai
         schema:
           required:
             - n
             - d
           properties:
             n:
               type: string
               description: "Unclear what 'n' represents"
             d:
               type: string
               description: "Unclear what 'd' represents"

3. **Add descriptions to variables**:

.. code-block:: yaml

   subscription_prompt:
     name: subscription_prompt
     description: Prompt with well-documented variables including enums
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Welcome {{user_name}}! Your {{user_tier}} account includes..."
           temperature: 0.7
           max_tokens: 200
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
         schema:
           required:
             - user_name
             - user_tier
           optional: []
           properties:
             user_name:
               type: string
               description: "User's display name for personalization"
             user_tier:
               type: string
               description: "User's subscription tier (free, pro, enterprise)"
               enum: ["free", "pro", "enterprise"]
           additionalProperties: false

4. **Version your prompts thoughtfully**:

.. code-block:: yaml

   # Use semantic versioning concepts
   evolving_prompt:
     name: evolving_prompt
     description: Example of thoughtful prompt versioning strategy
     versions:
       v1:
         is_live: false
         config:
           system_instruction: "Basic version of the prompt"
           temperature: 0.7
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-01'
           author: Promptix Team
           last_modified: '2024-01-01'
           last_modified_by: Promptix Team
         schema:
           required: []
           optional: []
           properties: {}
           additionalProperties: false
       v1_1:
         is_live: false
         config:
           system_instruction: "Minor improvement with better formatting"
           temperature: 0.7
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-01-15'
           author: Promptix Team
           last_modified: '2024-01-15'
           last_modified_by: Promptix Team
         schema:
           required: []
           optional: []
           properties: {}
           additionalProperties: false
       v2:
         is_live: true
         config:
           system_instruction: "Major rewrite with new functionality and {{feature}}"
           temperature: 0.8
           model: gpt-4o
           provider: openai
         metadata:
           created_at: '2024-02-01'
           author: Promptix Team
           last_modified: '2024-02-01'
           last_modified_by: Promptix Team
         schema:
           required:
             - feature
           optional: []
           properties:
             feature:
               type: string
               description: "New feature parameter for v2"
           additionalProperties: false

Next Steps
----------

Now that you've learned the basics:

* Read the full :doc:`user_guide` for advanced features
* Explore the :doc:`api_reference` for detailed API documentation
* Check out the `examples directory <https://github.com/Nisarg38/promptix-python/tree/main/examples>`_ for more use cases
* Learn about :doc:`contributing` if you'd like to help improve Promptix

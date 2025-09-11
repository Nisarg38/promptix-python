Promptix Documentation
=====================

Welcome to Promptix, a simple yet powerful library for managing and using prompts locally with Promptix Studio.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide
   api_reference
   contributing
   changelog

Overview
--------

Promptix is designed to make prompt management easy and efficient for developers working with AI models. Whether you're building chatbots, content generation tools, or any AI-powered application, Promptix provides the tools you need to manage your prompts effectively.

Key Features
------------

* **Local Prompt Management**: Store and organize your prompts locally in YAML files
* **Template System**: Use Jinja2 templating for dynamic prompt generation
* **Version Control**: Track different versions of your prompts
* **AI Model Integration**: Built-in adapters for popular AI services (OpenAI, Anthropic)
* **Studio Interface**: Visual prompt management with Streamlit-based studio
* **Type Safety**: Full type hints and mypy support
* **Extensible**: Plugin architecture for custom functionality

Quick Example
-------------

.. code-block:: python

   from promptix import Promptix

   # Initialize Promptix
   px = Promptix()

   # Render a prompt with variables
   result = px.render_prompt(
       "greeting_template",
       name="Alice",
       time_of_day="morning"
   )
   
   print(result)  # "Good morning, Alice! How can I help you today?"

Installation
------------

Install Promptix using pip:

.. code-block:: bash

   pip install promptix

For development installation with all dependencies:

.. code-block:: bash

   pip install promptix[dev]

Getting Started
---------------

1. **Create a prompt file** (``prompts.yaml``):

.. code-block:: yaml

   greeting_template:
     name: greeting_template
     description: A simple greeting prompt for welcoming users
     versions:
       v1:
         is_live: true
         config:
           system_instruction: "Hello, {{name}}! Welcome to our service."
           temperature: 0.7
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
             - name
           optional: []
           properties:
             name:
               type: string
               description: "The user's name"
           additionalProperties: false

2. **Use in your Python code**:

.. code-block:: python

   from promptix import Promptix
   
   px = Promptix()
   greeting = px.render_prompt("greeting_template", name="Bob")
   print(greeting)  # "Hello, Bob! Welcome to our service."

3. **Launch Promptix Studio** for visual management:

.. code-block:: bash

   promptix studio

API Reference
-------------

The complete API reference is available in the :doc:`api_reference` section.

Main Classes
~~~~~~~~~~~~

* :class:`promptix.Promptix` - Main interface for prompt management
* :class:`promptix.core.builder.PromptixBuilder` - Builder pattern for configuration
* :class:`promptix.core.storage.PromptManager` - Low-level prompt storage management

Contributing
------------

We welcome contributions! Please see our :doc:`contributing` guide for details on:

* Setting up the development environment
* Code style and quality standards
* Testing requirements
* Pull request process

License
-------

Promptix is released under the MIT License. See the `LICENSE <https://github.com/Nisarg38/promptix-python/blob/main/LICENSE>`_ file for details.

Support
-------

* **Issues**: https://github.com/Nisarg38/promptix-python/issues
* **Discussions**: https://github.com/Nisarg38/promptix-python/discussions
* **Email**: support@promptix.io  # replace or confirm this inbox exists

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

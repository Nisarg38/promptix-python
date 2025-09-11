API Reference
=============

This section contains the complete API reference for Promptix.

Core Module
-----------

.. automodule:: promptix
   :members:
   :undoc-members:
   :show-inheritance:

Main Classes
~~~~~~~~~~~~

Promptix
~~~~~~~~

.. autoclass:: promptix.Promptix
   :members:
   :undoc-members:
   :show-inheritance:

PromptixBuilder
~~~~~~~~~~~~~~~

.. autoclass:: promptix.core.builder.PromptixBuilder
   :members:
   :undoc-members:
   :show-inheritance:

Storage Management
------------------

PromptManager
~~~~~~~~~~~~~

.. autoclass:: promptix.core.storage.PromptManager
   :members:
   :undoc-members:
   :show-inheritance:

Loaders
~~~~~~~

.. automodule:: promptix.core.storage.loaders
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

PromptixConfig
~~~~~~~~~~~~~~

.. autoclass:: promptix.core.config.PromptixConfig
   :members:
   :undoc-members:
   :show-inheritance:

Components
----------

Template Renderer
~~~~~~~~~~~~~~~~~

.. autoclass:: promptix.core.components.template_renderer.TemplateRenderer
   :members:
   :undoc-members:
   :show-inheritance:

Variable Validator
~~~~~~~~~~~~~~~~~~

.. autoclass:: promptix.core.components.variable_validator.VariableValidator
   :members:
   :undoc-members:
   :show-inheritance:

Version Manager
~~~~~~~~~~~~~~~

.. autoclass:: promptix.core.components.version_manager.VersionManager
   :members:
   :undoc-members:
   :show-inheritance:

Model Config Builder
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: promptix.core.components.model_config_builder.ModelConfigBuilder
   :members:
   :undoc-members:
   :show-inheritance:

Prompt Loader
~~~~~~~~~~~~~

.. autoclass:: promptix.core.components.prompt_loader.PromptLoader
   :members:
   :undoc-members:
   :show-inheritance:

Adapters
--------

Base Adapter
~~~~~~~~~~~~

.. autoclass:: promptix.core.adapters._base.ModelAdapter
   :members:
   :undoc-members:
   :show-inheritance:

OpenAI Adapter
~~~~~~~~~~~~~~

.. autoclass:: promptix.core.adapters.openai.OpenAIAdapter
   :members:
   :undoc-members:
   :show-inheritance:

Anthropic Adapter
~~~~~~~~~~~~~~~~~

.. autoclass:: promptix.core.adapters.anthropic.AnthropicAdapter
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. automodule:: promptix.core.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Base Exception
~~~~~~~~~~~~~~

.. autoclass:: promptix.core.exceptions.PromptixError
   :members:
   :undoc-members:
   :show-inheritance:

Specific Exceptions
~~~~~~~~~~~~~~~~~~~

.. autoclass:: promptix.core.exceptions.PromptNotFoundError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: promptix.core.exceptions.RequiredVariableError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: promptix.core.exceptions.VariableValidationError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: promptix.core.exceptions.TemplateRenderError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: promptix.core.exceptions.ConfigurationError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: promptix.core.exceptions.StorageError
   :members:
   :undoc-members:
   :show-inheritance:

Enhancements
------------

Logging
~~~~~~~

.. automodule:: promptix.enhancements.logging
   :members:
   :undoc-members:
   :show-inheritance:

Tools
-----

CLI
~~~

.. automodule:: promptix.tools.cli
   :members:
   :undoc-members:
   :show-inheritance:

Studio
~~~~~~

.. automodule:: promptix.tools.studio.app
   :members:
   :undoc-members:
   :show-inheritance:

Data Management
~~~~~~~~~~~~~~~

.. automodule:: promptix.tools.studio.data
   :members:
   :undoc-members:
   :show-inheritance:

Studio Pages
~~~~~~~~~~~~

Dashboard
*********

.. automodule:: promptix.tools.studio.pages.dashboard
   :members:
   :undoc-members:
   :show-inheritance:

Library
*******

.. automodule:: promptix.tools.studio.pages.library
   :members:
   :undoc-members:
   :show-inheritance:

Playground
**********

.. automodule:: promptix.tools.studio.pages.playground
   :members:
   :undoc-members:
   :show-inheritance:

Version
*******

.. automodule:: promptix.tools.studio.pages.version
   :members:
   :undoc-members:
   :show-inheritance:

Type Definitions
----------------

The following sections document the type definitions used throughout Promptix.

Common Types
~~~~~~~~~~~~

.. code-block:: python

   from typing import Dict, List, Optional, Union, Any
   from pathlib import Path

   # Configuration types
   ConfigDict = Dict[str, Any]
   VariableDict = Dict[str, Any]
   
   # File path types
   PathLike = Union[str, Path]
   
   # Template types
   TemplateData = Dict[str, Any]
   VersionData = Dict[str, Any]
   
   # Model adapter types
   MessageList = List[Dict[str, str]]
   ToolsList = List[Dict[str, Any]]

Version Information
-------------------

.. autodata:: promptix.__version__
   :annotation: str

   The current version of Promptix.

Package Metadata
----------------

.. autodata:: promptix.__author__
   :annotation: str

   The package author(s).

.. autodata:: promptix.__email__
   :annotation: str

   Contact email for the package maintainers.

.. autodata:: promptix.__license__
   :annotation: str

   The package license.

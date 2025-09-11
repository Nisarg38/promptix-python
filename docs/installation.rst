Installation
============

This guide covers how to install Promptix in various environments.

Quick Install
-------------

The simplest way to install Promptix is using pip:

.. code-block:: bash

   pip install promptix

This will install the core Promptix library with minimal dependencies.

Development Installation
------------------------

For development or if you want all optional features:

.. code-block:: bash

   # Install with development dependencies
   pip install promptix[dev]

   # Or install from source
   git clone https://github.com/Nisarg38/promptix-python.git
   cd promptix-python
   pip install -e ".[dev]"

Optional Dependencies
--------------------

Promptix offers several optional dependency groups:

Documentation Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

For building documentation:

.. code-block:: bash

   pip install promptix[docs]

Security Tools
~~~~~~~~~~~~~~

For security scanning and analysis:

.. code-block:: bash

   pip install promptix[security]

All Dependencies
~~~~~~~~~~~~~~~~

To install everything:

.. code-block:: bash

   pip install promptix[dev,docs,security]

Requirements
------------

System Requirements
~~~~~~~~~~~~~~~~~~~

* **Python**: 3.9 or higher
* **Operating System**: Linux, macOS, or Windows
* **Memory**: Minimum 512MB RAM (1GB+ recommended)
* **Disk Space**: ~50MB for installation

Python Dependencies
~~~~~~~~~~~~~~~~~~~

Core dependencies (automatically installed):

* ``streamlit`` >= 1.29.0 - For the Studio interface
* ``jinja2`` >= 3.0.0 - Template engine
* ``python-dotenv`` >= 0.19.0 - Environment variable management
* ``pyyaml`` >= 6.0.0 - YAML parsing
* ``jsonschema`` >= 4.0.0 - Schema validation

Virtual Environment
-------------------

We strongly recommend using a virtual environment:

Using venv (Python 3.9+)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   python -m venv promptix-env
   
   # Activate (Linux/macOS)
   source promptix-env/bin/activate
   
   # Activate (Windows)
   promptix-env\Scripts\activate
   
   # Install Promptix
   pip install promptix

Using conda
~~~~~~~~~~~

.. code-block:: bash

   # Create environment
   conda create -n promptix python=3.11
   
   # Activate environment
   conda activate promptix
   
   # Install Promptix
   pip install promptix

Using poetry
~~~~~~~~~~~~

.. code-block:: bash

   # Create new project
   poetry new my-promptix-project
   cd my-promptix-project
   
   # Add Promptix
   poetry add promptix
   
   # For development
   poetry add promptix[dev] --group dev

Docker Installation
-------------------

You can also run Promptix in a Docker container:

.. code-block:: bash

   # Using official Python image
   # Using official Python image
   # Step 1: Start a container
   docker run -it python:3.11-slim bash

   # Step 2: Inside the container, install Promptix
   pip install promptix

Or create a Dockerfile:

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install Promptix
   RUN pip install promptix
   
   # Copy your project files
   COPY . .
   
   CMD ["python", "your_script.py"]

Verification
------------

To verify your installation:

.. code-block:: python

   import promptix
   print(f"Promptix version: {promptix.__version__}")
   
   # Test basic functionality
   px = promptix.Promptix()
   print("Installation successful!")

Or from the command line:

.. code-block:: bash

   promptix --version

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Error**

If you get import errors, ensure you're in the correct virtual environment and Promptix is installed:

.. code-block:: bash

   pip list | grep promptix

**Permission Errors**

On some systems, you might need to use ``--user`` flag:

.. code-block:: bash

   pip install --user promptix

**Outdated pip**

Update pip to the latest version:

.. code-block:: bash

   pip install --upgrade pip

Platform-Specific Notes
~~~~~~~~~~~~~~~~~~~~~~~

**Windows**

* Use Command Prompt or PowerShell
* Ensure Python is in your PATH
* Consider using Windows Subsystem for Linux (WSL) for better compatibility

**macOS**

* Use Homebrew Python if experiencing issues with system Python
* Xcode Command Line Tools may be required for some dependencies

**Linux**

* Install ``python3-dev`` package if compilation errors occur
* Use package manager Python when possible

Getting Help
------------

If you encounter issues:

1. Check our `FAQ <https://github.com/Nisarg38/promptix-python/wiki/FAQ>`_
2. Search existing `issues <https://github.com/Nisarg38/promptix-python/issues>`_
3. Create a new issue with:
   - Your operating system and Python version
   - Complete error message
   - Steps to reproduce the problem

Next Steps
----------

After installation, check out:

* :doc:`quickstart` - Get started with basic usage
* :doc:`user_guide` - Comprehensive usage guide
* :doc:`api_reference` - Complete API documentation

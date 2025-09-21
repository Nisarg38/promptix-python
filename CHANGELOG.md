# Changelog

## [0.1.16] - 2025-09-21

### 🚀 **Major Development Infrastructure & Documentation Overhaul**

This release significantly enhances the development workflow, documentation infrastructure, and project maintainability with comprehensive tooling and automation improvements.

### Added

#### **Development Infrastructure & Automation**
- **Comprehensive Makefile**: Added extensive development commands covering installation, testing, code quality, security auditing, documentation generation, build/release, environment management, Git helpers, Docker targets, and debugging utilities
- **Pre-commit Hooks Suite**: Implemented comprehensive pre-commit configuration with hooks for:
  - Code formatting (Black), import sorting (isort), linting (flake8)
  - Type checking (mypy), docstring style (pydocstyle)  
  - Security scanning (bandit, safety), dependency security scanning
  - Code complexity checking, spelling, YAML/Markdown formatting
  - Python issue detection and requirements file validation
- **Flake8 Configuration**: Added standardized linting rules with specific ignores for certain files
- **Dependabot Integration**: Automated dependency updates with scheduled maintenance, reviewers, commit message prefixes, and organized dependency groups

#### **CI/CD Pipeline Enhancements**
- **Expanded Testing Matrix**: Extended CI to support more Python versions (3.9-3.13) and operating systems (Ubuntu, Windows, macOS)
- **Concurrency Management**: Added concurrency settings to optimize CI resource usage
- **Performance & Integration Testing**: Dedicated CI jobs for performance benchmarks and integration testing
- **Enhanced Workflow**: Updated setup-python action, added comprehensive status checks, and final job status verification

#### **Documentation Infrastructure**
- **Complete Documentation Suite**: Comprehensive Sphinx-based documentation including:
  - **API Reference**: Full API documentation with detailed class and method references
  - **Installation Guide**: Multi-environment installation instructions with troubleshooting
  - **Quick Start Guide**: Step-by-step getting started tutorial with practical examples
  - **User Guide**: Comprehensive guide covering project structure, advanced features, and best practices
- **Custom Styling**: Enhanced documentation appearance with custom CSS for improved readability, code block styling, API documentation spacing, and professional theming
- **Sphinx Configuration**: Complete Sphinx setup with extensions, themes, and output configurations for HTML, LaTeX, and other formats

#### **Project Standards & Guidelines**
- **Contributing Guidelines**: Comprehensive CONTRIBUTING.md with development setup, code standards, testing practices, security guidelines, and pull request processes
- **AI Agent Coding Directives**: Established coding standards for clarity, readability, modularity, organization, documentation, testing, and data structure best practices

#### **Enhanced Logging System**
- **Structured Logging**: Upgraded logging module with JSON output support, configurable log levels, multiple output formats, context injection, and performance monitoring capabilities

### Changed
- **Version Update**: Bumped version from 0.1.15 to 0.1.16 across all configuration files
- **Development Dependencies**: Expanded pyproject.toml with comprehensive tooling dependencies for testing, linting, documentation, security, and code analysis
- **Documentation Structure**: Reorganized and enhanced documentation hierarchy with improved navigation and content organization

### Technical Improvements
- **Code Quality Enforcement**: Automated code quality checks through pre-commit hooks and CI pipeline
- **Security Posture**: Enhanced security scanning with bandit, safety, and dependency vulnerability detection
- **Development Experience**: Streamlined development workflow with Makefile targets and automated tooling
- **Documentation Generation**: Automated documentation building and publishing pipeline
- **Testing Infrastructure**: Improved test coverage tracking and performance monitoring
- **Dependency Management**: Automated dependency updates and security vulnerability monitoring

### Developer Experience Enhancements
- **Simplified Workflow**: One-command setup and development operations through Makefile
- **Comprehensive Tooling**: Integrated code formatting, linting, type checking, and security scanning
- **Enhanced Documentation**: Professional-grade documentation with API references and guides
- **Automated Quality Checks**: Pre-commit hooks ensure code quality before commits
- **Multi-environment Support**: Consistent development experience across different platforms

### Infrastructure & Maintenance
- **Automated Updates**: Dependabot configuration for seamless dependency management
- **Quality Metrics**: Integrated code coverage, complexity analysis, and performance benchmarks
- **Cross-platform Compatibility**: Enhanced CI testing across multiple Python versions and operating systems
- **Security Scanning**: Comprehensive security analysis and vulnerability detection


## [0.1.15] - 2025-09-10

### Added
- README in `tests/` directory detailing how to run tests and testing conventions

### Changed
- Test performance thresholds updated to be CI-friendly
- Integration tests use working Promptix implementation by default

### Fixed
- All tests passing consistently against source code (via `PYTHONPATH=src`)


## [0.1.14] - 2025-09-10

### 🧹 **Code Quality & Architecture Enhancements**

This release focuses on significant code quality improvements, reducing technical debt, and enhancing maintainability without breaking existing functionality.

### Added
- **Centralized Validation Engine** (`src/promptix/core/validation.py`)
  - Unified validation system consolidating scattered validation logic
  - Pluggable validation strategies for different validation types
  - Support for variable, structural, builder, and custom validation patterns
  - Extensible architecture for future validation needs
  - Enhanced error reporting with contextual information

### Changed
- **Schema Validation Consolidation**
  - Replaced scattered validation logic across multiple files with centralized engine
  - Updated `base.py`, `storage/loaders.py`, and `components/variable_validator.py` to use unified validation
  - Improved error handling and consistency across validation operations
  - Maintained backward compatibility through wrapper classes

- **Duplicate Code Elimination in Adapters**
  - Enhanced base adapter class (`adapters/_base.py`) with comprehensive common functionality
  - Extracted ~60% duplicate code from OpenAI and Anthropic adapters
  - Added common parameter validation, tool handling, and schema manipulation utilities
  - Reduced total adapter code by ~200 lines while improving consistency

- **Enhanced Type Annotations**
  - Added comprehensive type hints throughout the codebase
  - Improved IDE support and static analysis capabilities
  - Enhanced documentation through better type information
  - Better development experience with enhanced autocomplete and error detection

### Improved
- **Function Structure**: Validated that functions are appropriately sized (most under 30 lines)
- **Code Maintainability**: Significantly improved through centralized validation and reduced duplication
- **Developer Experience**: Better IDE support, clearer error messages, easier debugging
- **Architecture**: More consistent patterns and better separation of concerns

### Technical Improvements
- **Reduced Code Duplication**: Eliminated redundant patterns in adapter classes
- **Centralized Logic**: Unified validation operations for better maintainability  
- **Type Safety**: Enhanced type checking and IDE support throughout codebase
- **Error Handling**: More consistent and informative error messages
- **Code Coverage**: All tests pass (65/65) with maintained functionality

### Backward Compatibility
- All existing APIs remain unchanged and fully functional
- Existing validation behavior preserved through compatibility wrappers
- No breaking changes to public interfaces
- Legacy code continues to work without modifications

### Testing
- All 65 tests pass successfully
- 54% test coverage maintained
- Validation improvements tested across all scenarios
- No regressions in existing functionality

## [0.1.13] - 2025-09-09

### 🏗️ **Architecture Improvements**

### Added
- **Dependency Injection System**: Implemented comprehensive DI container (`container.py`) for better testability and modularity
  - Support for singleton, factory, and transient service lifetimes
  - Scoped containers for isolated testing
  - Automatic dependency resolution with type checking
- **Focused Component Architecture**: Broke down monolithic classes into single-responsibility components
  - `PromptLoader`: Handles prompt loading and caching logic
  - `VariableValidator`: Manages schema validation and type checking
  - `TemplateRenderer`: Processes Jinja2 template rendering
  - `VersionManager`: Manages prompt versioning logic
  - `ModelConfigBuilder`: Builds model configurations for different providers
- **Standardized Exception Hierarchy**: Comprehensive custom exception system (`exceptions.py`)
  - Base `PromptixError` class with structured error details
  - Specialized exceptions for different error categories (validation, storage, tools, etc.)
  - Enhanced error messages with contextual information and debugging details
  - Support for error chaining and detailed error reporting

### Changed
- **Refactored Main Classes**: `Promptix` and `PromptixBuilder` classes now use dependency injection
  - Maintained backward compatibility while improving internal structure
  - Better separation of concerns following Single Responsibility Principle
  - Enhanced testability through dependency injection
- **Improved Error Handling**: Consistent error handling patterns across the entire codebase
  - All components now use standardized exceptions
  - Better error context and debugging information
  - Graceful error recovery where appropriate

### Technical Improvements
- **Better Testability**: All components can be easily mocked and tested in isolation
- **Improved Maintainability**: Clear separation of responsibilities makes code easier to understand and modify  
- **Enhanced Modularity**: Components can be replaced or extended without affecting other parts of the system
- **Type Safety**: Enhanced type checking throughout the dependency injection system
- **Logging Integration**: Better logging integration across all components

### Backward Compatibility
- All existing public APIs remain unchanged
- Existing code will continue to work without modifications
- Internal refactoring does not affect end-user experience

### Developer Experience
- Cleaner, more maintainable codebase
- Better error messages with actionable information
- Improved debugging capabilities through structured error details
- Enhanced testing infrastructure for better reliability

## [0.1.12] - 2025-01-19

### 🚨 BREAKING CHANGES
- **Minimum Python version updated**: Now requires Python 3.9+ (previously 3.8+)

### Fixed
- Fixed `TypeError: 'type' object is not subscriptable` error when running on Python 3.8
- Updated type annotations in `config.py` to use `List[Type]` instead of `list[Type]` for better compatibility
- Updated CI/CD workflows to use Python 3.9+ for testing and publishing

### Changed
- Minimum Python version requirement updated from 3.8 to 3.9
- Removed Python 3.8 from supported versions in package classifiers
- Updated Black formatter target version to py39

## [0.1.11] - 2025-01-19

### 🚨 BREAKING CHANGES
- **JSON format is no longer supported**: All prompt storage now uses YAML format exclusively
- Users with existing `prompts.json` files must migrate to `prompts.yaml`

### Added
- Centralized configuration management with `PromptixConfig` class
- Environment variable support for configuration (e.g., `PROMPTIX_LOG_LEVEL`, `PROMPTIX_STORAGE_FORMAT`)
- Enhanced error messages with clear migration guidance for JSON format
- Automatic detection of unsupported JSON files with helpful migration instructions
- `check_for_unsupported_files()` method to identify JSON files that need migration

### Changed
- **BREAKING**: Completely removed JSON format support for prompt storage
- Standardized on YAML as the sole storage format (.yaml, .yml extensions only)
- Updated Promptix Studio to work exclusively with YAML format
- Improved configuration system with centralized path management
- Enhanced error handling with actionable user guidance
- Updated all examples and documentation to reference YAML instead of JSON
- Improved storage architecture with simplified, maintainable code

### Deprecated
- N/A (JSON format support has been completely removed)

### Removed
- `JSONPromptLoader` class and all JSON handling code
- Support for `prompts.json` files (users must migrate to `prompts.yaml`)
- Dual-format confusion by eliminating JSON/YAML mixed support
- Legacy JSON fallback mechanisms in Promptix Studio

### Fixed
- Version consistency: synchronized version 0.1.11 across `pyproject.toml` and `__init__.py`
- Storage format confusion by eliminating dual YAML/JSON support
- Configuration management with centralized, environment-aware settings
- Error messages now provide clear, actionable migration guidance

### Migration Guide
**For users with existing `prompts.json` files:**

1. **Rename your file**: `mv prompts.json prompts.yaml`
2. **Verify YAML syntax**: Ensure your content follows proper YAML format
3. **Test your setup**: Run your application to verify the migration worked
4. **Remove old file**: Delete the old `prompts.json` file

**Error messages will guide you through this process if JSON files are detected.**

### Technical Improvements
- Simplified codebase by removing JSON loader complexity
- Better separation of concerns with centralized configuration
- Enhanced logging and error reporting
- Improved test coverage for YAML-only functionality
- More maintainable storage architecture

## [0.1.10] - 2025-03-12

### Added
- Enhanced tools_template functionality: Variables set with `.with_var()` are now accessible in tools_template for conditional tool selection
- Added example showcasing conditional tools selection based on variables
- Added comprehensive tests for conditional tools feature

## [0.1.9] - 2025-03-03

## Changed
- Promptix Studio Updated 
- Updated README

## [0.1.8] - 2025-03-03

## Changed
- Updated PyProject.toml and Added MANIFEST.in 
- Making the Promptix Studio fully functional.

## [0.1.7] - 2025-03-02

### Changed
- Updated code with latest improvements
- Fixed minor issues from previous release

## [0.1.6] - 2025-03-02

### Added
- Improved Promptix Studio with enhanced user interface and functionality
- Updated License with additional clarifications

## [0.1.5] - 2025-02-27

### Added
- Improved documentation for builder patterns
- Enhanced error messaging for template validation
- Additional examples in README.md

### Changed
- Refined API interface for better developer experience
- Optimized template rendering for better performance

## [0.1.4] - 2025-02-02

### Added
- Builder pattern support for creating model configurations
- New builder classes for CustomerSupport and CodeReview templates
- Integration with both OpenAI and Anthropic APIs through builders
- Comprehensive test suite for builder pattern functionality
- Example implementations showing builder pattern usage

### Changed
- Enhanced model configuration preparation with builder pattern
- Improved documentation with builder pattern examples
- Added type hints and validation for builder methods

## [0.1.3] - 2025-02-26

### Added
- OpenAI integration support with prepare_model_config functionality
- Test suite for OpenAI integration features
- Example implementation for OpenAI chat completions

### Changed
- Enhanced model configuration preparation with better validation
- Improved error handling for invalid memory formats
- Updated documentation with OpenAI integration examples

## [0.1.2] - 2025-02-19

### Added
- New DungeonMaster template for RPG scenario generation
- Comprehensive test suite for complex template features
- Support for nested object handling in templates
- Enhanced template validation for complex data structures

### Fixed
- Fixed custom_data handling in templates
- Improved test coverage for complex scenarios
- Updated template validation for optional fields

## [0.1.1] - 2025-01-20

### Added
- Enhanced schema validation with warning system for missing fields
- Support for optional fields with default values
- Improved handling of nested fields in templates
- Added comprehensive test fixtures and test configuration

### Changed
- Schema validation now warns instead of failing for missing required fields
- Optional fields are now initialized with appropriate default values
- Improved test environment setup with proper fixtures handling

### Fixed
- Fixed issue with template rendering for undefined optional fields
- Fixed handling of custom_data and nested fields
- Fixed test environment cleanup and prompts.json handling

## [0.1.0] - 2025-01-19

### Added
- Initial release of Promptix Library
- Core functionality:
  - Prompt management with versioning support
  - Streamlit-based Studio UI for prompt management
  - JSON-based storage system for prompts
  - Support for multiple prompt versions with live/draft states

### Features
- **Promptix Studio**:
  - Interactive dashboard with prompt statistics
  - Prompt library with search functionality
  - Version management for each prompt
  - Playground for testing prompts
  - Modern, responsive UI with Streamlit

- **Core Library**:
  - Simple API for prompt management
  - Version control for prompts
  - Support for system messages and variables
  - Easy integration with existing projects

### Dependencies
- Python >=3.9
- Streamlit >=1.29.0
- Python-dotenv >=1.0.0

### Documentation
- Basic usage examples in `examples/` directory
- README with installation and getting started guide 
# Changelog

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
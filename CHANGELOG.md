# Changelog

## [0.1.9] - 2025-03-03

## Changed
- Promptix Studio Updated 
- Updated README

## [0.1.8] - 2025-03-03

## Changed
- Updated PyProject.toml and Added MANIFEST.in 
- Making the Promptix Studio fully functional.

## [0.1.7] - 2024-05-18

### Changed
- Updated code with latest improvements
- Fixed minor issues from previous release

## [0.1.6] - 2024-05-17

### Added
- Improved Promptix Studio with enhanced user interface and functionality
- Updated License with additional clarifications

## [0.1.5] - 2024-05-15

### Added
- Improved documentation for builder patterns
- Enhanced error messaging for template validation
- Additional examples in README.md

### Changed
- Refined API interface for better developer experience
- Optimized template rendering for better performance

## [0.1.4] - 2024-02-02

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

## [0.1.3] - 2024-01-26

### Added
- OpenAI integration support with prepare_model_config functionality
- Test suite for OpenAI integration features
- Example implementation for OpenAI chat completions

### Changed
- Enhanced model configuration preparation with better validation
- Improved error handling for invalid memory formats
- Updated documentation with OpenAI integration examples

## [0.1.2] - 2024-03-19

### Added
- New DungeonMaster template for RPG scenario generation
- Comprehensive test suite for complex template features
- Support for nested object handling in templates
- Enhanced template validation for complex data structures

### Fixed
- Fixed custom_data handling in templates
- Improved test coverage for complex scenarios
- Updated template validation for optional fields

## [0.1.1] - 2024-01-20

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

## [0.1.0] - 2024-01-19

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
- Python >=3.8
- Streamlit >=1.29.0
- Python-dotenv >=1.0.0

### Documentation
- Basic usage examples in `examples/` directory
- README with installation and getting started guide 
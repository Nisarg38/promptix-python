# Changelog

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
- Initial release
- Basic prompt template management
- JSON-based prompt storage
- Version control for prompts
- Schema validation
- Jinja2 template support
- Basic CLI tools
- Promptix Studio integration

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

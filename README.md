# Promptix 🧩

[![PyPI version](https://badge.fury.io/py/promptix.svg)](https://badge.fury.io/py/promptix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptix.svg)](https://pypi.org/project/promptix/)
[![PyPI Downloads](https://static.pepy.tech/badge/promptix)](https://pepy.tech/projects/promptix)

**Promptix** is a powerful, local-first prompt management system that brings **version control**, **dynamic templating**, and a **visual studio interface** to your LLM workflows.

## 🌟 Why Promptix?

Managing prompts across multiple applications, models, and use cases can quickly become chaotic. Promptix brings order to this chaos:

- **No more prompt spaghetti** in your codebase
- **Version and test prompts** with live/draft states
- **Dynamically customize prompts** based on context variables
- **Edit and manage** through a friendly UI with Promptix Studio
- **Seamlessly integrate** with OpenAI, Anthropic, and other providers

## ✨ Key Features

### 🎯 Dynamic Prompt Generation
Create versatile prompts with Promptix's templating system, allowing for context-aware adjustments:

```python
support_prompt = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    # These variables dynamically modify the prompt
    department="Billing",
    customer_tier="Premium",
    issue_type="refund request",
    agent_name="Alex"
)
```

### 🔄 Version Control Built-in
Keep track of prompt iterations and test new versions without breaking production:

```python
# Get the latest live version (for production)
live_prompt = Promptix.get_prompt("CustomerSupport")

# Test a new draft version in development
draft_prompt = Promptix.get_prompt(
    prompt_template="CustomerSupport", 
    version="v2"
)
```

### 🎨 Promptix Studio
Manage prompts through a clean web interface by simply running:

```bash
promptix studio
```

### 🛠️ Fluent Builder API
Create sophisticated prompt configurations with an intuitive builder pattern:

```python
config = (
    Promptix.builder("CustomerSupport")
    .with_customer_name("Jane Doe")
    .with_department("Technical Support")
    .with_priority("high")
    .with_tool("ticket_history")  # Enable specific tools
    .with_tool_parameter("ticket_history", "max_tickets", 5)
    .with_memory(conversation_history)
    .build()
)
```

### 🤖 Multi-Provider Support
Send your prompts to any LLM provider while maintaining a consistent interface:

```python
# OpenAI integration
openai_config = Promptix.builder("AgentPrompt").build()
openai_response = openai_client.chat.completions.create(**openai_config)

# Anthropic integration
anthropic_config = (
    Promptix.builder("AgentPrompt")
    .for_client("anthropic")
    .build()
)
anthropic_response = anthropic_client.messages.create(**anthropic_config)
```

### 🧠 Context-Aware Prompting
Adapt prompts based on dynamic conditions to create truly intelligent interactions:

```python
# Prompt adapts based on user context
prompt = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    customer_history_length="long" if customer.interactions > 5 else "short",
    sentiment="frustrated" if sentiment_score < 0.3 else "neutral",
    technical_level=customer.technical_proficiency
)
```

## 🚀 Getting Started

### Installation

```bash
pip install promptix
```

### Quick Start

1. **Launch Promptix Studio**:
```bash
promptix studio
```

2. **Create your first prompt template** in the Studio UI or in your YAML file.

3. **Use the prompt in your code**:
```python
from promptix import Promptix

# Basic usage
greeting = Promptix.get_prompt(
    prompt_template="Greeting",
    user_name="Alex"
)

# With OpenAI
from openai import OpenAI
client = OpenAI()

model_config = Promptix.prepare_model_config(
    prompt_template="CustomerSupport",
    customer_name="Jordan Smith",
    issue="billing question"
)

response = client.chat.completions.create(**model_config)
```

## 📊 Real-World Use Cases

### Customer Service
Create dynamic support agent prompts that adapt based on:
- Department-specific knowledge and protocols
- Customer tier and history
- Issue type and severity
- Agent experience level

### Phone Agents
Develop sophisticated call handling prompts that:
- Adjust tone and approach based on customer sentiment
- Incorporate relevant customer information
- Follow department-specific scripts and procedures
- Enable different tools based on the scenario

### Content Creation
Generate consistent but customizable content with prompts that:
- Adapt to different content formats and channels
- Maintain brand voice while allowing flexibility
- Include relevant reference materials based on topic

## 🧪 Advanced Usage

### Custom Tools Configuration

```python
# Configure specialized tools for different scenarios
security_review_config = (
    Promptix.builder("CodeReviewer")
    .with_code_snippet(code)
    .with_review_focus("security")
    .with_tool("vulnerability_scanner")
    .with_tool("dependency_checker")
    .build()
)
```

### Schema Validation

Promptix automatically validates your prompt variables against defined schemas:

```python
try:
    # Will raise error if technical_level isn't one of the allowed values
    prompt = Promptix.get_prompt(
        prompt_template="TechnicalSupport",
        technical_level="expert"  # Must be in ["beginner", "intermediate", "advanced"]
    )
except ValueError as e:
    print(f"Validation Error: {str(e)}")
```

## 🤝 Contributing

Promptix is a new project aiming to solve real problems in prompt engineering. Your contributions and feedback are highly valued!

1. Star the repository to show support
2. Open issues for bugs or feature requests
3. Submit pull requests for improvements
4. Share your experience using Promptix

I'm creating these projects to solve problems I face as a developer, and I'd greatly appreciate your support and feedback!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
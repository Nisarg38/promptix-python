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

### 🔄 Static Prompt Retrieval and Version Control
Fetch your static prompts and manage different versions without dynamic templating:

```python
# Get the latest live version of a static prompt
live_prompt = Promptix.get_prompt("CustomerSupportStatic")

# Test a new draft version in development
draft_prompt = Promptix.get_prompt(
    prompt_template="CustomerSupportStatic", 
    version="v2"
)
```

### 🎯 Dynamic Templating with Builder Pattern
Create sophisticated, context-aware system instructions using the fluent builder API:

```python
# Generate a dynamic system instruction
system_instruction = (
    Promptix.builder("CustomerSupport")
    .with_customer_name("Jane Doe")
    .with_department("Technical Support")
    .with_priority("high")
    .with_tool("ticket_history")
    .with_tool_parameter("ticket_history", "max_tickets", 5)
    .system_instruction()  # Returns the system instruction string
)
```

### 🤖 Model Configuration for API Calls
Prepare complete configurations for different LLM providers:

```python
# OpenAI integration
openai_config = (
    Promptix.builder("AgentPrompt")
    .with_customer_context(customer_data)
    .with_issue_details(issue)
    .for_client("openai")
    .build()
)
openai_response = openai_client.chat.completions.create(**openai_config)

# Anthropic integration
anthropic_config = (
    Promptix.builder("AgentPrompt")
    .with_customer_context(customer_data)
    .with_issue_details(issue)
    .for_client("anthropic")
    .build()
)
anthropic_response = anthropic_client.messages.create(**anthropic_config)
```

### 🎨 Promptix Studio
Manage prompts through a clean web interface by simply running:

```bash
promptix studio
```

When you run this command, you'll get access to the Promptix Studio dashboard:

![Promptix Studio Dashboard](https://raw.githubusercontent.com/Nisarg38/promptix-python/refs/heads/main/docs/images/promptix-studio-dashboard.png)

The Studio interface provides:

- **Dashboard overview** with prompt usage statistics
- **Prompt Library** for browsing and managing all your prompts
- **Version management** to track prompt iterations and mark releases as live
- **Quick creation** of new prompts with a visual editor
- **Usage statistics** showing which models and providers are most used
- **Live editing** with immediate validation and preview

Studio makes it easy to collaborate on prompts, test variations, and manage your prompt library without touching code.

> **Note**: To include the screenshot in your README, save the image to your repository (e.g., in a `docs/images/` directory) and update the image path accordingly.

### 🧠 Context-Aware Prompting
Adapt prompts based on dynamic conditions to create truly intelligent interactions:

```python
# Build system instruction with conditional logic
system_instruction = (
    Promptix.builder("CustomerSupport")
    .with_history_context("long" if customer.interactions > 5 else "short")
    .with_sentiment("frustrated" if sentiment_score < 0.3 else "neutral")
    .with_technical_level(customer.technical_proficiency)
    .system_instruction()
)
```

### 🔧 Conditional Tool Selection
Variables set using `.with_var()` are available in tools_template allowing for dynamic tool selection based on variables:

```python
# Conditionally select tools based on variables
config = (
    Promptix.builder("ComplexCodeReviewer")
    .with_var({
        'programming_language': 'Python',  # This affects which tools are selected
        'severity': 'high',
        'review_focus': 'security'
    })
    .build()
)

# Explicitly added tools will override template selections
config = (
    Promptix.builder("ComplexCodeReviewer")
    .with_var({
        'programming_language': 'Java',
        'severity': 'medium'
    })
    .with_tool("complexity_analyzer")  # This tool will be included regardless of template logic
    .with_tool_parameter("complexity_analyzer", "thresholds", {"cyclomatic": 10})
    .build()
)
```

This allows you to create sophisticated tools configurations that adapt based on input variables, with the ability to override the template logic when needed.

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

3. **Use prompts in your code**:
```python
from promptix import Promptix

# Static prompt retrieval
greeting = Promptix.get_prompt("SimpleGreeting")

# Dynamic system instruction
system_instruction = (
    Promptix.builder("CustomerSupport")
    .with_customer_name("Alex")
    .with_issue_type("billing")
    .system_instruction()
)

# With OpenAI
from openai import OpenAI
client = OpenAI()

# Example conversation history
memory = [
    {"role": "user", "content": "Can you help me with my last transaction ?"}
]

openai_config = (
    Promptix.builder("CustomerSupport")
    .with_customer_name("Jordan Smith")
    .with_issue("billing question")
    .with_memory(memory)
    .for_client("openai")
    .build()
)

response = client.chat.completions.create(**openai_config)
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

Read more about the design principles behind Promptix in [Why I Created Promptix: A Local-First Approach to Prompt Management](https://nisarg38.github.io/Portfolio-Website/blog/blogs/promptix-01).

For a detailed guide on how to use Promptix, see [How to Use Promptix: A Developer's Guide](https://nisarg38.github.io/Portfolio-Website/blog/blogs/promptix-02).

## 🧪 Advanced Usage

### Custom Tools Configuration

```python
# Example conversation history
memory = [
    {"role": "user", "content": "Can you help me understand Python decorators?"}
]

# Configure specialized tools for different scenarios
security_review_config = (
    Promptix.builder("CodeReviewer")
    .with_code_snippet(code)
    .with_review_focus("security")
    .with_tool("vulnerability_scanner")
    .with_tool("dependency_checker")
    .with_memory(memory)
    .for_client("openai")
    .build()
)
```

### Schema Validation

Promptix automatically validates your prompt variables against defined schemas:

```python
try:
    # Dynamic system instruction with validation
    system_instruction = (
        Promptix.builder("TechnicalSupport")
        .with_technical_level("expert")  # Must be in ["beginner", "intermediate", "advanced", "expert"]
        .system_instruction()
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

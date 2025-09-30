<div align="center">

# 🧩 Promptix

### Local-First Prompt Management for Production LLM Applications

[![PyPI version](https://badge.fury.io/py/promptix.svg)](https://badge.fury.io/py/promptix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptix.svg)](https://pypi.org/project/promptix/)
[![PyPI Downloads](https://static.pepy.tech/badge/promptix)](https://pepy.tech/projects/promptix)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-ff69b4.svg)](https://github.com/sponsors/Nisarg38)

[**Quick Start**](#-quick-start-in-30-seconds) • [**Features**](#-what-you-get) • [**Examples**](#-see-it-in-action) • [**Studio**](#-promptix-studio) • [**Docs**](https://nisarg38.github.io/Portfolio-Website/blog/blogs/promptix-02)

</div>

---

## 🎯 What is Promptix?

Stop hardcoding prompts in your Python code. **Promptix** is a powerful prompt management system that gives you **version control**, **dynamic templating**, and a **beautiful UI** for managing LLM prompts—all stored locally in your repository.

### The Problem

```python
# ❌ Before: Prompts scattered everywhere in your code
def get_response(customer_name, issue):
    system_msg = f"You are a helpful support agent. Customer: {customer_name}..."
    # Copy-pasted prompts, no versioning, hard to maintain
```

### The Solution

```python
# ✅ After: Clean, versioned, dynamic prompts
from promptix import Promptix

config = (
    Promptix.builder("CustomerSupport")
    .with_customer_name("Jane Doe")
    .with_issue_type("billing")
    .for_client("openai")
    .build()
)

response = client.chat.completions.create(**config)
```

---

## 💖 Show Some Love

**Promptix is free and open-source**, but if you're using it in your enterprise or finding it valuable, we'd love to hear about it! Here are some ways to show support:

### 🌟 Enterprise Users
If your company is using Promptix, we'd be thrilled to:
- **Feature you** in our "Who's Using Promptix" section
- **Get your feedback** on enterprise features
- **Share your success story** (with permission)

### 💰 Support the Project
- ⭐ **Star this repository** - it helps others discover Promptix
- 🐛 **Report issues** or suggest features
- 💬 **Share your experience** - testimonials help the community
- ☕ **Buy me a coffee** - [GitHub Sponsors](https://github.com/sponsors/Nisarg38) or [Ko-fi](https://ko-fi.com/promptix)

### 🤝 Enterprise Support
For enterprise users who want to:
- Get priority support
- Request custom features
- Get implementation guidance
- Discuss commercial licensing

[Contact us](mailto:contact@promptix.io) - we'd love to chat!

---

## 🚀 Quick Start in 30 Seconds

### 1. Install Promptix
```bash
pip install promptix
```

### 2. Create Your First Prompt
```bash
promptix studio  # Opens web UI at http://localhost:8501
```

### 3. Use It in Your Code
```python
from promptix import Promptix

# Simple static prompt
prompt = Promptix.get_prompt("MyPrompt")

# Dynamic prompt with variables
system_instruction = (
    Promptix.builder("CustomerSupport")
    .with_customer_name("Alex")
    .with_priority("high")
    .system_instruction()
)
```

**That's it!** 🎉 You're now managing prompts like a pro.

---

## ✨ What You Get

<table>
<tr>
<td width="50%">

### 🎨 **Visual Prompt Editor**
Manage all your prompts through Promptix Studio—a clean web interface with live preview and validation.

</td>
<td width="50%">

### 🔄 **Version Control**
Track every prompt change. Test drafts in development, promote to production when ready.

</td>
</tr>
<tr>
<td width="50%">

### 🎯 **Dynamic Templating**
Context-aware prompts that adapt to user data, sentiment, conditions, and more.

</td>
<td width="50%">

### 🤖 **Multi-Provider Support**
One API, works with OpenAI, Anthropic, and any LLM provider.

</td>
</tr>
</table>

---

## 👀 See It in Action

### Example 1: Static Prompts with Versioning
```python
# Use the current live version
live_prompt = Promptix.get_prompt("WelcomeMessage")

# Test a draft version before going live
draft_prompt = Promptix.get_prompt(
    prompt_template="WelcomeMessage", 
    version="v2"
)
```

### Example 2: Dynamic Context-Aware Prompts
```python
# Adapt prompts based on real-time conditions
system_instruction = (
    Promptix.builder("CustomerSupport")
    .with_customer_tier("premium" if user.is_premium else "standard")
    .with_sentiment("frustrated" if sentiment < 0.3 else "neutral")
    .with_history_length("detailed" if interactions > 5 else "brief")
    .system_instruction()
)
```

### Example 3: OpenAI Integration
```python
from openai import OpenAI

client = OpenAI()

# Build complete config for OpenAI
openai_config = (
    Promptix.builder("CodeReviewer")
    .with_code_snippet(code)
    .with_review_focus("security")
    .with_memory([
        {"role": "user", "content": "Review this code for vulnerabilities"}
    ])
    .for_client("openai")
    .build()
)

response = client.chat.completions.create(**openai_config)
```

### Example 4: Anthropic Integration
```python
from anthropic import Anthropic

client = Anthropic()

# Same builder, different client
anthropic_config = (
    Promptix.builder("CodeReviewer")
    .with_code_snippet(code)
    .with_review_focus("security")
    .for_client("anthropic")
    .build()
)

response = client.messages.create(**anthropic_config)
```

### Example 5: Conditional Tool Selection
```python
# Tools automatically adapt based on variables
config = (
    Promptix.builder("CodeReviewer")
    .with_var({
        'language': 'Python',      # Affects which tools are selected
        'severity': 'high',
        'focus': 'security'
    })
    .with_tool("vulnerability_scanner")  # Override template selections
    .build()
)
```

---

## 🎨 Promptix Studio

Launch the visual prompt editor with one command:

```bash
promptix studio
```

![Promptix Studio Dashboard](https://raw.githubusercontent.com/Nisarg38/promptix-python/refs/heads/main/docs/images/promptix-studio-dashboard.png)

**Features:**
- 📊 **Dashboard** with prompt usage analytics
- 📚 **Prompt Library** for browsing and editing
- 🔄 **Version Management** with live/draft states
- ✏️ **Visual Editor** with instant validation
- 📈 **Usage Statistics** for models and providers
- 🚀 **Quick Creation** of new prompts

---

## 🏗️ Why Promptix?

| Challenge | Promptix Solution |
|-----------|-------------------|
| 🍝 Prompts scattered across codebase | Centralized prompt library |
| 🔧 Hard to update prompts in production | Version control with live/draft states |
| 🎭 Static prompts for dynamic scenarios | Context-aware templating |
| 🔄 Switching between AI providers | Unified API for all providers |
| 🧪 Testing prompt variations | Visual editor with instant preview |
| 👥 Team collaboration on prompts | File-based storage with Git integration |

---

## 📚 Real-World Use Cases

### 🎧 Customer Support Agents
```python
# Adapt based on customer tier, history, and sentiment
config = (
    Promptix.builder("SupportAgent")
    .with_customer_tier(customer.tier)
    .with_interaction_history(customer.interactions)
    .with_issue_severity(issue.priority)
    .build()
)
```

### 📞 Phone Call Agents
```python
# Dynamic call handling with sentiment analysis
system_instruction = (
    Promptix.builder("PhoneAgent")
    .with_caller_sentiment(sentiment_score)
    .with_department(transfer_dept)
    .with_script_type("complaint" if is_complaint else "inquiry")
    .system_instruction()
)
```

### 💻 Code Review Automation
```python
# Specialized review based on language and focus area
config = (
    Promptix.builder("CodeReviewer")
    .with_language(detected_language)
    .with_review_focus("performance")
    .with_tool("complexity_analyzer")
    .build()
)
```

### ✍️ Content Generation
```python
# Consistent brand voice with flexible content types
config = (
    Promptix.builder("ContentCreator")
    .with_brand_voice(company.voice_guide)
    .with_content_type("blog_post")
    .with_target_audience(audience_profile)
    .build()
)
```

---

## 🧪 Advanced Features

<details>
<summary><b>Custom Tools Configuration</b></summary>

```python
# Configure specialized tools based on scenario
config = (
    Promptix.builder("SecurityReviewer")
    .with_code(code_snippet)
    .with_tool("vulnerability_scanner")
    .with_tool("dependency_checker")
    .with_tool_parameter("vulnerability_scanner", "depth", "thorough")
    .build()
)
```
</details>

<details>
<summary><b>Schema Validation</b></summary>

```python
# Automatic validation against defined schemas
try:
    system_instruction = (
        Promptix.builder("TechnicalSupport")
        .with_technical_level("expert")  # Validated against allowed values
        .system_instruction()
    )
except ValueError as e:
    print(f"Validation Error: {str(e)}")
```
</details>

<details>
<summary><b>Memory/Chat History</b></summary>

```python
# Include conversation history
memory = [
    {"role": "user", "content": "What's my account balance?"},
    {"role": "assistant", "content": "Your balance is $1,234.56"}
]

config = (
    Promptix.builder("BankingAgent")
    .with_customer_id(customer_id)
    .with_memory(memory)
    .build()
)
```
</details>

---

## 📖 Learn More

- 📝 [**Developer's Guide**](https://nisarg38.github.io/Portfolio-Website/blog/blogs/promptix-02) - Complete usage guide
- 🎯 [**Design Philosophy**](https://nisarg38.github.io/Portfolio-Website/blog/blogs/promptix-01) - Why Promptix exists
- 💡 [**Examples**](./examples/) - Working code examples
- 📚 [**API Reference**](./docs/api_reference.rst) - Full API documentation

---

## 🤝 Contributing

Promptix is actively developed and welcomes contributions!

**Ways to contribute:**
- ⭐ Star the repository
- 🐛 Report bugs or request features via [Issues](https://github.com/Nisarg38/promptix-python/issues)
- 🔧 Submit pull requests
- 📢 Share your experience using Promptix

Your feedback helps make Promptix better for everyone!

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by developers, for developers**

[Get Started](#-quick-start-in-30-seconds) • [View Examples](./examples/) • [Read the Docs](https://nisarg38.github.io/Portfolio-Website/blog/blogs/promptix-02)

</div>
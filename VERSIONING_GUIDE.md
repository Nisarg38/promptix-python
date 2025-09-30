# Promptix V2 Auto-Versioning System 🔄

Complete automatic version management for AI prompts with Git-native workflows.

## 🎯 Quick Start

### 1. Install the Pre-commit Hook
```bash
# Install automatic versioning
promptix hooks install

# Check installation
promptix hooks status
```

### 2. Edit and Commit Prompts
```bash
# Edit any prompt
vim prompts/simple-chat/current.md

# Commit as usual - versions happen automatically  
git add .
git commit -m "Added error handling instructions"
# ✅ Auto-created versions/v002.md
```

### 3. Switch Between Versions
```bash
# Switch to a specific version
promptix version switch simple-chat v001

# Or edit config.yaml directly:
# current_version: v001
git commit -m "Revert to v001"
# ✅ Auto-deployed v001 to current.md
```

## 🏗️ System Architecture

### File Structure
```
my-project/
├── prompts/                    # Git-friendly prompt workspace
│   ├── simple-chat/           # Individual agent directories
│   │   ├── config.yaml        # Configuration & current_version tracking
│   │   ├── current.md         # Active prompt (easy to diff)
│   │   └── versions/          # Automatic version history
│   │       ├── v001.md        
│   │       └── v002.md
│   └── code-reviewer/         # Another agent
│       └── ...
├── hooks/                     # Pre-commit hook script
│   └── pre-commit
└── .git/hooks/               # Git hooks directory
    └── pre-commit            # Installed hook
```

### Enhanced Config.yaml
```yaml
# Agent configuration
metadata:
  name: "SimpleChat"
  description: "Demo chat agent"
  author: "Your Name"
  version: "1.0.0"
  last_modified: "2024-03-01"

# 🔄 NEW: Current version tracking
current_version: v003

# 🔄 NEW: Version history  
versions:
  v001:
    created_at: "2024-03-01T10:30:00"
    author: "developer"
    commit: "abc1234"
    notes: "Initial version"
  v002:
    created_at: "2024-03-01T14:15:00"
    author: "developer"
    commit: "def5678"
    notes: "Added personality"
  v003:
    created_at: "2024-03-01T16:45:00"
    author: "developer"
    commit: "ghi9012"
    notes: "Auto-versioned"

# Schema and config remain the same...
schema:
  type: "object"
  # ... rest of schema
```

## 🔄 User Workflows

### Workflow 1: Normal Development (Auto-versioning)

```bash
# 1. Edit prompt content
vim prompts/simple-chat/current.md
# Add: "Be encouraging and supportive in your responses."

# 2. Commit normally
git add prompts/simple-chat/current.md
git commit -m "Added supportive personality"

# 🤖 Hook runs automatically:
# 📝 Promptix: Processing version management...
#    ✅ prompts/simple-chat/current.md → v004
# 📦 Processed 1 version operation(s)

# 3. Result: 
# ✅ New version v004 created in versions/
# ✅ Config updated with version metadata
# ✅ Clean git diff shows exactly what changed
```

### Workflow 2: Version Switching (Rollback/Deploy)

```bash
# Option A: Use CLI
promptix version switch simple-chat v002
# ✅ Switched simple-chat to v002
# ✅ Updated current.md and config.yaml

# Option B: Edit config.yaml directly  
vim prompts/simple-chat/config.yaml
# Change: current_version: v002

git add .
git commit -m "Rollback to v002"

# 🤖 Hook runs automatically:
# 📝 Promptix: Processing version management...
#    🔄 Deployed v002 to current.md

# 3. Result:
# ✅ current.md now contains v002 content
# ✅ Ready to use the older version
# ✅ Next edit will create v005 (continuing sequence)
```

### Workflow 3: Version Exploration

```bash
# List all agents and current versions
promptix version list

# List versions for specific agent
promptix version versions simple-chat

# View specific version content
promptix version get simple-chat v001

# Create manual version with notes
promptix version create simple-chat --notes "Stable release candidate"
```

## 🛠️ CLI Commands

### Hook Management
```bash
# Installation
promptix hooks install          # Install pre-commit hook
promptix hooks install --force  # Overwrite existing hook

# Management  
promptix hooks status           # Show installation status
promptix hooks test             # Test hook without committing
promptix hooks disable          # Temporarily disable
promptix hooks enable           # Re-enable disabled hook
promptix hooks uninstall        # Remove completely
```

### Version Management
```bash
# Listing
promptix version list                    # All agents + current versions
promptix version versions <agent>       # All versions for agent

# Content Access
promptix version get <agent> <version>  # View version content

# Version Control
promptix version switch <agent> <version>   # Switch to version
promptix version create <agent>             # Create new version manually
promptix version create <agent> --name v010 --notes "Release candidate"
```

## 🔧 Pre-commit Hook Details

### What the Hook Does

1. **Detects Changes**: Monitors `prompts/*/current.md` and `prompts/*/config.yaml` files
2. **Auto-versioning**: When `current.md` changes → creates `versions/vXXX.md`
3. **Version Switching**: When `current_version` changes in config → deploys that version to `current.md`
4. **Updates Metadata**: Maintains version history in `config.yaml`
5. **Git Integration**: Stages new/updated files for the commit

### Safety Features

- ✅ **Never blocks commits** - Always exits successfully
- ✅ **Graceful errors** - Failures become warnings, not errors
- ✅ **Multiple bypasses** - Easy to skip when needed
- ✅ **Simple logic** - File copying + git operations only
- ✅ **No dependencies** - Uses standard Python + Git + YAML

### Bypass Options

```bash
# Temporary skip
SKIP_PROMPTIX_HOOK=1 git commit -m "Skip versioning"

# Disable temporarily
promptix hooks disable

# Git-native bypass
git commit --no-verify -m "Bypass all hooks"

# Remove completely
promptix hooks uninstall
```

## 🚀 Advanced Features

### Batch Version Creation
When committing multiple agents at once:
```bash
vim prompts/simple-chat/current.md
vim prompts/code-reviewer/current.md

git add prompts/
git commit -m "Updated both chat and review prompts"

# 🤖 Hook processes both:
# 📝 Promptix: Processing version management...
#    ✅ prompts/simple-chat/current.md → v005
#    ✅ prompts/code-reviewer/current.md → v012  
# 📦 Processed 2 version operations
```

### Version Deployment Chain
Switch → Edit → Commit creates clean version chains:
```bash
# 1. Switch to older version
promptix version switch simple-chat v002

# 2. Make improvements
vim prompts/simple-chat/current.md

# 3. Commit creates new version based on v002
git commit -m "Improved v002 with new features"
# ✅ Creates v006 (continuing sequence, based on v002 content)
```

### Configuration-Only Changes
Hook ignores config-only changes to avoid infinite loops:
```bash
# Only change temperature, not prompt content
vim prompts/simple-chat/config.yaml

git commit -m "Adjusted temperature parameter"
# Hook runs but finds no current.md changes - exits silently
```

## 📊 Git Integration Benefits

### Perfect Diffs
```diff
# Before (V1): Buried in YAML
- version: "v1" 
+ version: "v2"
- content: "You are helpful"
+ content: "You are a friendly and helpful"

# After (V2): Clean Markdown  
- You are helpful
+ You are a friendly and helpful assistant
```

### Meaningful History
```bash
git log --oneline prompts/simple-chat/
abc1234 Added supportive personality          # Clear intent
def5678 Switch back to v002                   # Version management
ghi9012 Improved error handling instructions  # Feature addition
```

### Team Collaboration
```bash
# PR reviews show exactly what changed:
# Files changed: prompts/simple-chat/current.md
# +Be encouraging and supportive in responses
# +Ask clarifying questions when needed

# Automatic conflict resolution:
# No more YAML merge conflicts
# Clear ownership of prompt changes
```

## 🧪 Testing & Demo

### Manual Testing
```bash
# 1. Install hook
promptix hooks install

# 2. Create test agent
promptix agent create test-agent

# 3. Edit and commit
vim prompts/test-agent/current.md
git add . && git commit -m "Test versioning"

# 4. Check results
ls prompts/test-agent/versions/
promptix version versions test-agent
```

## 🚨 Troubleshooting

### Common Issues

**Hook not running?**
```bash
promptix hooks status  # Check installation
promptix hooks test    # Test without committing
```

**Version not switching?** 
```bash
# Check config.yaml syntax
cat prompts/agent-name/config.yaml

# Verify version exists
ls prompts/agent-name/versions/
```

**Permission errors?**
```bash
chmod +x .git/hooks/pre-commit
promptix hooks install --force
```

### Debug Mode
```bash
# Enable verbose output
export PROMPTIX_DEBUG=1
git commit -m "Test with debug"
```

## 🤝 Team Setup

### Onboarding New Developers
```bash
# 1. Clone repo
git clone <repo-url>
cd <project>

# 2. Install hook  
promptix hooks install

# 3. Ready to go!
# Edit prompts, commit normally
# Versioning happens automatically
```

### Repository Setup
```bash
# Initial setup for new repo
mkdir my-promptix-project
cd my-promptix-project
git init

# Copy hook system
cp -r /path/to/promptix/hooks .
promptix hooks install

# Create first agent
promptix agent create my-agent
git add . && git commit -m "Initial setup"
```

## 📈 Benefits Summary

### Developer Experience
- ✅ **5-minute setup**: `promptix hooks install` and you're ready
- ✅ **Zero friction**: Commit normally, versions happen automatically  
- ✅ **Perfect diffs**: See exactly what changed in prompts
- ✅ **Easy rollbacks**: Switch versions in seconds

### Team Collaboration  
- ✅ **Clean PRs**: Clear prompt changes, no YAML noise
- ✅ **No conflicts**: Git-friendly structure eliminates merge issues
- ✅ **Audit trail**: Complete history of all prompt changes
- ✅ **Consistent workflow**: Same experience for all team members

### System Reliability
- ✅ **Never blocks**: Commits always succeed, even on errors
- ✅ **Easy bypass**: Multiple escape hatches when needed
- ✅ **Simple logic**: Minimal code paths reduce bugs
- ✅ **Fail gracefully**: Errors become warnings, not failures

---

**Ready to get started?** Run `promptix hooks install` and start committing! 🚀

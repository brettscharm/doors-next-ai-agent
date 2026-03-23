# 🚪 DOORS Next Bob Integration Package

> **Plug-and-play integration for connecting Bob to IBM DOORS Next Generation (DNG)**

A complete, ready-to-use package that enables Bob (your AI coding assistant) to interact with IBM DOORS Next projects, browse requirements, and help you build applications based on your requirements data.

---

## 📋 Table of Contents

- [What This Package Does](#-what-this-package-does)
- [Quick Start Guide](#-quick-start-guide)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Using with Bob](#-using-with-bob)
- [API Reference](#-api-reference)
- [Usage Examples](#-usage-examples)
- [Troubleshooting](#-troubleshooting)
- [Advanced Usage](#-advanced-usage)

---

## 🎯 What This Package Does

This package provides a **conversational interface** between Bob and your DOORS Next server, enabling you to:

✅ **Connect** to DOORS Next with your credentials  
✅ **List** all available projects (even if you have 100+)  
✅ **Browse** modules and folders within projects  
✅ **Retrieve** requirements with full metadata  
✅ **Export** requirements to JSON, CSV, or Markdown  
✅ **Build** applications based on your requirements data  

### The Conversational Workflow

```
You → Bob → DOORS Next → Requirements → Your Application
```

1. **Connect**: Authenticate with DOORS Next
2. **List Projects**: See all available projects with numbers
3. **Select Project**: Choose by number or name
4. **Pull Modules**: Get all modules from the project
5. **Save Requirements**: Export to files for app building

---

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.8 or higher
- Access to a DOORS Next server
- Valid DOORS Next credentials
- Bob (Claude Dev) installed in VS Code

### 5-Minute Setup

```bash
# 1. Clone or download this package
cd doors-next-bob-integration

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env with your DOORS credentials

# 4. Test connection
python3 -c "from doors_client import DOORSNextClient; c = DOORSNextClient.from_env(); print('✅ Connected!' if c.authenticate() else '❌ Failed')"

# 5. Configure Bob (see "Using with Bob" section)
```

**That's it!** You're ready to use Bob with DOORS Next.

---

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP client for DOORS API
- `python-dotenv` - Environment variable management
- `mcp` - Model Context Protocol framework
- `lxml` - XML parsing for DOORS responses

### Step 2: Verify Installation

```bash
python3 -c "import requests, dotenv, mcp, lxml; print('✅ All dependencies installed')"
```

---

## ⚙️ Configuration

### Step 1: Create Environment File

```bash
cp .env.example .env
```

### Step 2: Add Your Credentials

Edit `.env` and replace with your actual credentials:

```env
DOORS_URL=https://your-doors-server.com/rm
DOORS_USERNAME=your_username
DOORS_PASSWORD=your_password
DOORS_PROJECT=Your Project Name
```

**Important Notes:**
- ⚠️ **Never commit `.env` to git** - it contains your password
- ✅ The URL should end with `/rm` (no trailing slash)
- ✅ Use your IBM ID credentials if using IBM Cloud
- ✅ `DOORS_PROJECT` is optional for MCP server usage

### Step 3: Test Your Connection

```bash
python3 -c "from doors_client import DOORSNextClient; c = DOORSNextClient.from_env(); print('✅ Connected!' if c.authenticate() else '❌ Failed')"
```

**Expected output:**
```
✅ Successfully authenticated with DOORS Next
✅ Connected!
```

---

## 🤖 Using with Bob

### What is Bob?

Bob is your AI coding assistant (Claude Dev extension for VS Code) that can now interact with DOORS Next through this MCP server.

### Configure Bob to Use This Package

#### Option A: Using Bob's Settings UI (Recommended)

1. Open VS Code
2. Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
3. Type "Bob: Open MCP Settings"
4. Add this configuration:

```json
{
  "mcpServers": {
    "doors-next": {
      "command": "python3",
      "args": [
        "/ABSOLUTE/PATH/TO/doors_mcp_server.py"
      ],
      "env": {
        "DOORS_URL": "https://your-doors-server.com/rm",
        "DOORS_USERNAME": "your_username",
        "DOORS_PASSWORD": "your_password"
      }
    }
  }
}
```

**⚠️ Important:** Replace `/ABSOLUTE/PATH/TO/` with the full path to this directory!

**Find your path:**
```bash
cd doors-next-bob-integration
pwd
# Copy the output and add /doors_mcp_server.py
```

**Example paths:**
- Mac/Linux: `/Users/yourname/projects/doors-next-bob-integration/doors_mcp_server.py`
- Windows: `C:/Users/yourname/projects/doors-next-bob-integration/doors_mcp_server.py`

#### Option B: Manual Configuration

Edit Bob's MCP settings file directly:

**Mac/Linux:**
```
~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

**Windows:**
```
%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

Add the server configuration shown above.

### Step 4: Restart VS Code

After adding the MCP server configuration, **restart VS Code** so Bob can detect the new server.

### Verify Bob Can See the Server

Ask Bob:
```
Bob, what MCP servers do you have access to?
```

You should see `doors-next` in the list.

---

## 💬 Example Bob Conversations

### Example 1: Discover Projects

**You:**
```
Bob, use the doors-next MCP server to list all projects
```

**Bob:**
```
I'll connect to DOORS Next and list all projects...

# DOORS Next Projects (107 total)

1. **User Management System**
   - ID: `_abc123`
   - URL: https://your-server.com/rm/process/project-areas/_abc123

2. **Payment Gateway**
   - ID: `_def456`
   - URL: https://your-server.com/rm/process/project-areas/_def456

[... more projects ...]
```

### Example 2: Get Modules from a Project

**You:**
```
Bob, get modules from project 1
```

**Bob:**
```
# Modules in 'User Management System'

Found 3 module(s):

1. **User Requirements**
   - ID: `_mod001`
   - URL: https://your-server.com/rm/modules/_mod001

2. **System Requirements**
   - ID: `_mod002`
   - URL: https://your-server.com/rm/modules/_mod002

3. **Security Requirements**
   - ID: `_mod003`
   - URL: https://your-server.com/rm/modules/_mod003
```

### Example 3: Complete Workflow

**You:**
```
Bob, I need to build an API based on requirements in DOORS. 
Can you help me pull the requirements and create API specs?
```

**Bob:**
```
I'll help you with that! Let me start by connecting to DOORS Next.
```

**You:**
```
Use the doors-next MCP server to list all projects
```

**Bob:** *[Shows numbered list of projects]*

**You:**
```
Get modules from project 5
```

**Bob:** *[Shows modules in project 5]*

**You:**
```
Now use the doors_client.py to pull all requirements from the first module 
and create an OpenAPI specification based on those requirements
```

**Bob:** *[Pulls requirements and generates OpenAPI spec]*

---

## 📚 API Reference

### DOORSNextClient Class

The main client for interacting with DOORS Next.

#### Initialization

```python
from doors_client import DOORSNextClient

# From environment variables
client = DOORSNextClient.from_env()

# Or manually
client = DOORSNextClient(
    base_url="https://your-server.com/rm",
    username="your_username",
    password="your_password",
    project="Your Project Name"
)
```

#### Methods

##### `authenticate() -> bool`

Authenticate with DOORS Next server.

```python
if client.authenticate():
    print("Connected!")
else:
    print("Authentication failed")
```

**Returns:** `True` if successful, `False` otherwise

---

##### `list_projects() -> List[Dict]`

List all DOORS Next RM projects.

```python
projects = client.list_projects()
for i, project in enumerate(projects, 1):
    print(f"{i}. {project['title']} (ID: {project['id']})")
```

**Returns:** List of project dictionaries with:
- `title` - Project name
- `id` - Project identifier
- `url` - Project service provider URL

---

##### `get_modules(project_url: str, recursive: bool = True) -> List[Dict]`

Get modules/folders from a specific project.

```python
projects = client.list_projects()
bob_project = projects[6]  # Project 7 (0-indexed)
modules = client.get_modules(bob_project['url'])

for module in modules:
    indent = "  " * module['level']
    print(f"{indent}- {module['title']}")
```

**Parameters:**
- `project_url` - Project service provider URL from `list_projects()`
- `recursive` - If True, fetch nested folders (default: True)

**Returns:** List of module dictionaries with:
- `title` - Module name
- `id` - Module identifier
- `url` - Module URL
- `level` - Nesting level (0 = root)
- `created` - Creation timestamp
- `modified` - Last modified timestamp

---

##### `get_requirements_from_module(module_id: str) -> List[Dict]`

Get requirements from a specific module.

```python
requirements = client.get_requirements_from_module("985621")

for req in requirements:
    print(f"{req['id']}: {req['title']}")
    print(f"  Status: {req['status']}")
    print(f"  Type: {req['type']}")
```

**Parameters:**
- `module_id` - Module identifier (from `get_modules()`)

**Returns:** List of requirement dictionaries with:
- `id` - Requirement identifier
- `title` - Requirement title
- `description` - Full description
- `status` - Status (e.g., "Approved", "Draft")
- `type` - Type (e.g., "Functional", "Non-Functional")
- `url` - Requirement URL

---

##### `get_requirements_reportable_api(module_url: str) -> List[Dict]`

Get requirements with full metadata using Reportable REST API.

```python
requirements = client.get_requirements_reportable_api(module_url)

for req in requirements:
    print(f"{req['id']}: {req['title']}")
    print(f"  Created: {req['created']} by {req['creator']}")
    print(f"  Custom attributes: {req['custom_attributes']}")
```

**Parameters:**
- `module_url` - Full module URL

**Returns:** List of requirement dictionaries with extended metadata:
- All fields from `get_requirements_from_module()` plus:
- `format` - Content format
- `created` - Creation timestamp
- `modified` - Last modified timestamp
- `creator` - Creator name
- `custom_attributes` - Dictionary of custom attributes

---

##### `export_to_json(requirements: List[Dict], filename: str)`

Export requirements to JSON file.

```python
requirements = client.get_requirements_from_module("985621")
client.export_to_json(requirements, "requirements.json")
```

---

##### `export_to_markdown(requirements: List[Dict], filename: str)`

Export requirements to Markdown file.

```python
requirements = client.get_requirements_from_module("985621")
client.export_to_markdown(requirements, "requirements.md")
```

---

## 🎨 Usage Examples

### Example 1: List All Projects

```python
from doors_client import DOORSNextClient

# Connect
client = DOORSNextClient.from_env()
client.authenticate()

# List projects
projects = client.list_projects()
print(f"Found {len(projects)} projects:")
for i, project in enumerate(projects, 1):
    print(f"{i}. {project['title']}")
```

### Example 2: Get Modules from a Project

```python
from doors_client import DOORSNextClient

client = DOORSNextClient.from_env()
client.authenticate()

# Get projects
projects = client.list_projects()

# Select first project
project = projects[0]
print(f"Getting modules from: {project['title']}")

# Get modules
modules = client.get_modules(project['url'])
print(f"Found {len(modules)} modules:")
for module in modules:
    indent = "  " * module['level']
    print(f"{indent}- {module['title']}")
```

### Example 3: Export Requirements to JSON

```python
from doors_client import DOORSNextClient

client = DOORSNextClient.from_env()
client.authenticate()

# Get project and modules
projects = client.list_projects()
modules = client.get_modules(projects[0]['url'])

# Get requirements from first module
module_id = modules[0]['id']
requirements = client.get_requirements_from_module(module_id)

# Export to JSON
client.export_to_json(requirements, "requirements.json")
print(f"Exported {len(requirements)} requirements to requirements.json")
```

### Example 4: Create Requirements Summary

```python
from doors_client import DOORSNextClient

client = DOORSNextClient.from_env()
client.authenticate()

# Get all requirements
projects = client.list_projects()
modules = client.get_modules(projects[0]['url'])
requirements = client.get_requirements_from_module(modules[0]['id'])

# Analyze by status
status_counts = {}
for req in requirements:
    status = req['status']
    status_counts[status] = status_counts.get(status, 0) + 1

print("Requirements by Status:")
for status, count in status_counts.items():
    print(f"  {status}: {count}")
```

### Example 5: Using with Bob for App Generation

**Conversation with Bob:**

```
You: Bob, I need to create a REST API based on DOORS requirements.

Bob: I'll help you with that! Let me connect to DOORS.

You: Use doors-next to list all projects

Bob: [Shows projects]

You: Get modules from project 3

Bob: [Shows modules]

You: Now pull requirements from the first module and create an OpenAPI 
     specification with endpoints for each requirement

Bob: [Pulls requirements and generates OpenAPI spec]

You: Great! Now generate Python Flask code to implement these endpoints

Bob: [Generates Flask application code]
```

---

## 🔧 Troubleshooting

### Bob Can't See the MCP Server

**Symptoms:** Bob says "I don't have access to doors-next MCP server"

**Solutions:**

1. **Check the path** in your MCP config:
   ```bash
   cd doors-next-bob-integration
   pwd
   # Use this path + /doors_mcp_server.py
   ```

2. **Restart VS Code** - MCP servers are loaded at startup

3. **Check Bob's logs** - Look for errors in Bob's output panel

4. **Verify the config file exists:**
   ```bash
   # Mac/Linux
   cat ~/Library/Application\ Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
   ```

---

### Authentication Errors

**Symptoms:** "❌ Authentication failed" or 401 errors

**Solutions:**

1. **Verify credentials** in `.env`:
   ```bash
   python3 -c "from doors_client import DOORSNextClient; c = DOORSNextClient.from_env(); print(c.authenticate())"
   ```

2. **Check URL format:**
   - ✅ Correct: `https://goblue.clm.ibmcloud.com/rm`
   - ❌ Wrong: `https://goblue.clm.ibmcloud.com` (missing /rm)
   - ❌ Wrong: `https://goblue.clm.ibmcloud.com/rm/` (trailing slash)

3. **Test network access:**
   ```bash
   curl -I https://your-doors-server.com/rm
   ```

4. **Try different credentials** - Some servers use IBM ID, others use local accounts

---

### Import Errors

**Symptoms:** "ModuleNotFoundError" or "No module named..."

**Solutions:**

```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Verify installation
python3 -c "import requests, dotenv, mcp, lxml; print('✅ OK')"
```

---

### "Project Not Found" Errors

**Symptoms:** Bob can't find a project by name

**Solutions:**

1. **List all projects first:**
   ```
   Bob, use doors-next to list all projects
   ```

2. **Use project number instead of name:**
   ```
   Bob, get modules from project 5
   ```

3. **Use exact project name** (case-insensitive):
   ```
   Bob, get modules from "User Management System"
   ```

---

### No Modules Found

**Symptoms:** `get_modules` returns empty list

**Solutions:**

1. **Check permissions** - Ensure your account can view modules

2. **Verify project type** - Only RM projects have modules

3. **Try a different project:**
   ```python
   projects = client.list_projects()
   for project in projects:
       modules = client.get_modules(project['url'])
       if modules:
           print(f"{project['title']}: {len(modules)} modules")
   ```

---

### Slow Performance

**Symptoms:** Operations take a long time

**Solutions:**

1. **Use non-recursive module fetching:**
   ```python
   modules = client.get_modules(project_url, recursive=False)
   ```

2. **Limit requirements fetching:**
   ```python
   # Only get first 10 modules
   for module in modules[:10]:
       requirements = client.get_requirements_from_module(module['id'])
   ```

3. **Check network latency:**
   ```bash
   ping your-doors-server.com
   ```

---

## 🚀 Advanced Usage

### Using Directly in Python Scripts

```python
#!/usr/bin/env python3
"""
Example: Export all requirements from all projects
"""
from doors_client import DOORSNextClient
import json

def export_all_requirements():
    client = DOORSNextClient.from_env()
    client.authenticate()
    
    all_data = []
    projects = client.list_projects()
    
    for project in projects:
        print(f"Processing: {project['title']}")
        modules = client.get_modules(project['url'])
        
        for module in modules:
            requirements = client.get_requirements_from_module(module['id'])
            all_data.append({
                'project': project['title'],
                'module': module['title'],
                'requirements': requirements
            })
    
    with open('all_requirements.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Exported requirements from {len(projects)} projects")

if __name__ == '__main__':
    export_all_requirements()
```

### Extending the MCP Server

To add new tools to the MCP server, edit `doors_mcp_server.py`:

```python
# Add to list_tools()
Tool(
    name="get_requirements",
    description="Get requirements from a module",
    inputSchema={
        "type": "object",
        "properties": {
            "module_url": {
                "type": "string",
                "description": "Module URL from get_modules"
            }
        },
        "required": ["module_url"]
    }
)

# Add to call_tool()
elif name == "get_requirements":
    module_url = arguments.get("module_url")
    requirements = client.get_requirements_reportable_api(module_url)
    # Format and return requirements
```

### Integration with CI/CD

```yaml
# .github/workflows/sync-requirements.yml
name: Sync DOORS Requirements

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Sync requirements
        env:
          DOORS_URL: ${{ secrets.DOORS_URL }}
          DOORS_USERNAME: ${{ secrets.DOORS_USERNAME }}
          DOORS_PASSWORD: ${{ secrets.DOORS_PASSWORD }}
        run: python sync_requirements.py
```

---

## 📁 File Structure

```
doors-next-bob-integration/
├── README.md                    # This file - complete documentation
├── BOB_INTEGRATION.md           # Bob-specific integration guide
├── requirements.txt             # Python dependencies
├── .env.example                 # Template for credentials
├── .env                         # Your credentials (DO NOT COMMIT)
├── .gitignore                   # Git ignore rules
├── doors_client.py              # DOORS API client library
├── doors_mcp_server.py          # MCP server for Bob
├── DEMO_WORKFLOW_PLAN.md        # Workflow documentation
├── FINDING_MODULES_GUIDE.md     # Module discovery guide
└── archive_*/                   # Archived test/debug files
```

---

## 🔒 Security Best Practices

1. **Never commit `.env`** - It contains your password
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate passwords regularly** - Update `.env` when passwords change
4. **Limit permissions** - Use read-only accounts when possible
5. **Review MCP config** - Ensure credentials aren't in version control

---

## 📖 Additional Resources

- **BOB_INTEGRATION.md** - Detailed Bob integration guide with example prompts
- **DEMO_WORKFLOW_PLAN.md** - Complete workflow documentation
- **FINDING_MODULES_GUIDE.md** - Guide for discovering modules in DOORS
- [DOORS Next Documentation](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors-next)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

---

## 💡 Tips & Best Practices

1. **Start with list_projects** - Always list projects first to see what's available
2. **Use project numbers** - Faster than typing full project names
3. **Cache project lists** - The MCP server caches project lists automatically
4. **Test incrementally** - Test each step before moving to the next
5. **Read error messages** - They often contain helpful suggestions
6. **Use Bob's memory** - Bob remembers project numbers within a conversation
7. **Export early, export often** - Save requirements to files as you work

---

## 🆘 Getting Help

If you encounter issues:

1. ✅ Check the [Troubleshooting](#-troubleshooting) section
2. ✅ Verify your DOORS connection works
3. ✅ Ensure all dependencies are installed
4. ✅ Check the MCP server path in your config
5. ✅ Review Bob's output panel for detailed errors
6. ✅ Read **BOB_INTEGRATION.md** for Bob-specific guidance

---

## 🎉 You're Ready!

This package is now configured and ready to use. Start by asking Bob:

```
Bob, use the doors-next MCP server to list all projects
```

Then follow the conversational workflow to explore your DOORS Next data and build amazing applications!

---

**Made with ❤️ for Bob users who work with DOORS Next**

*Last updated: March 23, 2026*
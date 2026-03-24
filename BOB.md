# DOORS Next AI Agent

This MCP server connects you to IBM DOORS Next Generation (DNG).
All the heavy lifting is done by the MCP tools — you do NOT need to write any Python code.

## First-Time Setup (Do This Automatically)

When a user says "connect to DNG" and the `doors-next` MCP server is NOT available yet:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get the absolute path** to this project directory:
   ```bash
   pwd
   ```

3. **Configure the MCP server** by adding it to your MCP settings file.
   The settings file location depends on the tool:
   - **Bob (VS Code):** Check Bob's MCP settings in VS Code
   - **Other AI assistants:** Check the extension's MCP settings

   Add this entry (using the real absolute path from step 2):
   ```json
   {
     "doors-next": {
       "command": "python3",
       "args": ["doors_mcp_server.py"],
       "cwd": "<absolute path from pwd>"
     }
   }
   ```

4. **Tell the user to restart VS Code** so the MCP server activates.

5. After restart, proceed to the workflow below.

## Reading Requirements

### 1. Get Credentials and Connect
Ask the user for their DOORS Next **URL**, **username**, and **password**.
Then call the `connect_to_dng` tool with those values.

Tell the user:
> "Successfully connected! There are X projects. Do you want me to list them all, or do you know which one we're working with today?"

### 2. Show Modules
When the user picks a project, call `get_modules` with the project number or name.

### 3. Get Requirements
When the user picks a module, call `get_module_requirements` with the project and module.

### 4. Save
After showing requirements, ask if they want to save them to this project.
If yes, call `save_requirements` with their preferred format (json, csv, or markdown).

## Writing Requirements

### When the user asks to generate/create requirements:

1. **First call `get_artifact_types`** for the target project to see what types are available (System Requirement, Heading, User Requirement, etc.)

2. **Generate the requirements** based on the user's input. For each requirement you need:
   - `title` — the requirement statement
   - `content` — detailed body text, acceptance criteria, rationale
   - `artifact_type` — must match a type from step 1 (e.g., "System Requirement", "Heading")

3. **Show the user what you're about to create** and ask for confirmation before writing.

4. **Call `create_requirements`** with the project and the array of requirements.

5. **Tell the user:** "I created X requirements in the 'AI Generated Artifacts' folder in DNG. Please review them and move the ones you approve into the appropriate module."

### Write Rules
- ALL created requirements are automatically prefixed with `[AI Generated]`
- ALL created requirements go into the "AI Generated Artifacts" folder (auto-created)
- NEVER modify or overwrite existing requirements — only create new ones
- NEVER touch Approved requirements
- ALWAYS show the user what will be created and get confirmation before writing
- The human is responsible for moving artifacts into modules and setting approval status

## Tools Quick Reference

| Tool | What it does | Parameters |
|------|-------------|------------|
| `connect_to_dng` | Connect with credentials | url, username, password |
| `list_projects` | List all projects | none |
| `get_modules` | Get modules from a project | project_identifier |
| `get_module_requirements` | Get requirements from a module | project_identifier, module_identifier |
| `save_requirements` | Save requirements to local file | format (json/csv/markdown), filename (optional) |
| `get_artifact_types` | List artifact types for a project | project_identifier |
| `create_requirements` | Create requirements in DNG | project_identifier, requirements[] |

## Rules

- Do NOT write Python code to interact with DNG. Use the MCP tools only.
- Projects and modules can be referenced by number (from listed output) or name (partial match works).
- If `.env` exists with credentials, the tools work without calling `connect_to_dng` first.

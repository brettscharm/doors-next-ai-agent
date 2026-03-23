#!/usr/bin/env python3
"""
DOORS Next MCP Server
Allows Bob to query IBM DOORS Next projects and modules directly via MCP protocol

This server provides two main tools:
1. list_projects - Lists all DNG projects with numbers
2. get_modules - Gets modules from a project (by number or name)
"""

import os
import asyncio
from typing import Any, Optional, List, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from dotenv import load_dotenv
from doors_client import DOORSNextClient

# Load environment variables
load_dotenv()

# Initialize the MCP server
app = Server("doors-next-server")

# Global client instance and projects cache
_client: Optional[DOORSNextClient] = None
_projects_cache: List[Dict] = []


def get_client() -> DOORSNextClient:
    """Get or create the DOORS client instance"""
    global _client
    if _client is None:
        base_url = os.getenv("DOORS_URL")
        username = os.getenv("DOORS_USERNAME")
        password = os.getenv("DOORS_PASSWORD")
        project = os.getenv("DOORS_PROJECT", "")  # Optional for MCP server
        
        if not all([base_url, username, password]):
            raise ValueError(
                "Missing required environment variables: DOORS_URL, DOORS_USERNAME, DOORS_PASSWORD\n"
                "Please set these in your .env file"
            )
        
        _client = DOORSNextClient(base_url, username, password, project)
        if not _client.authenticate():
            raise ValueError("Failed to authenticate with DOORS Next. Check your credentials.")
    
    return _client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for querying DOORS Next"""
    return [
        Tool(
            name="list_projects",
            description=(
                "List all available DOORS Next RM projects. "
                "Returns a numbered list of projects with their IDs. "
                "Use the project number or name with get_modules to retrieve modules."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_modules",
            description=(
                "Get all modules from a DOORS Next project. "
                "You can specify the project by number (from list_projects) or by name. "
                "Returns a list of modules with their IDs and names."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_identifier": {
                        "type": "string",
                        "description": (
                            "Project identifier - can be either:\n"
                            "- A number (e.g., '1', '2', '3') from the list_projects output\n"
                            "- A project name (case-insensitive partial match)"
                        )
                    }
                },
                "required": ["project_identifier"]
            }
        ),
        Tool(
            name="get_requirements",
            description=(
                "Get all requirements from a DOORS Next project using the Reportable API. "
                "You can specify the project by number (from list_projects) or by name. "
                "Returns a list of requirements with ID, title, description, status, and type."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_identifier": {
                        "type": "string",
                        "description": (
                            "Project identifier - can be either:\n"
                            "- A number (e.g., '1', '2', '3') from the list_projects output\n"
                            "- A project name (case-insensitive partial match)"
                        )
                    }
                },
                "required": ["project_identifier"]
            }
        )
    ]


def find_project_by_identifier(projects: List[Dict], identifier: str) -> Optional[Dict]:
    """
    Find a project by number or name
    
    Args:
        projects: List of project dictionaries
        identifier: Either a number (1-based index) or project name
        
    Returns:
        Project dictionary or None if not found
    """
    # Try to parse as number first
    try:
        index = int(identifier) - 1  # Convert to 0-based index
        if 0 <= index < len(projects):
            return projects[index]
    except ValueError:
        pass
    
    # Search by name (case-insensitive partial match)
    identifier_lower = identifier.lower()
    for project in projects:
        if identifier_lower in project['title'].lower():
            return project
    
    return None


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    global _projects_cache
    
    try:
        client = get_client()
        
        if name == "list_projects":
            # Get all projects
            projects = client.list_projects()
            _projects_cache = projects  # Cache for get_modules
            
            if not projects:
                return [TextContent(
                    type="text",
                    text="No projects found. This could mean:\n"
                         "- Your credentials don't have access to any projects\n"
                         "- The DOORS server URL is incorrect\n"
                         "- There are no RM projects in this DOORS instance"
                )]
            
            # Format as numbered list
            result = f"# DOORS Next Projects ({len(projects)} total)\n\n"
            
            for i, project in enumerate(projects, 1):
                result += f"{i}. **{project['title']}**\n"
                result += f"   - ID: `{project['id']}`\n"
                result += f"   - URL: {project['url']}\n\n"
            
            result += "\n---\n\n"
            result += "**To get modules from a project:**\n"
            result += "Use the `get_modules` tool with either:\n"
            result += "- The project number (e.g., '1', '2', '3')\n"
            result += "- The project name (e.g., 'User Management System')\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_modules":
            project_identifier = arguments.get("project_identifier")
            
            if not project_identifier:
                return [TextContent(
                    type="text",
                    text="Error: project_identifier is required\n\n"
                         "Please provide either:\n"
                         "- A project number from list_projects (e.g., '1')\n"
                         "- A project name (e.g., 'User Management System')"
                )]
            
            # Get projects if not cached
            if not _projects_cache:
                _projects_cache = client.list_projects()
            
            if not _projects_cache:
                return [TextContent(
                    type="text",
                    text="Error: No projects available. Run list_projects first."
                )]
            
            # Find the project
            project = find_project_by_identifier(_projects_cache, project_identifier)
            
            if not project:
                # Build helpful error message
                error_msg = f"Error: Project not found: '{project_identifier}'\n\n"
                error_msg += "Available projects:\n"
                for i, p in enumerate(_projects_cache, 1):
                    error_msg += f"{i}. {p['title']}\n"
                
                return [TextContent(type="text", text=error_msg)]
            
            # Get modules from the project
            modules = client.get_modules(project['url'])
            
            if not modules:
                return [TextContent(
                    type="text",
                    text=f"No modules found in project '{project['title']}'.\n\n"
                         "This could mean:\n"
                         "- The project has no modules yet\n"
                         "- You don't have permission to view modules\n"
                         "- The modules endpoint is not available for this project"
                )]
            
            # Format modules list
            result = f"# Modules in '{project['title']}'\n\n"
            result += f"Found {len(modules)} module(s):\n\n"
            
            for i, module in enumerate(modules, 1):
                result += f"{i}. **{module['title']}**\n"
                if module.get('id'):
                    result += f"   - ID: `{module['id']}`\n"
                if module.get('url'):
                    result += f"   - URL: {module['url']}\n"
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_requirements":
            project_identifier = arguments.get("project_identifier")
            
            if not project_identifier:
                return [TextContent(
                    type="text",
                    text="Error: project_identifier is required\n\n"
                         "Please provide either:\n"
                         "- A project number from list_projects (e.g., '1')\n"
                         "- A project name (e.g., 'Aviary Requirements')"
                )]
            
            # Get projects if not cached
            if not _projects_cache:
                _projects_cache = client.list_projects()
            
            if not _projects_cache:
                return [TextContent(
                    type="text",
                    text="Error: No projects available. Run list_projects first."
                )]
            
            # Find the project
            project = find_project_by_identifier(_projects_cache, project_identifier)
            
            if not project:
                # Build helpful error message
                error_msg = f"Error: Project not found: '{project_identifier}'\n\n"
                error_msg += "Available projects:\n"
                for i, p in enumerate(_projects_cache, 1):
                    error_msg += f"{i}. {p['title']}\n"
                
                return [TextContent(type="text", text=error_msg)]
            
            # Get requirements from the project
            requirements = client.get_requirements_from_project(project['url'])
            
            if not requirements:
                return [TextContent(
                    type="text",
                    text=f"No requirements found in project '{project['title']}'.\n\n"
                         "This could mean:\n"
                         "- The project has no requirements yet\n"
                         "- You don't have permission to view requirements\n"
                         "- The requirements endpoint is not available for this project\n\n"
                         "💡 Try using get_modules instead to see if there are modules with requirements."
                )]
            
            # Format requirements list
            result = f"# Requirements in '{project['title']}'\n\n"
            result += f"Found {len(requirements)} requirement(s):\n\n"
            
            for i, req in enumerate(requirements, 1):
                result += f"{i}. **{req['title']}**\n"
                result += f"   - ID: `{req['id']}`\n"
                result += f"   - Status: {req['status']}\n"
                result += f"   - Type: {req['type']}\n"
                if req.get('description'):
                    # Truncate long descriptions
                    desc = req['description']
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    result += f"   - Description: {desc}\n"
                if req.get('url'):
                    result += f"   - URL: {req['url']}\n"
                result += "\n"
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool: {name}\n\n"
                     "Available tools:\n"
                     "- list_projects\n"
                     "- get_modules\n"
                     "- get_requirements"
            )]
    
    except Exception as e:
        import traceback
        error_msg = f"Error executing {name}: {str(e)}\n\n"
        error_msg += "Traceback:\n"
        error_msg += traceback.format_exc()
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob

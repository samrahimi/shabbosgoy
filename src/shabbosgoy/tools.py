#!/usr/bin/env python3
# Tool management for the shabbosgoy application

import os
import shutil
from pathlib import Path

from shabbosgoy.config import DATA_DIR
from shabbosgoy.utils import error_exit, read_file_content

# Define tools directory
TOOLS_DIR = DATA_DIR / "tools"

def init_tools_dir():
    """Initialize the tools directory if it doesn't exist"""
    TOOLS_DIR.mkdir(exist_ok=True, parents=True)

def create_tool(tool_name, tool_script_path, description):
    """Create a new tool by copying the script and creating a toolinfo file
    
    Args:
        tool_name (str): The name of the tool
        tool_script_path (str): Path to the tool script
        description (str): Description of the tool
    
    Returns:
        bool: True if successful, False otherwise
    """
    init_tools_dir()
    
    # Check if tool already exists
    tool_path = TOOLS_DIR / f"{tool_name}.tool"
    toolinfo_path = TOOLS_DIR / f"{tool_name}.toolinfo"
    
    if tool_path.exists() or toolinfo_path.exists():
        return False, f"Tool '{tool_name}' already exists"
    
    # Check if script exists
    script_path = Path(tool_script_path)
    if not script_path.exists():
        return False, f"Script '{tool_script_path}' does not exist"
    
    try:
        # Copy script to tools directory
        shutil.copy2(script_path, tool_path)
        
        # Make the tool executable
        os.chmod(tool_path, 0o755)
        
        # Create toolinfo file
        toolinfo_content = f"""
## {tool_name}
Path: {tool_path}
Usage: {description}

"""
        with open(toolinfo_path, 'w') as f:
            f.write(toolinfo_content)
        
        return True, f"Tool '{tool_name}' created successfully"
    except Exception as e:
        return False, f"Failed to create tool: {e}"

def remove_tool(tool_name, confirm=True):
    """Remove a tool and its toolinfo file
    
    Args:
        tool_name (str): The name of the tool
        confirm (bool): Whether to confirm before removing
    
    Returns:
        bool: True if successful, False otherwise
    """
    init_tools_dir()
    
    # Check if tool exists
    tool_path = TOOLS_DIR / f"{tool_name}.tool"
    toolinfo_path = TOOLS_DIR / f"{tool_name}.toolinfo"
    
    if not tool_path.exists() and not toolinfo_path.exists():
        return False, f"Tool '{tool_name}' does not exist"
    
    try:
        # Remove tool and toolinfo files
        if tool_path.exists():
            os.remove(tool_path)
        if toolinfo_path.exists():
            os.remove(toolinfo_path)
        
        return True, f"Tool '{tool_name}' removed successfully"
    except Exception as e:
        return False, f"Failed to remove tool: {e}"

def list_tools():
    """List all available tools
    
    Returns:
        list: List of tool names
    """
    init_tools_dir()
    
    # Get all toolinfo files
    toolinfo_files = list(TOOLS_DIR.glob("*.toolinfo"))
    
    # Extract tool names from filenames
    tool_names = [f.stem for f in toolinfo_files]
    
    return tool_names

def get_tool_info(tool_name):
    """Get information about a tool
    
    Args:
        tool_name (str): The name of the tool
    
    Returns:
        dict: Tool information
    """
    init_tools_dir()
    
    # Check if tool exists
    toolinfo_path = TOOLS_DIR / f"{tool_name}.toolinfo"
    
    if not toolinfo_path.exists():
        return None
    
    # Read toolinfo file
    toolinfo_content = read_file_content(toolinfo_path)
    
    return toolinfo_content

def get_tools_block(tool_names):
    """Generate a TOOLS block for the system prompt
    
    Args:
        tool_names (list): List of tool names to include
    
    Returns:
        str: TOOLS block for the system prompt
    """
    if not tool_names:
        return ""
    
    tools_block = "<TOOLS>\n"
    
    for tool_name in tool_names:
        tool_info = get_tool_info(tool_name)
        if tool_info:
            tools_block += f"{tool_info}\n\n---\n\n"
    
    tools_block += "</TOOLS>"
    
    return tools_block

def get_tool_use_block():
    """Generate a tool_use block for the system prompt
    
    Returns:
        str: tool_use block for the system prompt
    """
    tool_use_block = """<tool_use>
You have access to certain custom tools that can be invoked directly from the command line.
These tools are executable scripts that can be used alone or in combination with other commands.
You can use these tools just like any other command in your ACTION block.

It is essential to follow the documentation for each tool and the user instructions.
Remember that you do not have to use these tools - whether to use them depends entirely
on the task and the instructions from the user.
</tool_use>"""
    
    return tool_use_block

def parse_tool_args(args_str):
    """Parse tool arguments from a string
    
    This function parses arguments in the format:
    tool_name="name" tool_script=path/to/tool description="description"
    
    Args:
        args_str (str): String containing tool arguments
    
    Returns:
        dict: Dictionary of parsed arguments
    """
    # Simple parsing for demonstration purposes
    if not args_str:
        return {}
        
    # Extract tool_name
    tool_name_match = args_str.split('tool_name=')[1].split(' ')[0] if 'tool_name=' in args_str else None
    if tool_name_match:
        tool_name = tool_name_match.strip('"\'')
    else:
        tool_name = None
        
    # Extract tool_script
    tool_script_match = args_str.split('tool_script=')[1].split(' ')[0] if 'tool_script=' in args_str else None
    if tool_script_match:
        tool_script = tool_script_match.strip('"\'')
    else:
        tool_script = None
        
    # Extract description (everything after description=)
    description_match = args_str.split('description=')[1] if 'description=' in args_str else None
    if description_match:
        # Handle quoted description
        if description_match.startswith('"') and '"' in description_match[1:]:
            description = description_match.split('"')[1]
        elif description_match.startswith("'") and "'" in description_match[1:]:
            description = description_match.split("'")[1]
        else:
            description = description_match.split(' ')[0]
    else:
        description = None
        
    return {
        'tool_name': tool_name,
        'tool_script': tool_script,
        'description': description
    }
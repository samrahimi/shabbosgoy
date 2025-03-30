#!/usr/bin/env python3
# Test script for tool creation

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shabbosgoy.tools import create_tool, list_tools, get_tool_info

def main():
    """Test tool creation"""
    print("Testing tool creation...")
    
    # Create a test tool
    tool_name = "hello_world"
    tool_script = "tests/hello_world.sh"
    description = "A simple hello world tool for testing the tool management system. It greets the user and echoes back any arguments provided."
    
    success, message = create_tool(tool_name, tool_script, description)
    print(message)
    
    if success:
        print("\nListing tools:")
        tools = list_tools()
        for tool in tools:
            print(f"  - {tool}")
            print(f"{get_tool_info(tool)}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
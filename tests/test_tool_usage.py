#!/usr/bin/env python3
# Test script for tool usage in system prompt

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary modules
from src.shabbosgoy.config import get_config, PROMPTS_DIR
from src.shabbosgoy.tools import get_tools_block, get_tool_use_block

def load_system_prompt_test(is_agentic, tools_list=None):
    """Test version of load_system_prompt"""
    # Get custom instructions from config
    config = get_config()
    custom_instructions = config.get('custom_instructions', '')
    
    # Select system prompt based on mode
    grounding_prompt_path = PROMPTS_DIR / "agentic.prompt.xml" if is_agentic else PROMPTS_DIR / "atomic.prompt.xml"
    
    if not grounding_prompt_path.exists():
        print(f"System prompt file not found: {grounding_prompt_path}")
        return "ERROR: System prompt file not found"
    
    with open(grounding_prompt_path, "r") as f:
        grounding_prompt = f.read()
    
    # Start with the base prompt
    system_prompt = grounding_prompt
    
    # Add tools information if tools are specified
    if tools_list and len(tools_list) > 0:
        tools_block = get_tools_block(tools_list)
        tool_use_block = get_tool_use_block()
        if tools_block:
            system_prompt = f"{system_prompt}\n\n{tools_block}\n\n{tool_use_block}"
    
    # Add custom instructions if present
    if len(custom_instructions.strip()) > 0:
        system_prompt = f"{system_prompt}\n\n<AdditionalSystemContext>\n{custom_instructions.strip()}\n</AdditionalSystemContext>"

    return system_prompt

def main():
    """Test tool usage in system prompt"""
    print("Testing tool usage in system prompt...")
    
    # Test with no tools
    print("\n=== System prompt with no tools ===")
    system_prompt = load_system_prompt_test(False)
    print(f"System prompt length: {len(system_prompt)} characters")
    print("First 100 characters:", system_prompt[:100])
    print("Last 100 characters:", system_prompt[-100:])
    
    # Test with hello_world tool
    print("\n=== System prompt with hello_world tool ===")
    system_prompt_with_tool = load_system_prompt_test(False, ["hello_world"])
    print(f"System prompt length: {len(system_prompt_with_tool)} characters")
    print("First 100 characters:", system_prompt_with_tool[:100])
    print("Last 100 characters:", system_prompt_with_tool[-100:])
    
    # Check if the TOOLS and tool_use blocks are included
    tools_block_included = "<TOOLS>" in system_prompt_with_tool
    tool_use_block_included = "<tool_use>" in system_prompt_with_tool
    
    print(f"\nTOOLS block included: {tools_block_included}")
    print(f"tool_use block included: {tool_use_block_included}")
    
    # Extract and print the TOOLS block
    if tools_block_included:
        tools_start = system_prompt_with_tool.find("<TOOLS>")
        tools_end = system_prompt_with_tool.find("</TOOLS>") + len("</TOOLS>")
        tools_block = system_prompt_with_tool[tools_start:tools_end]
        print("\nTOOLS block:")
        print(tools_block)
    
    # Extract and print the tool_use block
    if tool_use_block_included:
        tool_use_start = system_prompt_with_tool.find("<tool_use>")
        tool_use_end = system_prompt_with_tool.find("</tool_use>")
        if tool_use_end > 0:
            tool_use_end += len("</tool_use>")
        tool_use_block = system_prompt_with_tool[tool_use_start:tool_use_end]
        print("\ntool_use block:")
        print(tool_use_block)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
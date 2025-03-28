#!/usr/bin/env python3
# Working memory management for the shabbosgoy application

import uuid
from pathlib import Path
from shabbosgoy.config import WORKING_MEMORY_DIR

def initialize_working_memory():
    """Initialize a new working memory file"""
    # Create directory if it doesn't exist
    WORKING_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate a unique ID for this task
    task_id = str(uuid.uuid4())[:8]
    memory_file = WORKING_MEMORY_DIR / f"temp_task_{task_id}.memory.xml"
    
    # Initialize the memory file with an empty structure
    with open(memory_file, 'w') as f:
        f.write("<task_memory>\n</task_memory>")
    
    return memory_file, task_id

def update_working_memory(memory_file, section_name, content):
    """Append to the working memory file"""
    try:
        with open(memory_file, 'r') as f:
            memory_content = f.read()
        
        # Insert the new content before the closing tag
        updated_content = memory_content.replace("</task_memory>", 
                                                f"<{section_name}>\n{content}\n</{section_name}>\n</task_memory>")
        
        with open(memory_file, 'w') as f:
            f.write(updated_content)
    except Exception as e:
        print(f"\033[33mWarning: Failed to update working memory: {e}\033[0m", file=sys.stderr)

def get_working_memory(memory_file):
    """Read the current working memory content"""
    try:
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                return f.read()
        return ""
    except Exception as e:
        print(f"\033[33mWarning: Failed to read working memory: {e}\033[0m", file=sys.stderr)
        return ""

import sys  # Added missing import

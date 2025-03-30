#!/usr/bin/env python3
# Skills management for the shabbosgoy application

import os
from pathlib import Path

from shabbosgoy.config import DATA_DIR
from shabbosgoy.utils import error_exit, read_file_content

# Define skills directory
SKILLS_DIR = DATA_DIR / "skills"

def init_skills_dir():
    """Initialize the skills directory if it doesn't exist"""
    SKILLS_DIR.mkdir(exist_ok=True, parents=True)

def create_skill(skill_name, description):
    """Create a new skill with the specified name and description
    
    Args:
        skill_name (str): The name of the skill
        description (str): Description of the skill
    
    Returns:
        bool: True if successful, False otherwise
    """
    init_skills_dir()
    
    # Check if skill already exists
    skillinfo_path = SKILLS_DIR / f"{skill_name}.skillinfo"
    
    if skillinfo_path.exists():
        return False, f"Skill '{skill_name}' already exists"
    
    try:
        # Create skillinfo file
        skillinfo_content = f"""# {skill_name}

{description}
"""
        with open(skillinfo_path, 'w') as f:
            f.write(skillinfo_content)
        
        return True, f"Skill '{skill_name}' created successfully"
    except Exception as e:
        return False, f"Failed to create skill: {e}"

def remove_skill(skill_name, confirm=True):
    """Remove a skill
    
    Args:
        skill_name (str): The name of the skill
        confirm (bool): Whether to confirm before removing
    
    Returns:
        bool: True if successful, False otherwise
    """
    init_skills_dir()
    
    # Check if skill exists
    skillinfo_path = SKILLS_DIR / f"{skill_name}.skillinfo"
    
    if not skillinfo_path.exists():
        return False, f"Skill '{skill_name}' does not exist"
    
    try:
        # Remove skillinfo file
        if skillinfo_path.exists():
            os.remove(skillinfo_path)
        
        return True, f"Skill '{skill_name}' removed successfully"
    except Exception as e:
        return False, f"Failed to remove skill: {e}"

def list_skills():
    """List all available skills
    
    Returns:
        list: List of skill names
    """
    init_skills_dir()
    
    # Get all skillinfo files
    skillinfo_files = list(SKILLS_DIR.glob("*.skillinfo"))
    
    # Extract skill names from filenames
    skill_names = [f.stem for f in skillinfo_files]
    
    return skill_names

def get_skill_info(skill_name):
    """Get information about a skill
    
    Args:
        skill_name (str): The name of the skill
    
    Returns:
        dict: Skill information
    """
    init_skills_dir()
    
    # Check if skill exists
    skillinfo_path = SKILLS_DIR / f"{skill_name}.skillinfo"
    
    if not skillinfo_path.exists():
        return None
    
    # Read skillinfo file
    skillinfo_content = read_file_content(skillinfo_path)
    
    return skillinfo_content

def get_skills_block(skill_names):
    """Generate a SKILLS block for the system prompt
    
    Args:
        skill_names (list): List of skill names to include
    
    Returns:
        str: SKILLS block for the system prompt
    """
    if not skill_names:
        return ""
    
    skills_block = "<SKILLS>\n"
    
    for skill_name in skill_names:
        skill_info = get_skill_info(skill_name)
        if skill_info:
            skills_block += f"{skill_info}\n\n---\n\n"
    
    skills_block += "</SKILLS>"
    
    return skills_block

def get_skill_use_block():
    """Generate a skill_use block for the system prompt
    
    Returns:
        str: skill_use block for the system prompt
    """
    skill_use_block = """<skill_use>
You have been provided with specific skills that enhance your capabilities.
These skills are descriptions of workflows, processes, or domain knowledge that you should apply when relevant.

It is essential to follow the documentation for each skill and the user instructions.
Remember that you do not have to use these skills - whether to apply them depends entirely
on the task and the instructions from the user.
</skill_use>"""
    
    return skill_use_block

def parse_skill_args(args_str):
    """Parse skill arguments from a string
    
    Args:
        args_str (str): String containing skill arguments
    
    Returns:
        dict: Dictionary of parsed arguments
    """
    print(f"Raw args string: '{args_str}'")
    
    # Very simple parsing for demonstration purposes
    skill_name = None
    description = None
    
    # Extract skill_name
    if 'skill_name=' in args_str:
        skill_name_start = args_str.find('skill_name=') + len('skill_name=')
        if args_str[skill_name_start] == '"':
            # Extract quoted value
            skill_name_end = args_str.find('"', skill_name_start + 1)
            if skill_name_end != -1:
                skill_name = args_str[skill_name_start + 1:skill_name_end]
        else:
            # Extract unquoted value
            skill_name_end = args_str.find(' ', skill_name_start)
            if skill_name_end == -1:
                skill_name_end = len(args_str)
            skill_name = args_str[skill_name_start:skill_name_end]
    
    # Extract description
    if 'description=' in args_str:
        desc_start = args_str.find('description=') + len('description=')
        if args_str[desc_start] == '"':
            # Extract quoted value
            desc_end = args_str.find('"', desc_start + 1)
            if desc_end != -1:
                description = args_str[desc_start + 1:desc_end]
        else:
            # Extract unquoted value
            desc_end = args_str.find(' ', desc_start)
            if desc_end == -1:
                desc_end = len(args_str)
            description = args_str[desc_start:desc_end]
    
    print(f"Parsed: skill_name='{skill_name}', description='{description}'")
    
    return {
        'skill_name': skill_name,
        'description': description
    }
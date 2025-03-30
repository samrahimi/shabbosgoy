#!/usr/bin/env python3
# Test script for skill usage in system prompt

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary modules
from src.shabbosgoy.config import get_config, PROMPTS_DIR
from src.shabbosgoy.skills import get_skills_block, get_skill_use_block

def load_system_prompt_test(is_agentic, skills_list=None):
    """Test version of load_system_prompt for skills"""
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
    
    # Add skills information if skills are specified
    if skills_list and len(skills_list) > 0:
        skills_block = get_skills_block(skills_list)
        skill_use_block = get_skill_use_block()
        if skills_block:
            system_prompt = f"{system_prompt}\n\n{skills_block}\n\n{skill_use_block}"
    
    # Add custom instructions if present
    if len(custom_instructions.strip()) > 0:
        system_prompt = f"{system_prompt}\n\n<AdditionalSystemContext>\n{custom_instructions.strip()}\n</AdditionalSystemContext>"

    return system_prompt

def main():
    """Test skill usage in system prompt"""
    print("Testing skill usage in system prompt...")
    
    # Test with no skills
    print("\n=== System prompt with no skills ===")
    system_prompt = load_system_prompt_test(False)
    print(f"System prompt length: {len(system_prompt)} characters")
    print("First 100 characters:", system_prompt[:100])
    print("Last 100 characters:", system_prompt[-100:])
    
    # Test with web_development skill
    print("\n=== System prompt with web_development skill ===")
    system_prompt_with_skill = load_system_prompt_test(False, ["web_development"])
    print(f"System prompt length: {len(system_prompt_with_skill)} characters")
    print("First 100 characters:", system_prompt_with_skill[:100])
    print("Last 100 characters:", system_prompt_with_skill[-100:])
    
    # Check if the SKILLS and skill_use blocks are included
    skills_block_included = "<SKILLS>" in system_prompt_with_skill
    skill_use_block_included = "<skill_use>" in system_prompt_with_skill
    
    print(f"\nSKILLS block included: {skills_block_included}")
    print(f"skill_use block included: {skill_use_block_included}")
    
    # Extract and print the SKILLS block
    if skills_block_included:
        skills_start = system_prompt_with_skill.find("<SKILLS>")
        skills_end = system_prompt_with_skill.find("</SKILLS>")
        if skills_end > 0:
            skills_end += len("</SKILLS>")
        skills_block = system_prompt_with_skill[skills_start:skills_end]
        print("\nSKILLS block:")
        print(skills_block)
    
    # Extract and print the skill_use block
    if skill_use_block_included:
        skill_use_start = system_prompt_with_skill.find("<skill_use>")
        skill_use_end = system_prompt_with_skill.find("</skill_use>")
        if skill_use_end > 0:
            skill_use_end += len("</skill_use>")
        skill_use_block = system_prompt_with_skill[skill_use_start:skill_use_end]
        print("\nskill_use block:")
        print(skill_use_block)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
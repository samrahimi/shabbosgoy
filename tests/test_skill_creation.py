#!/usr/bin/env python3
# Test script for skill creation

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shabbosgoy.skills import create_skill, list_skills, get_skill_info

def main():
    """Test skill creation"""
    print("Testing skill creation...")
    
    # Create a test skill
    skill_name = "web_development"
    description = """A skill for web development tasks. This skill includes knowledge of:
- HTML, CSS, and JavaScript
- Frontend frameworks like React, Vue, and Angular
- Backend technologies like Node.js, Express, and Django
- Database integration with MongoDB, MySQL, and PostgreSQL
- Responsive design principles
- Web accessibility standards
- Performance optimization techniques"""
    
    success, message = create_skill(skill_name, description)
    print(message)
    
    if success:
        print("\nListing skills:")
        skills = list_skills()
        for skill in skills:
            print(f"  - {skill}")
            print(f"{get_skill_info(skill)}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
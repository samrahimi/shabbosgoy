#!/usr/bin/env python3
# Entry point for the shabbosgoy application

import sys
import argparse
from shabbosgoy.config import get_config, load_system_prompt, set_config_item
from shabbosgoy.utils import error_exit, read_file_content, confirm_action
from shabbosgoy.modes import run_standard_mode, run_agentic_mode
from shabbosgoy.tools import create_tool, remove_tool, list_tools, get_tool_info, parse_tool_args
from shabbosgoy.skills import create_skill, remove_skill, list_skills, get_skill_info, parse_skill_args

def parse_args():
    """Parse command line arguments"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="ShabbosGoy - An agentic AI sysadmin that executes commands and scripts in a Linux terminal environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  shabbosgoy "list all files in the current directory"
  
  # Run in agentic mode for complex tasks
  shabbosgoy "create a web server with Node.js" --agentic
  
  # Use with context file
  shabbosgoy "summarize this data" -c data.json
  
  # Use with tools and skills
  shabbosgoy "when is shabbos tonight" -c location.json --tools search_wikipedia,ask_a_rabbi --skills jewish_calendar
  
  # Tool management
  shabbosgoy --create-tool --tool-name="hello_world" --tool-script=path/to/script.sh --tool-description="A tool that says hello"
  shabbosgoy --list-tools
  shabbosgoy --remove-tool hello_world
  
  # Skill management
  shabbosgoy --create-skill --skill-name="web_development" --skill-description="Knowledge of web technologies"
  shabbosgoy --list-skills
  shabbosgoy --remove-skill web_development
"""
    )
    parser.add_argument("prompt", nargs="*", help="The prompt to send to the LLM", default=[])
    parser.add_argument("--context", "-c", help="Path to a file containing context")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no output)")
    parser.add_argument("--agentic", action="store_true", help="Run in agentic mode (execute multiple steps until completion)")
    parser.add_argument("--max-steps", type=int, help="Maximum number of steps in agentic mode")
    parser.add_argument("--api-endpoint", help="Chat Completions endpoint for the LLM service. Defaults to OpenRouter")
    parser.add_argument("--api-key", help="API key for the LLM service")
    parser.add_argument("--model", help="Model name to use")
    parser.add_argument("--temperature", type=float, help="Temperature setting for the LLM")
    parser.add_argument("--max-context", type=int, help="Maximum input context size in characters")
    parser.add_argument("--custom-instructions", help="Custom instructions to add to the system prompt")
    
    # Configuration group
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument("--set-config", nargs=2, metavar=('KEY', 'VALUE'), help="Set a configuration value")
    config_group.add_argument("--get-config", metavar='KEY', help="Get a configuration value")
    
    # Tool management group
    tool_group = parser.add_argument_group('Tool Management')
    tool_group.add_argument("--create-tool", action="store_true", help="Create a new tool (use with --tool-name, --tool-script, and --tool-description)")
    tool_group.add_argument("--tool-name", help="Name of the tool (used with --create-tool)")
    tool_group.add_argument("--tool-script", help="Path to the tool script (used with --create-tool)")
    tool_group.add_argument("--tool-description", help="Description of the tool (used with --create-tool)")
    tool_group.add_argument("--list-tools", action="store_true", help="List all available tools")
    tool_group.add_argument("--remove-tool", help="Remove a tool with the specified name")
    tool_group.add_argument("--tools", help="Comma-separated list of tools to use for this query")

    # Skill management arguments
    skill_group = parser.add_argument_group('Skill Management')
    skill_group.add_argument("--create-skill", action="store_true", help="Create a new skill (use with --skill-name and --skill-description)")
    skill_group.add_argument("--skill-name", help="Name of the skill (used with --create-skill)")
    skill_group.add_argument("--skill-description", help="Description of the skill (used with --create-skill)")
    skill_group.add_argument("--list-skills", action="store_true", help="List all available skills")
    skill_group.add_argument("--remove-skill", help="Remove a skill with the specified name")
    skill_group.add_argument("--skills", help="Comma-separated list of skills to use for this query")
    return parser.parse_args()

def parse_input_sources(args):
    """Parse input sources based on command line arguments"""
    # If we're just setting or getting config, we don't need input sources
    if args.set_config or args.get_config:
        return "", args
        
    # If we're just managing tools or skills, we don't need input sources
    if args.create_tool or args.list_tools or args.remove_tool or args.create_skill or args.list_skills or args.remove_skill:
        return "", args

    # Check if stdin has content (not connected to a terminal)
    has_stdin_content = not sys.stdin.isatty()
    
    # Get prompt from command line arguments
    if args.prompt:
        prompt = " ".join(args.prompt)
    else:
        # If no prompt provided and no stdin content and no context file, show error
        if not has_stdin_content and not args.context:
            error_exit(f"No prompt provided. Usage: {sys.argv[0]} \"your prompt\" [< input_file] [--context file]")
        # If only stdin content or context file is provided, use it as the prompt
        prompt = ""
    
    # Get context from --context option if provided
    context = ""
    if args.context:
        context = read_file_content(args.context)
    # If no context from file but stdin has content, get context from stdin
    elif has_stdin_content:
        context = sys.stdin.read().strip()
    
    # Format the user message based on provided inputs
    if prompt and context:
        user_query = f"<prompt>{prompt}</prompt>\n<context>\n\n{context}\n\n</context>"
    elif prompt:
        user_query = f"<prompt>{prompt}</prompt>"
    else:
        user_query = f"<context>\n\n{context}\n\n</context>"
    
    if not user_query:
        error_exit("No query content provided")
    
    return user_query, args

def main():
    """Main execution flow"""
    # Parse input sources and arguments
    args = parse_args()
    
    # Get configuration
    config = get_config()
    
    # Handle --set-config
    if args.set_config:
        key, value = args.set_config
        set_config_item(key, value)
        print(f"Configuration updated: {key} = {value}")
        return
    
    # Handle --get-config
    if args.get_config:
        key = args.get_config
        if key in config:
            print(f"{key} = {config[key]}")
        else:
            print(f"Configuration key '{key}' not found")
        return
    
    # Handle tool management
    if args.create_tool:
        # Check if required parameters are provided
        if not args.tool_name or not args.tool_script or not args.tool_description:
            error_exit(
                "Missing required parameters for --create-tool.\n"
                "Usage: shabbosgoy --create-tool --tool-name=\"name\" --tool-script=path/to/script --tool-description=\"description\"\n"
                "Example: shabbosgoy --create-tool --tool-name=\"hello_world\" --tool-script=\"scripts/hello.sh\" --tool-description=\"A tool that says hello\""
            )
        
        tool_name = args.tool_name
        tool_script = args.tool_script
        description = args.tool_description
        
        success, message = create_tool(tool_name, tool_script, description)
        if not success:
            if "already exists" in message:
                if confirm_action(f"Tool '{tool_name}' already exists. Do you want to overwrite it?"):
                    # Remove the existing tool first
                    remove_tool(tool_name, confirm=False)
                    success, message = create_tool(tool_name, tool_script, description)
                    print(message)
                else:
                    print("Tool creation cancelled.")
            else:
                error_exit(message)
        else:
            print(message)
        return
    
    if args.list_tools:
        tools = list_tools()
        if tools:
            print("Available tools:")
            for tool in tools:
                print(f"  - {tool}")
                print(f"{get_tool_info(tool)}\n")
        else:
            print("No tools available.")
        return
    
    if args.remove_tool:
        if confirm_action(f"Are you sure you want to remove tool '{args.remove_tool}'?"):
            success, message = remove_tool(args.remove_tool)
            print(message)
        else:
            print("Tool removal cancelled.")
        return
    

    # Handle skill management
    if args.create_skill:
        # Check if required parameters are provided
        if not args.skill_name or not args.skill_description:
            error_exit(
                "Missing required parameters for --create-skill.\n"
                "Usage: shabbosgoy --create-skill --skill-name=\"name\" --skill-description=\"description\"\n"
                "Example: shabbosgoy --create-skill --skill-name=\"web_development\" --skill-description=\"Knowledge of web development\""
            )
        
        skill_name = args.skill_name
        description = args.skill_description
        
        success, message = create_skill(skill_name, description)
        if not success:
            if "already exists" in message:
                if confirm_action(f"Skill '{skill_name}' already exists. Do you want to overwrite it?"):
                    # Remove the existing skill first
                    remove_skill(skill_name, confirm=False)
                    success, message = create_skill(skill_name, description)
                    print(message)
                else:
                    print("Skill creation cancelled.")
            else:
                error_exit(message)
        else:
            print(message)
        return
    
    if args.list_skills:
        skills = list_skills()
        if skills:
            print("Available skills:")
            for skill in skills:
                print(f"  - {skill}")
                print(f"{get_skill_info(skill)}\n")
        else:
            print("No skills available.")
        return
    
    if args.remove_skill:
        if confirm_action(f"Are you sure you want to remove skill '{args.remove_skill}'?"):
            success, message = remove_skill(args.remove_skill)
            print(message)
        else:
            print("Skill removal cancelled.")
        return
    
    # Parse input sources if we're not just setting or getting config
    user_query, _ = parse_input_sources(args)
    
    # Override max_steps from command line if provided
    max_steps = args.max_steps or config['max_steps']

    # Override other settings from command line if provided
    api_endpoint = args.api_endpoint or config['api_endpoint']
    api_key = args.api_key or config['api_key']
    model_name = args.model or config['model_name']
    temperature = args.temperature if args.temperature is not None else config['temperature']
    max_input_context = args.max_context or config['max_input_context']
    
    # Check if API key is empty
    if api_key == "sk-or-v1-CHANGEME" or not api_key.strip():
        error_exit(
            "LLM Provider API key not set. Please either:\n"
            "1. Set it permanently with: {sys.argv[0]} --set-config api_key YOUR_API_KEY\n"
            "2. Provide it for this run with: {sys.argv[0]} --api-key YOUR_API_KEY ...\n\n"
            "[Current API Endpoint: {api_endpoint}. Use {sys.argv[0]} --set-config api_endpoint YOUR_API_ENDPOINT to change it]"
        )
    
    # Load system prompt with custom instructions if provided
    tools_list = []
    if args.tools:
        tools_list = [tool.strip() for tool in args.tools.split(',')]
        # Validate tools
        available_tools = list_tools()
        for tool in tools_list:
            if tool not in available_tools and available_tools:
                error_exit(
                    f"Tool '{tool}' not found.\n"
                    f"Available tools: {', '.join(available_tools)}\n"
                    f"To create a new tool: shabbosgoy --create-tool tool_name=\"{tool}\" tool_script=path/to/script description=\"description\""
                )
            elif not available_tools:
                error_exit(
                    f"No tools available. You need to create tools first.\n"
                    f"To create a new tool: shabbosgoy --create-tool tool_name=\"{tool}\" tool_script=path/to/script description=\"description\""
                )
                
    # Process skills
    skills_list = []
    if args.skills:
        skills_list = [skill.strip() for skill in args.skills.split(',')]
        # Validate skills
        available_skills = list_skills()
        for skill in skills_list:
            if skill not in available_skills and available_skills:
                error_exit(
                    f"Skill '{skill}' not found.\n"
                    f"Available skills: {', '.join(available_skills)}\n"
                    f"To create a new skill: shabbosgoy --create-skill skill_name=\"{skill}\" description=\"description\""
                )
            elif not available_skills:
                error_exit(
                    f"No skills available. You need to create skills first.\n"
                    f"To create a new skill: shabbosgoy --create-skill skill_name=\"{skill}\" description=\"description\""
                )
    

    system_prompt = load_system_prompt(args.agentic, tools_list, skills_list, instructions= args.custom_instructions if args.custom_instructions else None)

    
    # Run in agentic mode or standard mode
    if args.agentic or sys.argv[0] == "shiksa":
        run_agentic_mode(
            api_endpoint, 
            api_key, 
            model_name, 
            temperature, 
            system_prompt, 
            user_query, 
            args.headless, 
            max_steps, 
            max_input_context
        )
    else:
        run_standard_mode(
            api_endpoint, 
            api_key, 
            model_name, 
            temperature, 
            system_prompt, 
            user_query, 
            args.headless, 
            max_input_context
        )

if __name__ == "__main__":
    main()

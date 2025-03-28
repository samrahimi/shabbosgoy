#!/usr/bin/env python3
# Entry point for the shabbosgoy application

import sys
import argparse
from shabbosgoy.config import get_config, load_system_prompt, set_config_item
from shabbosgoy.utils import error_exit, read_file_content
from shabbosgoy.modes import run_standard_mode, run_agentic_mode

def parse_args():
    """Parse command line arguments"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Send a query to an LLM and execute the response")
    parser.add_argument("prompt", nargs="*", help="The prompt to send to the LLM")
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
    parser.add_argument("--set-config", nargs=2, metavar=('KEY', 'VALUE'), help="Set a configuration value")
    parser.add_argument("--get-config", metavar='KEY', help="Get a configuration value")
    return parser.parse_args()

def parse_input_sources(args):
    """Parse input sources based on command line arguments"""
    # If we're just setting or getting config, we don't need input sources
    if args.set_config or args.get_config:
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
    system_prompt = load_system_prompt(args.agentic)
    
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

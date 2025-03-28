#!/usr/bin/env python3
# Execution modes for the shabbosgoy application

from shabbosgoy.llm import send_llm_request
from shabbosgoy.utils import extract_tagged_content, display_execution_warning, check_done
from shabbosgoy.executor import execute_command
from shabbosgoy.memory import initialize_working_memory, update_working_memory, get_working_memory

def run_standard_mode(api_endpoint, api_key, model_name, temperature, system_prompt, user_query, headless, max_input_context):
    """Run in standard single-query mode"""
    content = send_llm_request(api_endpoint, api_key, model_name, temperature, 
                               system_prompt, user_query, headless, max_input_context)
    
    think, action = extract_tagged_content(content)

    # Display the response (if not in headless mode)
    if not headless:
        print("\033[32m" + "-" * 40 + "\033[0m")
        print("\033[32mThought:\033[0m")
        print(f"\033[33m{think}\033[0m")
        print("\033[32mAction:\033[0m")
        print(f"\033[33m{action}\033[0m")
        print("\033[32m" + "-" * 40 + "\033[0m")

        display_execution_warning()
        
        print("\033[34m" + "-" * 40 + "\033[0m")
        print("\033[34mExecution output:\033[0m")

    # Execute the action
    output, exit_code = execute_command(action, headless)
    print(output)
    if not headless:
        print("\033[34m" + "-" * 40 + "\033[0m")
    
    return output, exit_code

def run_agentic_mode(api_endpoint, api_key, model_name, temperature, system_prompt, user_query, 
                     headless, max_steps, max_input_context):
    """Run in agentic mode, looping until completion or max steps reached"""
    # Initialize working memory
    memory_file, task_id = initialize_working_memory()
    
    if not headless:
        print(f"\033[36mRunning in agentic mode (max {max_steps} steps, task ID: {task_id})\033[0m")
    
    # Execution loop
    step = 1
    done = False

    while step <= max_steps and not done:
        if not headless:
            print(f"\n\033[36m=== Agentic Mode: Step {step}/{max_steps} ===\033[0m\n")
        
        # Get current working memory
        memory_content = get_working_memory(memory_file)
        
        # Format query with working memory
        full_query = f"{user_query}\n\n<working_memory>\n{memory_content}\n</working_memory>"
        
        # Send query to LLM
        content = send_llm_request(api_endpoint, api_key, model_name, temperature, 
                                   system_prompt, full_query, headless, max_input_context)
        
        # Extract thinking and action components
        think, action = extract_tagged_content(content)
        
        # Check if the task is complete
        is_done, think = check_done(think)
        if is_done:
            done = True
            if not headless:
                print("\n\033[32m=== Task Completed ===\033[0m")
        
        # Update working memory with thinking
        update_working_memory(memory_file, f"thinking_step_{step}", think)
        update_working_memory(memory_file, f"action_step_{step}", action)

        # Display the response (if not in headless mode)
        if not headless:
            print("\033[32m" + "-" * 40 + "\033[0m")
            print(f"\033[32mThought (Step {step}):\033[0m")
            print(f"\033[33m{think}\033[0m")
            print(f"\033[32mAction (Step {step}):\033[0m")
            print(f"\033[33m{action}\033[0m")
            print("\033[32m" + "-" * 40 + "\033[0m")
            
            display_execution_warning()
            
            print("\033[34m" + "-" * 40 + "\033[0m")
            print("\033[34mExecution output:\033[0m")
        
        # Execute the action
        output, exit_code = execute_command(action, headless)
        print(output)
        
        # Update working memory with execution results
        update_working_memory(memory_file, f"observation_step_{step}", 
                            f"Exit Code: {exit_code}\nOutput:\n{output}")
        
        if not headless:
            print("\033[34m" + "-" * 40 + "\033[0m")
        
        if done:
            break
        
        step += 1
    
    if not headless and not done:
        print("\n\033[33m=== Maximum steps reached without completion ===\033[0m")
    
    return memory_file

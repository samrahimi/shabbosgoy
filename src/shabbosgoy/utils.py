#!/usr/bin/env python3
# Utility functions for the shabbosgoy application

import sys
import time

def error_exit(message):
    """Display error message and exit"""
    print(f"\033[31mERROR: {message}\033[0m", file=sys.stderr)
    sys.exit(1)

def read_file_content(file_path):
    """Read content from a file"""
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        error_exit(f"Failed to read file {file_path}: {e}")

def extract_tagged_content(text):
    """Extract content between <think> and <action> tags without using regex"""
    # Extract think content
    think_start_tag = "<THINK>"
    think_end_tag = "</THINK>"
    
    think_start = text.find(think_start_tag)
    think_end = text.rfind(think_end_tag)
    
    think = None
    if think_start != -1 and think_end != -1:
        # Add length of start tag to get content beginning
        think_content_start = think_start + len(think_start_tag)
        think = text[think_content_start:think_end]
    
    # Extract action content
    action_start_tag = "<ACTION>"
    action_end_tag = "</ACTION>"

    action_start = text.find(action_start_tag)
    action_end = text.rfind(action_end_tag)
    
    action = None
    if action_start != -1 and action_end != -1:
        # Add length of start tag to get content beginning
        action_content_start = action_start + len(action_start_tag)
        action = text[action_content_start:action_end]

    return think, action

def check_done(text: str):
    is_done = False

    done_start = text.lower().find("<done>")
    if done_start != -1:
        done_end = text.lower().find("</done>")
        is_done = done_end != -1
        if is_done:
            done_content_start = done_start + len("<done>")
            done_message = text[done_content_start:done_end]

            done_block = text[done_start:done_end+len("</done>")]
            text = text.replace(done_block, "")
            if os.getenv("DEBUG") is not None:
                print("[DEBUG] The agent has completed the task. Additional Info (if any): {done_block}")
    return is_done, text

def display_execution_warning(countdown_seconds=3):
    """Display warning and countdown before execution"""
    print("\033[31mWarning: AI-Generated Action. Press CTRL-C to cancel\033[0m")
    for i in range(countdown_seconds, 0, -1):
        print(f"\r\033[31mExecuting in {i} seconds...\033[0m", end="")
        time.sleep(1)
    print("\r\033[31mExecuting now!                      \033[0m")

import os  # Added missing import

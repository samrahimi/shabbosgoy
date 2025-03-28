#!/usr/bin/env python3
# Command execution for the shabbosgoy application

import subprocess

def execute_command(command, headless=False):
    """Execute a shell command and return the output and exit code"""
    try:
        # Use subprocess.Popen to capture output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        exit_code = process.returncode
        
        # Combine stdout and stderr
        output = stdout
        if stderr:
            output += f"\n--- STDERR ---\n{stderr}"
        
        # Show execution status (if not in headless mode)
        if not headless:
            if exit_code == 0:
                print("\033[32mCommand executed successfully.\033[0m")
            else:
                print(f"\033[31mCommand failed with exit code {exit_code}.\033[0m")
        
        return output, exit_code
    except Exception as e:
        error_msg = f"Failed to execute command: {e}"
        print(f"\033[31m{error_msg}\033[0m", file=sys.stderr)
        return error_msg, 1

import sys  # Added missing import

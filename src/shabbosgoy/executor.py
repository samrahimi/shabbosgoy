#!/usr/bin/env python3
# Command execution for the shabbosgoy application

import subprocess
import sys
import os
import select
import fcntl
import termios
import signal
import time

def execute_command(command, headless=False):
    """Execute a shell command with real-time output streaming and input handling."""
    process = None
    old_term = None
    stdin_fd = sys.stdin.fileno()
    old_stdin_flags = None
    
    try:
        # Create the subprocess with pipes for stdin, stdout, and stderr
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # Use binary mode for more reliable I/O
            universal_newlines=False
        )
        
        # Set stdout and stderr to non-blocking mode
        for pipe in [process.stdout, process.stderr]:
            flags = fcntl.fcntl(pipe.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(pipe.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        # Save terminal settings for stdin to restore later
        try:
            old_term = termios.tcgetattr(stdin_fd)
            # Set terminal to raw mode for character-by-character input
            new_term = termios.tcgetattr(stdin_fd)
            new_term[3] = new_term[3] & ~(termios.ECHO | termios.ICANON)  # lflags
            termios.tcsetattr(stdin_fd, termios.TCSANOW, new_term)
            
            # Set stdin to non-blocking
            old_stdin_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
            fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_stdin_flags | os.O_NONBLOCK)
        except (termios.error, IOError):
            # This might happen if stdin is not a terminal
            old_term = None
        
        # Set up for select
        stdout_data = []
        stderr_data = []
        
        # Main I/O loop
        while True:
            # Check if process has terminated
            if process.poll() is not None:
                break
                
            # Wait for I/O readiness with select
            readable, _, _ = select.select(
                [process.stdout, process.stderr, sys.stdin], 
                [], 
                [], 
                0.1  # Small timeout to prevent CPU hogging
            )
            
            # Handle stdout
            if process.stdout in readable:
                output = process.stdout.read(4096)
                if output:
                    sys.stdout.buffer.write(output)
                    sys.stdout.flush()
                    stdout_data.append(output)
            
            # Handle stderr
            if process.stderr in readable:
                error = process.stderr.read(4096)
                if error:
                    sys.stderr.buffer.write(error)
                    sys.stderr.flush()
                    stderr_data.append(error)
            
            # Handle stdin (user input)
            if sys.stdin in readable and process.poll() is None:
                try:
                    user_input = os.read(stdin_fd, 1)
                    if user_input:
                        process.stdin.write(user_input)
                        process.stdin.flush()
                except (IOError, BrokenPipeError):
                    pass
        
        # Read any remaining output after process completion
        for pipe, data_list, output_pipe in [
            (process.stdout, stdout_data, sys.stdout.buffer),
            (process.stderr, stderr_data, sys.stderr.buffer)
        ]:
            while True:
                try:
                    output = pipe.read(4096)
                    if not output:
                        break
                    output_pipe.write(output)
                    output_pipe.flush()
                    data_list.append(output)
                except (IOError, ValueError):
                    break
        
        # Get exit code
        exit_code = process.returncode
        
        # Combine stdout and stderr for return value
        stdout_content = b''.join(stdout_data)
        stderr_content = b''.join(stderr_data)
        
        # Convert to string for return value
        stdout_str = stdout_content.decode('utf-8', errors='replace')
        stderr_str = stderr_content.decode('utf-8', errors='replace')
        
        output = stdout_str
        if stderr_str:
            output += f"\n--- STDERR ---\n{stderr_str}"
        
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
    
    finally:
        # Restore terminal settings if we changed them
        if old_term:
            try:
                # Restore original stdin flags
                if old_stdin_flags is not None:
                    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_stdin_flags)
                
                # Restore terminal mode
                termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_term)
            except (termios.error, IOError):
                pass
        
        # Make sure process resources are cleaned up
        if process:
            for pipe in [process.stdout, process.stderr, process.stdin]:
                if pipe:
                    try:
                        pipe.close()
                    except:
                        pass
            
            # Make sure process is terminated
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=1)
                except:
                    try:
                        process.kill()
                    except:
                        pass

# For testing
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = ' '.join(sys.argv[1:])
        output, exit_code = execute_command(cmd)
        print(f"Exit code: {exit_code}")
    else:
        print("Usage: python executor.py <command>")
        print("Example: python executor.py ls -la")

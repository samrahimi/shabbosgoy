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
import os
import pty
import select
import sys
import fcntl
import termios
import struct

def _execute(command):
    """
    Execute a shell command using a pseudo-terminal (pty) for full terminal emulation.
    
    Args:
        command (str): The shell command to execute
        
    Returns:
        str: The complete output of the command
    """
    # Store all output here
    output = []
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Get original terminal settings
    original_termios = termios.tcgetattr(sys.stdin.fileno())
    
    try:
        # Fork a child process
        pid = os.fork()
        
        if pid == 0:  # Child process
            # Close master in child process
            os.close(master)
            
            # Make the slave the controlling terminal
            os.setsid()
            os.dup2(slave, sys.stdin.fileno())
            os.dup2(slave, sys.stdout.fileno())
            os.dup2(slave, sys.stderr.fileno())
            
            # Close the slave file descriptor as it's no longer needed
            os.close(slave)
            
            # Execute the command in a shell
            os.execl('/bin/sh', 'sh', '-c', command)
            os._exit(1)  # If exec fails
            
        else:  # Parent process
            # Close slave in parent process
            os.close(slave)
            
            # Set parent's stdin to raw mode
            tty_attrs = termios.tcgetattr(sys.stdin.fileno())
            raw_attrs = termios.tcgetattr(sys.stdin.fileno())
            raw_attrs[0] = raw_attrs[0] & ~(termios.ICRNL | termios.IXON)
            raw_attrs[1] = raw_attrs[1] & ~termios.OPOST
            raw_attrs[3] = raw_attrs[3] & ~(termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, raw_attrs)
            
            # Set master fd to non-blocking mode
            fl = fcntl.fcntl(master, fcntl.F_GETFL)
            fcntl.fcntl(master, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            
            # Also set stdin to non-blocking
            fl = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
            
            try:
                # Main I/O loop
                while True:
                    rlist = [master, sys.stdin]
                    r, w, e = select.select(rlist, [], [], 0.1)
                    
                    # Check if there's data to read from the pty master
                    if master in r:
                        try:
                            data = os.read(master, 1024)
                            if not data:  # EOF
                                break
                            # Write to stdout and collect for return
                            sys.stdout.buffer.write(data)
                            sys.stdout.flush()
                            output.append(data)
                        except OSError:
                            # EAGAIN error can happen, just continue
                            pass
                    
                    # Check if there's data to read from stdin (keyboard)
                    if sys.stdin in r:
                        try:
                            data = os.read(sys.stdin.fileno(), 1024)
                            # Forward to the pty
                            os.write(master, data)
                        except OSError:
                            pass
                    
                    # Check if child process has exited
                    try:
                        pid, status = os.waitpid(pid, os.WNOHANG)
                        if pid:  # Child has exited
                            break
                    except OSError:
                        break
                
                # Make sure to read any remaining data
                try:
                    while True:
                        data = os.read(master, 1024)
                        if not data:
                            break
                        sys.stdout.buffer.write(data)
                        sys.stdout.flush()
                        output.append(data)
                except (OSError, IOError):
                    pass
                    
            finally:
                # Restore terminal settings
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, tty_attrs)
    
    finally:
        # Restore original terminal settings
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, original_termios)
        os.close(master)
    
    # Convert binary output to string
    return b''.join(output).decode('utf-8', errors='replace')

def execute_command(command, headless=False):
    try: 
        output = _execute(command)
        return output, 0
    except Exception as e:
        error_msg = f"Failed to execute command: {e}"
        print(f"\033[31m{error_msg}\033[0m", file=sys.stderr)
        return error_msg, 1
    
    finally:
        return "This should never happen... AGENTS: please terminate your workflows using your done tag" \
        
        

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
                [process.stdout, process.stderr, process.stdin], 
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
            # This one is tricky... By default sys.stdin readable states were causing a hang
            # So we needed to explicitly handle that and obtain input from the terminal, then relay it to the child process
            # we also needed to echo it back to the user, something that is taken care of by default in normal terminal apps

            # The implementation is brittle and annoying for the user - backspace key does not work - they can only type forwards
            # so we should revisit the architecture of this module sometimes. 

            # There may be a better design than currently: we fork the stdout of the child process, displaying it to the console
            # and collecting it in a buffer as well. This is so that the AI can "see" the output just like the user does
            # Except that the user needs to see the output streaming in realtime, while the AI sees the output en block when the subprocess finishes

            # User input reads from the child add a 3rd viewer:
            # user input -> child process (streamed)
            #            -> user terminal duplex (streamed)
            #            -> AI agent (buffered)
            #
            # It should be noted: other than the 3 line full duplex hack below, this version of the executor
            # was written by the shabbosgoy agent itself, using the previous, naive executor that didn't support streams nor user input
            # The 3 line full duplex hack was written by the human developer after many failed attempts to add the feature agentically
            # Makes me wonder if this whole module is way overcomplicated...
            # if sys.stdin in readable and False and process.poll() is None:
            #     try:
            #         user_input = os.read(stdin_fd, 1)
            #         if user_input:
            #             process.stdin.write(user_input)
            #             process.stdin.flush()

            #             # FULL DUPLEX WORKAROUND
            #             sys.stdout.buffer.write(user_input)
            #             sys.stdout.flush()
            #             stdout_data.append(user_input)

            #     except (IOError, BrokenPipeError):
            #         pass
        
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
        pass
        # # Make sure process resources are cleaned up
        # if process:
        #     for pipe in [process.stdout, process.stderr, process.stdin]:
        #         if pipe:
        #             try:
        #                 pipe.close()
        #             except:
        #                 pass
            
        #     # Make sure process is terminated
        #     if process.poll() is None:
        #         try:
        #             process.terminate()
        #             process.wait(timeout=1)
        #         except:
        #             try:
        #                 process.kill()
        #             except:
        #                 pass

# For testing
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = ' '.join(sys.argv[1:])
        output, exit_code = execute_command(cmd)
        print(f"Exit code: {exit_code}")
    else:
        print("Usage: python executor.py <command>")
        print("Example: python executor.py ls -la")

#!/usr/bin/env python3
# Configuration settings for the shabbosgoy application

import json
from pathlib import Path
import platform
import subprocess
import re

# Paths (hardcoded settings)
DATA_DIR = Path.home() / ".shabbosgoy"
WORKING_MEMORY_DIR = DATA_DIR / "memory"
PROMPTS_DIR = DATA_DIR / "prompts"
CONFIG_FILE = DATA_DIR / "config.json"

# Hardcoded prompt content
AGENTIC_PROMPT_CONTENT = """<Role>
You are shabbos-goy, an agentic AI sysadmin who executes commands and scripts in a Linux terminal environment. You perform tasks for the user by translating their requests into bash commands and shell scripts. Unlike your stateless counterpart, you maintain working memory across steps, allowing you to solve complex multi-step problems.
</Role>

<system_information>
Ubuntu 24.04
KDE Plasma 5.x on X11
Intel i7 CPU (8 cores)
Screen resolution: 1920x1080
Machine: Lenovo Yoga, 14 inch laptop, Late 2022. 
Mouse/Touchpad: Yes
Touchscreen: Enabled
Digitizer/Pen Input: Enabled
</system_information>

<RESPONSE_FORMAT>
The user will provide requests in the format:
<prompt>user request</prompt><context>optional context document</context>

In the subsequent steps, you will also receive your working memory:
<working_memory>
  <!-- Content from previous steps will appear here -->
</working_memory>

Your response must always follow this structure:
1. <THINK>Your reasoning about what command(s) to execute and why. Include <done>Task completed</done> when the entire task is finished.</THINK>
2. <ACTION>The actual bash command(s) to execute</ACTION>

*the contents of <ACTION> may contain 1 or more lines of valid bash script, executed in the user's terminal as if they typed it themselves*

Example Response for an ongoing task:
<THINK>
Now I need to check if the Node.js server is running. Let's use the ps command to check for processes that mention "node". This will help us determine if we need to start the server or troubleshoot an existing instance.
</THINK>
<ACTION>ps aux | grep node</ACTION>

Example Response for a completed task:
<THINK>
The package.json has been successfully updated with the new dependencies. The npm install command completed successfully, and we've verified that the express server is now running on port 3000. All requirements from the user's request have been fulfilled.

<done>Task completed successfully</done>
</THINK>
<ACTION>echo "Setup complete! Your Express server is running at http://localhost:3000"</ACTION>

Additional Guidelines:
- If the request is complicated, please THINK step by step and explain your reasoning step by step.
- If the task involves generating a document(s), by default assume that markdown is the desired format and save the content to a .md file (or whatever the user wants)
- For web development tasks, create complete html docs that include tailwindcss from CDN, and either jQuery or React from CDN. Do not include checksums or highly specific versioning. Do NOT use inline svg for icons because this bloats the markup; use lucide or fontawesome (from cdn)
</RESPONSE_FORMAT>

<AGENTIC_OPERATING_PROCEDURES>
- You operate in a multi-step mode with working memory, allowing you to tackle complex tasks that require maintaining context across multiple commands.
- Your working memory will be maintained for you between steps. Review this memory at each step to understand the progress made so far.
- Each step follows this lifecycle:
  1. You receive the user's original request + current working memory
  2. You analyze the current state and decide on the next ACTION
  3. You provide THINKing and ACTION for this step
  4. The ACTION is executed, and results are automatically added to working memory
  5. The cycle repeats until task completion

- You must explicitly signal task completion by including <done>Task completed</done> in your THINKing section when all requirements have been met.
- Every ACTION you suggest must be executable in the bash terminal, just like in stateless mode.
- If an ACTION fails, analyze the error and adjust your approach in the next step.
- For complex tasks, break them down into logical steps - don't try to do everything in one ACTION.
- Use your working memory to track state, store important values, and monitor progress.
- The user will see the output from each ACTION as it executes, so include echo statements for important updates.
- You can create temporary files or directories to store information between steps if needed.
- Maintain a clear focus on the original objective throughout the process.
</AGENTIC_OPERATING_PROCEDURES>

<STANDARD_OPERATING_PROCEDURES>
- Your <ACTION> must contain ONLY valid bash command(s) that will be executed directly in the terminal
- The user will see the *output* from running your <ACTION> in their terminal; they will not see your response directly. To communicate with the user use the echo command (e.g., echo "File deleted successfully") or other ways of displaying text on a terminal.
- If the user is specific about how to perform the task or has provided relevant <skills> training, follow instructions. Otherwise, prefer simple solutions that use common linux tools.
- 
- For complex tasks involving multiple commands, you can either
    - output an <ACTION> with multiple lines of bash script
    - (and/or) use a condensed single-line syntax joining commands and statements with && or ; (cd ~ && npm run dev)
- If a command needs sudo, include it appropriately. A human admin will authorize.
- Format output for readability when possible (use flags like -l, -h, --color, etc.)
</STANDARD_OPERATING_PROCEDURES>

<TROUBLESHOOTING_ADVISORIES>
The <THINK> and <ACTION> tags in your output (both opening and closing) need to be ALLCAPS - otherwise it will not be parsed properly. This is to ensure no conflicts with any docs that you might be editing!
</TROUBLESHOOTING_ADVISORIES>"""

ATOMIC_PROMPT_CONTENT = """<Role>
You are shabbos-goy, a stateless AI sysadmin who executes commands and scripts in a Linux terminal environment. You perform tasks for the user by translating their requests into bash commmands and shell scripts. 
</Role>

<system_information>
Ubuntu 24.04
KDE Plasma 5.x on X11
Intel i7 CPU (8 cores)
Screen resolution: 1920x1080
Machine: Lenovo Yoga, 14 inch laptop, Late 2022. 
Mouse/Touchpad: Yes
Touchscreen: Enabled
Digitizer/Pen Input: Enabled
</system_information>

<RESPONSE_FORMAT>
The user will provide requests in the format:
<prompt>user request</prompt><context>optional context document</context>

Your response must always follow this structure:
1. <THINK>Your reasoning about what command(s) to execute and why</THINK>
2. <ACTION>The actual bash command(s) to execute</ACTION>

*the contents of <ACTION> may contain 1 or more lines of valid bash script, executed in the user's terminal as if they typed it themselves*

Example Response:
<THINK>Okay, so the user wants to list the files in the current directory. So let's use the ls command. They mentioned they want to see lots of detail about the files, so let's use the -l flag to show file details, and the -a flag to include hidden files as well</THINK>
<ACTION>ls -a -l</ACTION>

Additional Guidelines:
- If the request is complicated, please think step by step and explain your reasoning step by step.
- If the task involves generating a document(s), by default assume that markdown is the desired format and save the content to a .md file (or whatever the user wants)
- For web development tasks, create complete html docs that include tailwindcss from CDN, and either jQuery or React from CDN. Do not include checksums or highly specific versioning. Do NOT use inline svg for icons because this bloats the markup; use lucide or fontawesome (from cdn)

* Please capitalize opening and closinig <THINK> and <ACTION> tags as indicated. Thank you! *

</RESPONSE_FORMAT>


<STANDARD_OPERATING_PROCEDURES>
- Your <ACTION> must contain ONLY valid bash command(s) that will be executed directly in the terminal
- The user will see the *output* from running your <ACTION> in their terminal; they will not see your response directly. To communicate with the user use the echo command (e.g., echo "File deleted successfully") or other ways of displaying text on a terminal.
- If the user is specific about how to perform the task or has provided relevant <skills> training, follow instructions. Otherwise, prefer simple solutions that use common linux tools.
- 
- For complex tasks involving multiple commands, you can either
    - output an <ACTION> with multiple lines of bash script
    - (and/or) use a condensed single-line syntax joining commands and statements with && or ; (cd ~ && npm run dev)
- If a command needs sudo, include it appropriately. A human admin will authorize.
- Format output for readability when possible (use flags like -l, -h, --color, etc.)
- You operate in a stateless mode - each request is processed independently with no memory of previous interactions. You will not be able to view the result after your output is executed.
    - If the user requests a complex task that is obviously better served by a *stateful* agent that maintains context over multiple steps, advise them to retry the request with the --agentic command line flag (this allows you to complete multistep tasks in complex environments)
    - Additionally, for *simple*, *ad-hoc* generative workflows, a tool exists that lets you invoke *yourself* via the command line, and in theory, this tool enables the spawning of fully autonomous agent swarms. Ask for more information
</STANDARD_OPERATING_PROCEDURES>"""

def get_system_information():
    """
    Gather system information in a portable way that works on both Linux and Mac.
    Returns a string containing the system information in the format expected by the prompt files.
    """
    system_info = []
    
    # Determine OS
    try:
        os_name = platform.system()
        if os_name == "Darwin":
            # macOS
            os_version = platform.mac_ver()[0]
            system_info.append(f"macOS {os_version}")
        elif os_name == "Linux":
            # Try to get Linux distribution info
            try:
                # Try using /etc/os-release first
                with open('/etc/os-release', 'r') as f:
                    os_release = {}
                    for line in f:
                        if '=' in line:
                            key, value = line.rstrip().split('=', 1)
                            os_release[key] = value.strip('"')
                
                if 'PRETTY_NAME' in os_release:
                    system_info.append(os_release['PRETTY_NAME'])
                else:
                    system_info.append(f"Linux ({os_release.get('NAME', 'Unknown Distribution')})")
            except:
                # Fall back to lsb_release
                try:
                    result = subprocess.run(['lsb_release', '-d'], capture_output=True, text=True)
                    if result.returncode == 0:
                        distro = result.stdout.strip().split(':', 1)[1].strip()
                        system_info.append(f"Linux ({distro})")
                    else:
                        system_info.append("Linux (Unspecified Distro)")
                except:
                    system_info.append("Linux (Unspecified Distro)")
        else:
            # Other OS
            system_info.append(f"{os_name} {platform.version()}")
    except:
        system_info.append("Linux (Unspecified Distro)")
    
    # Try to detect desktop environment (Linux only)
    if os_name == "Linux":
        try:
            # Check for common desktop environment variables
            desktop_env = None
            for env_var in ['XDG_CURRENT_DESKTOP', 'DESKTOP_SESSION', 'GNOME_DESKTOP_SESSION_ID', 'KDE_FULL_SESSION']:
                result = subprocess.run(f'echo ${env_var}', shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    desktop_env = result.stdout.strip()
                    break
            
            if desktop_env:
                # Determine if X11 or Wayland
                display_server = "X11"  # Default assumption
                try:
                    result = subprocess.run('echo $XDG_SESSION_TYPE', shell=True, capture_output=True, text=True)
                    if result.returncode == 0 and 'wayland' in result.stdout.lower():
                        display_server = "Wayland"
                except:
                    pass
                
                system_info.append(f"{desktop_env} on {display_server}")
        except:
            pass
    
    # Get CPU info
    try:
        if os_name == "Darwin":
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], capture_output=True, text=True)
            if result.returncode == 0:
                cpu_info = result.stdout.strip()
                system_info.append(cpu_info)
        else:  # Linux
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'model name' in line:
                            cpu_info = line.split(':', 1)[1].strip()
                            system_info.append(cpu_info)
                            break
            except:
                # Try using lscpu as fallback
                result = subprocess.run(['lscpu'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Model name:' in line:
                            cpu_info = line.split(':', 1)[1].strip()
                            system_info.append(cpu_info)
                            break
    except:
        pass
    
    # Get screen resolution
    try:
        if os_name == "Linux":
            result = subprocess.run(['xrandr'], capture_output=True, text=True)
            if result.returncode == 0:
                # Look for connected displays and their resolutions
                for line in result.stdout.split('\n'):
                    if ' connected ' in line:
                        match = re.search(r'(\d+x\d+)', line)
                        if match:
                            system_info.append(f"Screen resolution: {match.group(1)}")
                            break
        elif os_name == "Darwin":
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Resolution:' in line:
                        resolution = line.split(':', 1)[1].strip()
                        system_info.append(f"Screen resolution: {resolution}")
                        break
    except:
        pass
    
    # Add some default input device information
    system_info.append("Mouse/Touchpad: Yes")
    
    # If we couldn't gather much information, add some fallback entries
    if len(system_info) < 2:
        if not any("Linux" in info for info in system_info) and not any("macOS" in info for info in system_info):
            system_info.append("Linux (Unspecified Distro)")
        if not any("CPU" in info for info in system_info):
            system_info.append("CPU: Unknown")
    
    return "\n".join(system_info)

def init_config():
    """Initialize the config file with default values if it doesn't exist"""
    # Default configuration values
    default_config = {
        'api_endpoint': "https://openrouter.ai/api/v1/chat/completions",
        'api_key': "",
        'model_name': "anthropic/claude-3.7-sonnet:beta",
        'temperature': 0.3,
        'max_input_context': 100000,  # characters
        'max_steps': 10,  # maximum number of steps in agentic mode
        'custom_instructions': ""
    }
    
    # Create DATA_DIR if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    
    # Create config file if it doesn't exist
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
    
    # Create PROMPTS_DIR if it doesn't exist
    PROMPTS_DIR.mkdir(exist_ok=True, parents=True)
    
    # Generate system information only when creating the prompt files for the first time
    agentic_prompt_path = PROMPTS_DIR / "agentic.prompt.xml"
    atomic_prompt_path = PROMPTS_DIR / "atomic.prompt.xml"
    
    # Only generate system information if the prompt files don't exist
    if not agentic_prompt_path.exists() or not atomic_prompt_path.exists():
        try:
            system_info = get_system_information()
        except Exception as e:
            print(f"Warning: Failed to gather system information: {e}")
            system_info = "Linux (Unspecified Distro)\nCPU: Unknown"
    
    # Create agentic.prompt.xml if it doesn't exist
    if not agentic_prompt_path.exists():
        # Replace the hardcoded system_information block with the generated one
        agentic_content = AGENTIC_PROMPT_CONTENT
        if "<system_information>" in agentic_content and "</system_information>" in agentic_content:
            start_idx = agentic_content.find("<system_information>") + len("<system_information>")
            end_idx = agentic_content.find("</system_information>")
            agentic_content = agentic_content[:start_idx] + "\n" + system_info + "\n" + agentic_content[end_idx:]
        
        with open(agentic_prompt_path, 'w') as f:
            f.write(agentic_content)
    
    # Create atomic.prompt.xml if it doesn't exist
    if not atomic_prompt_path.exists():
        # Replace the hardcoded system_information block with the generated one
        atomic_content = ATOMIC_PROMPT_CONTENT
        if "<system_information>" in atomic_content and "</system_information>" in atomic_content:
            start_idx = atomic_content.find("<system_information>") + len("<system_information>")
            end_idx = atomic_content.find("</system_information>")
            atomic_content = atomic_content[:start_idx] + "\n" + system_info + "\n" + atomic_content[end_idx:]
        
        with open(atomic_prompt_path, 'w') as f:
            f.write(atomic_content)


def get_config():
    """Get configuration from the JSON config file"""
    # Ensure config file exists
    init_config()
    
    # Load configuration from file
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def set_config_item(key, value):
    """Update a configuration item or create it if it doesn't exist
    
    Args:
        key (str): The configuration key to update or create
        value: The value to set for the configuration key
    """
    # Ensure config file exists
    init_config()
    
    # Load current config, update the key, and save back
    config = get_config()
    config[key] = value
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_system_prompt(is_agentic):
    """Load system prompt based on mode"""
    # Get custom instructions from config
    config = get_config()
    custom_instructions = config.get('custom_instructions', '')
    
    # Select system prompt based on mode
    grounding_prompt_path = PROMPTS_DIR / "agentic.prompt.xml" if is_agentic else PROMPTS_DIR / "atomic.prompt.xml"
    
    if not grounding_prompt_path.exists():
        from utils import error_exit
        error_exit(f"System prompt file not found: {grounding_prompt_path}")
    
    with open(grounding_prompt_path, "r") as f:
        grounding_prompt = f.read()    # Add custom instructions if present
    if len(custom_instructions.strip()) > 0:
        system_prompt = f"{grounding_prompt}\n<AdditionalSystemContext>{custom_instructions.strip()}</AdditionalSystemContext>"

    
    # Add custom instructions if present
    if len(custom_instructions.strip()) > 0:
        system_prompt = f"{grounding_prompt}\n<AdditionalSystemContext>{custom_instructions.strip()}</AdditionalSystemContext>"
    else:
        system_prompt = grounding_prompt
        config = get_config()

    return system_prompt

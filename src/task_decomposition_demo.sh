#!/bin/bash

# This script demonstrates recursive task decomposition
# It simulates delegating subtasks and using the results

echo "=== Recursive Task Decomposition Demo ==="
echo "Main agent: I need to create a report about the system"
echo "Main agent: I'll delegate subtasks to specialized agents"

echo -e "\n--- Delegating subtask 1: Get system info ---"
echo "Delegation agent: I'll get the system information"
# Simulate delegation by running the command directly
KERNEL_INFO=$(uname -a)
echo "Delegation agent result: $KERNEL_INFO"

echo -e "\n--- Delegating subtask 2: Get CPU info ---"
echo "Delegation agent: I'll get the CPU information"
# Simulate delegation by running the command directly
CPU_INFO=$(grep "model name" /proc/cpuinfo | head -1 | cut -d ":" -f2 | sed 's/^[ \t]*//')
echo "Delegation agent result: $CPU_INFO"

echo -e "\n--- Delegating subtask 3: Get memory info ---"
echo "Delegation agent: I'll get the memory information"
# Simulate delegation by running the command directly
MEM_INFO=$(free -h | grep "Mem:" | awk '{print "Total: " $2 ", Used: " $3 ", Free: " $4}')
echo "Delegation agent result: $MEM_INFO"

echo -e "\n--- Main agent: Now I'll compile the results ---"
echo "System Report:" > system_report.md
echo "===============" >> system_report.md
echo "" >> system_report.md
echo "## System Information" >> system_report.md
echo "Kernel: $KERNEL_INFO" >> system_report.md
echo "" >> system_report.md
echo "## Hardware" >> system_report.md
echo "CPU: $CPU_INFO" >> system_report.md
echo "Memory: $MEM_INFO" >> system_report.md

echo -e "\n=== Task Decomposition Complete ==="
echo "Main agent: I've created a system report by delegating subtasks"
echo "The report is saved in system_report.md"

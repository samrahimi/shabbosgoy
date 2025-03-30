#!/bin/bash
# A simple hello world tool for testing the tool management system

echo "Hello, World! This is a test tool."
echo "Arguments received: $@"

# If an argument is provided, use it as a name
if [ $# -gt 0 ]; then
    echo "Hello, $1!"
else
    echo "No name provided."
fi
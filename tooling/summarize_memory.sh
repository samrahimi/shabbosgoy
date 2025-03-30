#!/bin/bash

MEMORY_DIR="$HOME/.shabbosgoy/memory"
OUTPUT_FILE="$HOME/.shabbosgoy/memory_summaries.json"

# Check if directory exists
if [ ! -d "$MEMORY_DIR" ]; then
    echo "Error: Directory $MEMORY_DIR does not exist."
    exit 1
fi

# Initialize JSON array
echo "[" > "$OUTPUT_FILE"
first_file=true

# Loop through each XML file
for xml_file in "$MEMORY_DIR"/*.xml; do
    if [ -f "$xml_file" ]; then
        # Create a temporary file for this summary
        temp_output=$(mktemp)
        
        # Create the prompt for shabbosgoy
        prompt="Please analyze this XML file and extract the following information: 
1. initial_prompt: The original prompt provided by the user
2. session_summary: A detailed but concise explanation of how the agent tried to solve the problem
3. intended_outcome: What the user wanted to achieve
4. actual_outcome: What actually happened
5. key_learnings: Any information that might be useful in the future

Format your response as a single JSON object with these fields. Do not include any other text or explanation outside the JSON object. The JSON should be valid and properly escaped."
        
        echo "Processing file: $(basename "$xml_file")"
        
        # Run shabbosgoy with the file as context
        shabbosgoy "$prompt" -c "$xml_file" --headless > "$temp_output"
        
        # Add comma separator if not the first file
        if [ "$first_file" = false ]; then
            echo "," >> "$OUTPUT_FILE"
        else
            first_file=false
        fi
        
        # Append the output to our JSON file
        cat "$temp_output" >> "$OUTPUT_FILE"
        
        # Clean up temp file
        rm "$temp_output"
    fi
done

# Close the JSON array
echo "]" >> "$OUTPUT_FILE"

echo "Summary complete. Results saved to $OUTPUT_FILE"

#!/usr/bin/env python3
# LLM interaction for the shabbosgoy application

import json
import requests
from shabbosgoy.utils import error_exit

def send_llm_request(api_endpoint, api_key, model_name, temperature, system_prompt, user_query, headless=False, max_input_context=100000):
    """Send a request to the LLM API and return the response content"""
    # Only show query info if not in headless mode
    if not headless:
        print(f"\033[34mSending query to LLM: {user_query[:max_input_context]}{'...' if len(user_query) > max_input_context else ''}\033[0m")
        print("Contacting LLM service...")

    # Prepare the JSON payload
    json_payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_query[:max_input_context]
            }
        ],
        "temperature": temperature
    }

    # Make the API request
    try:
        response = requests.post(
            api_endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json=json_payload
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        error_exit(f"Failed to make API request: {e}")

    # Parse the response
    try:
        response_data = response.json()
        content = response_data.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            print("Full API response:")
            print(json.dumps(response_data, indent=2))
            error_exit("Failed to extract content from response. See API response above.")
        return content
    except (json.JSONDecodeError, KeyError) as e:
        error_exit(f"Error parsing API response: {e}")

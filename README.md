# ShabbosGoy

ShabbosGoy is an agentic AI sysadmin tool that executes commands and scripts in a Linux terminal environment.

This README is very minimal

## Installation

```bash
pip install http://github.com/samrahimi/shabbosgoy/dist/shabbosgoy-0.1.2.tar.gz
```

Or build a development version with live edits:

```bash
git clone http://github.com/samrahimi/shabbosgoy && cd shabbosgoy
python3 -m build
pip install . -e
```

Note: you may have to --break-system-packages or use your favorite workaround when installing on Debian / Ubuntu. Ignore the scary warnings - the only package it depends on is `requests` and installation will not break anything!

## Setup

There are several options you can configure as defaults, or use for a specific run. `shabbosgoy --help` will get you started.

The only mandatory setup task is putting in your API credentials for the LLM provider of your choice:

`shabbosgoy --set-config api_key <your_api_key>`

You might also need to set the API endpoint. OpenRouter is configured by default, but this agent will function properly with any API that handles *chat completions* requests and serves a model that is capable of performing tasks.

There are NO vendor-specific dependencies - the default model is Claude 3.7 Sonnet on OpenRouter, with neither advanced reasoning nor the "computer use" beta mode enabled. For a totally free, but rate limited option, Gemini 2.5 Pro prerelease is nearly as capable as Claude, and has a very large context window so it can run for more steps at peak performance levels. 

The API endpoint may be set using: `shabbosgoy --set-config api_endpoint <your_api_endpoint>`

Note that the endpoint needs to be the full URL for chat completions (take your provider's base URL, then add /chat/completions to the end of it)

We invite you to experiment with your favorite models and providers, and to contribute what you learn to the documentation or on the Issues page

## Usage

Run in stateless mode (agent will one-shot your task and execute the result, then exit)
```bash
shabbosgoy "your prompt" 
```

Run in agentic mode (agent will complete the task over one or more steps until it is finished). Use this for complex tasks and anything where the agent needs to fetch data, view the contents of files, or see the output of one command in order to figure out their next move

```bash
shabbosgoy "your prompt" --agentic
```

## Features

- Executes commands and scripts in a Linux terminal environment
- Maintains working memory across steps
- Solves complex multi-step problems

## License

This project is licensed under the MIT License - see the LICENSE file for details.

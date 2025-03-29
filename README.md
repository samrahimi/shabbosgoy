# ShabbosGoy

ShabbosGoy is an agentic AI sysadmin tool that executes commands and scripts in a Linux terminal environment.

This README is very minimal

## Installation

```bash
pip install  https://github.com/samrahimi/shabbosgoy/raw/refs/heads/main/dist/shabbosgoy-0.1.2.tar.gz

#Debian / Ubuntu (see note below):
#pip install --break-system-packages https://github.com/samrahimi/shabbosgoy/raw/refs/heads/main/dist/shabbosgoy-0.1.2.tar.gz
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


Attach a document to the context:

```bash
shabbosgoy "your prompt" -c path/to/your/file
```

 
Use in headless mode in an automated toolchain:

```bash
cat sitemap.xml | shabbosgoy "change the phone number on the contact page and save changes to that file" --headless --agentic | netlify deploy .
```

BE the toolchain:

```bash
shabbosgoy "you are in the root folder of my website... please remove the devops engineer from the about us page because we just replaced him with a bot, and then deploy to netlify using the cli (already installed and configured)" --agentic
```


Write a full length novel (recommend the latest Gemini 2.5 Pro model - it is free and very good at creative work):
```bash
shabbosgoy "write a medical thriller novel that touches on contemporary social and political issues of medical ethics. it should involve a scary viral pandemic and a miraculous cure or vaccine that launches in remarkably short time. but the side effects are not well studied, and we still don't know where the virus originated. start by writing a detailed outline that includes plot summary, characters, and chapter-by-chapter breakdown of key events in the story. then, write the full text of the book, one chapter per action step. for generating longform text use heredocs format to avoid parsing issues and keep it clean. each chapter must be 3000 words long. create a new directory and save each step's output in its own markdown file. good luck!" --agentic
```

Make it into an ebook so you can actually read it:

```bash
shabbbosgoy --agentic "concatenate the markdown files in this folder. outline first, then the chapter files in order. then convert it to an epub format that looks good on a mobile device"
```

Finally, give it some more work to do while you kick back and relax with a book!

*Your Shabbos Goy has the same privileges as the user who requests its services, so be careful what you wish for*

## Features

- Executes commands and scripts in a Linux terminal environment
- Maintains working memory across steps
- Solves complex multi-step problems
- Optimized for DevOps, system administration, troubleshooting, and business process automation
- Human in the loop by default: you have 5 seconds to review each proposed action before it is executed. Privileged actions will request you to authorize sudo like any other tool or script. 
- No enforced guardrails or limitations: the agent can do anything possible from the command line in your environment, within the privilege of the user who invokes it. Human in the loop may be disabled using --headless (headless mode is not recommended on production systems)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

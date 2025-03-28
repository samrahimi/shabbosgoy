# ShabbosGoy

ShabbosGoy is an agentic AI sysadmin tool that executes commands and scripts in a Linux terminal environment.

This README is very minimal

## Installation

```bash
pip install --user shabbosgoy
```

## Usage

Run in stateless mode (agent will one-shot your task and execute the result, then exit)
```bash
goy "your prompt" [options] 
```

Run in agentic mode (agent will complete the task over one or more steps until it is finished). Use this for complex tasks and anything where the agent needs to fetch data, view the contents of files, or see the output of one command in order to figure out their next move

```bash
shiksa "your prompt" [options] 
```
## Features

- Executes commands and scripts in a Linux terminal environment
- Maintains working memory across steps
- Solves complex multi-step problems

## License

This project is licensed under the MIT License - see the LICENSE file for details.

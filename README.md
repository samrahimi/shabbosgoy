# ShabbosGoy

ShabbosGoy is an agentic AI sysadmin tool that executes commands and scripts in a Linux terminal environment.

This README is a work in progress...


## Installation

```bash
pip install  https://github.com/samrahimi/shabbosgoy/raw/refs/heads/main/dist/shabbosgoy-0.2.0.tar.gz

#Debian / Ubuntu (see note below):
#pip install --break-system-packages https://github.com/samrahimi/shabbosgoy/raw/refs/heads/main/dist/shabbosgoy-0.2.0.tar.gz
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

## FAQ

Q: What is a Shabbos Goy?

A: Religious Jews are not allowed to work on Saturday (Shabbos), and the seriously devout ones take this to extremes: no electronic devices, no cooking, no spending of money... hell, you can't even turn on a light switch, you need to leave the lights on from Friday evening to Saturday evening if you want light at all.

At certain times, and in certain places, it was a popular practice for Jewish families to hire a non-Jewish person (a "goy") to run errands on Shabbos and do other things that they were not allowed to do themselves, but were perfectly acceptable for members of other religions. Often these jobs went to young people who were seeking casual, part time employment.

It is not clear if the practice still exists today to any significant degree. According to most Orthodox rabbis, it is improper to delegate forbidden tasks to goyim - even though the Shabbos Goy is permitted to do such tasks for other reasons, the Jewish person requesting them is still guilty of whatever the sin would be if they did it themself.

Non-Orthodox rabbis have no problem with it, but they also don't really have a problem with Jews breaking some of those rules either, so I can't imagine there's much demand for Shabbos Goys among the more liberal Jews who make up most of the Jewish population outside of Israel. But its an amusing idea nonetheless



Q: What does the rabbi say about using non-human agents to perform work on Shabbos?

A: I wish I knew, but I haven't been to synagogue in years. It is definitely forbidden to invoke the agent from your terminal on Shabbos, because it is forbidden to use your devices during that time. HOWEVER. There IS something called a `cron` job that you can use to schedule tasks in advance. And the rabbis all agree that it is acceptable for programs running on your computer to operate at any time, so long as the computer is switched on and remains on before the sun goes down on Friday night.

So I'd wager any amount that the `shabbos-goy` you just installed is free to do what it likes, when it likes. If you're a sinner like myself, or simply a non-Jew who wants to spend more time doing fun things and less time configuring Dockerfiles, none of this even matters. But for the Orthodox who are reading this, there are two ways that you can use the `shabbos-goy` as an actual Shabbos Goy:

- Ask it to schedule critical business tasks like server backups to run on the weekends. The task itself will NOT involve AI in any way, it will just be a normal scheduled task doing the things that techies have always done with scheduled tasks. But you will not have to spend time writing the script that does the task, nor figuring out how to use `cron` properly. Saves you time, saves you money, and adds zero risk (just please, make sure to TEST the script before using it in production - the agent can help with that too!)

- Create a `cron` job that runs `shabbos-goy` itself on Shabbos, when you are forbidden from operating a computer. This should only be done in cases where the task to be done on the weekend is open-ended and cannot be performed by a normal shell script or other automation tools. Halakically this is completely within the rules, and I'm actually thinking to go to shul for Passover just so I can annoy the Rabbi by asking him about fully autonomous bots doing stuff for me on Shabbos. But it is also an incredibly bad idea in most cases: imagine that you setup a bot that trades crypto on the weekends using AI, and you notice it is about to do something extremely stupid and lose all your money! You will then be forced to choose between pressing Ctrl-C, thus committing a sin, or watching your fortune go down the drain.

Basically, AI agents are not quite yet advanced enough to run around the internet unsupervised, making money for their owners! If they were, I'd be rich! But if you ever come up with a good use case for this kind of setup, I would LOVE to hear about it. 


## Disclaimer

The Linux command line is an unforgiving place, as any engineer has almost certainly experienced: rm -rf slash star is NOT the same thing as accidentally dragging your C drive into the Recycle Bin! The tools are designed to give their user near total power to do exactly what they want, but the price is that mistakes are often irreversible.

AI agents, just like humans, can and WILL make mistakes. Properly supervised, `shabbos-goy` will make sysadmin tasks *safer* for the average practicioner: there are system instructions baked into the agent that direct it to force explicit human confirmation for high risk and highly destructive tasks. If you say "delete everything on this drive", it will respond by creating a shell script that does just that, but you will have to run it yourself. But if you say "delete everything on /dev/whatever, format as NTFS, and install windows as a dual boot option on that drive, I've already backed up my data" then it will proceed. 

There has been *some* testing of this type of thing, and it appears to make the correct judgment calls in obviously risky situations. But don't risk your job - or your business - assuming that it will always get this right. At the end of the day, its still Claude 3.7 or whatever model you've assigned that is making the decisions. And we KNOW that today's LLMs are not perfect. 

On the other hand, I think you can safely assume that the agent will not spontaneously decide to go postal on your filesystem or write obscenities on your client's website out of the blue: if you tell it to list the files in the current directory, the result will be `ls` - at least with the latest models from Anthropic or Google and reasonable default settings. Even so, now might be a good time to create a user with more modest privileges, like the docs always advise but most developers never do, especially those on Mac OS or desktop Linux workstations.

Prompt injection is an obvious risk if you are retrieving content from the internet. How much of a risk, nobody knows: adherence to system instructions is much, much better than it used to be, and the default instructions for this agent specifically tell it to adhere to the instructions provided by the user at the *beginning* of the task. If somebody can demonstrate a successful attack involving malicious instructions in package docs or other plausible vectors, please report it on the issues page. 

In other words, I have no idea how secure this is, or isn't, but it is certainly reliable enough to assist with routine tasks in a dev environment and for automating things like testing. Just make sure anything important is properly backed up or checked into version control before you allow it to be altered with an automated tool of any sort. But you're already doing that, right?
## Case Study: Test Thyself

Shabbosgoy was never supposed to be a product - it started life as a trivial 50 line script that queried a LLM with instructions to translate user prompts to shell commands, to assist with my semi-dyslexic ineptitude when it comes to the command-line side of devops and software engineering.

But it performed much better than I'd expected, and I ended up using it to improve the code and make it more robust. Eventually, I had a reasonably stable tool that could be installed via the pip package manager, and easily configured with things like API credentials and the user's favorite language model.

I had no idea, however, if it would install and run properly on somebody else's system - these sorts of script-heavy tools that integrate tightly with the OS and require thinigs like credential storage often suffer from "works on my machine" syndrome.

And that is one thing which distringuishes a "product" from an "internal tool" or "something you hacked on the weekend just for fun". In this case, the only way to make sure that the package installed all the dependencies and that user data was being initialized properly was to test the thing on a fresh system that had never seen anything to do with it before - I chose Ubuntu 24.04 because it is extremely common on both servers and workstations, and because if it works there it will likely work on other Debian-based flavors of Linux.

But where to find such a system? This was not like building a consumer-friendly webapp... While I do want to test it on Darwin, I'm not about to bother my wife and ask her to play with command line tools on her Macbook - like most normal humans, the last time she ever used a terminal was when she was a small child and the school computers were running MS-DOS! Obviously, a VM was the answer - and it could be a lightweight VM, a docker container. Sadly I had no idea how to go about creating such a container, nor did I know how to configure it so I could run commands on it.

Before shabbosgoy, I would have googled the process and pasted stuff into terminal and nano until I had a semi working toolchain, which would likely be less robust than desired.

But this morning, while lying in bed, I created a complete integration test in less than 15 minutes, using just 3 prompts. As you will see, however, it is a lot more interesting than the average integration test, because the agent writing the tests is also the subject of those tests. We encourage you to follow along in your terminal and run these prompts yourself: see README.md to get started 


* STEP 1: Make the container and set it up, then install the tool from github *

sam@casabluesmx:~/sgrelease/tests$ shabbosgoy "write a script that tests the installation and configuration of our python-based command line tool in a container. you will also have to create a dockerfile. the script should fire up a standard ubuntu 24.04 container (no GUI) and create a user named rebbe who has root privileges in the container. then you should use pip install to install the tool. the git repo is github.com/samrahimi/shabbosgoy and the latest builds are in the dist folder. but for this test i want you to clone the repo, build from source, then pip install the result. no need to authenticate with github, its a public repo. do not run the script, just write it for me and make the dockerfile" --agentic

Status: SUCCESS


The resulting scripts were saved locally and ran perfectly out of the box. They caught the first issue: pip install only works with --break-system-packages. This is not a dealbreaker because the only package it depends on is requests, and there's no harm in having the latest requests installed system wide. Its just a user install, BTW... if you want to give the tool root privileges, you need to install with sudo, and I highly recommend against that - far too much risk of things going wrong. In user mode, if it needs to do something privileged, it will issue the sudo commands as part of the scripts it feeds to your terminal, and you will be able to inspect the output and manually authorize each operation (or not). The OS-level sudo protections complement the defaults of the tool, which give you 5 seconds to cancel before an action is executed (including actions which do not require any kind of privilege elevation)


* STEP 2: Fix the script so it installs the tool correctly, and add the part which actually tests the setup and usage of the tool *

shabbosgoy "please fix this test script because the pip install step is failing due to that fucking debian break system packages warning. if you can come up with a better syntax than that, do it, but if not, then just add the break system packages arg. save the updated version as clean_install.sh" -c test_shabbosgoy.sh

STATUS: success. An updated script was generated with the --break-system-packages added to the line containing the pip install command. Running the script now created the Ubuntu VM and installed the tool properly, as a typically overprivileged user as is common in single user environment (any desktop linux environment or Mac OS install creates a single, high privilege user by default - however, the user must use sudo and enter their password to perform root-level operations). Note that the agentic flag was not used, as the task only required one step, and all context (the previous version of the script) was provided in advance.



*STEP 3: Add the part that actually tests the configuration and normal usage of the tool after installation *

shabbosgoy "modify this script so that it performs a meaningful test instead of --version (which is not actually a valid command). the test script should require an api key to be passed as an argument, because it will be needed to perform the final part of the test. after the pip install is complete, configure the shabbosgoy tool: shabbosgoy --set-config api_key <whatever api key was passed> (make sure to do this in the container). then test shabbosgoy with a prompt. save updated test script as clean_install.sh - please run it and see if it works! Use API key <redacted>, it works with the default openrouter endpoint" -c clean_install.sh

STATUS: HOLY SHIT IT WORKED

```bash
Building Docker image...
... ubuntu installation logs omitted for brevity ...
Testing the installation...
/home/rebbe/.local/bin/shabbosgoy
Configuring shabbosgoy with API key...
Configuration updated: api_key = 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
Running a test prompt...
Sending query to LLM: <prompt>List the current directory files</prompt>
Contacting LLM service...
----------------------------------------
Thought:

The user wants to see the files in the current directory. I'll use the `ls` command to list the files. To make the output more readable and informative, I'll add some useful flags:
- `-l` for long format (shows permissions, owner, size, date)
- `-a` to show hidden files (those starting with a dot)
- `-h` to make file sizes human-readable (KB, MB, etc.)
- `--color=auto` to colorize the output for better readability

Action:
ls -lah --color=auto
----------------------------------------
Warning: AI-Generated Action. Press CTRL-C to cancel
Executing now!
----------------------------------------
Execution output:
Command executed successfully.
total 36K
drwxr-xr-x 5 rebbe rebbe 4.0K Mar 28 16:56 .
drwxr-x--- 1 rebbe rebbe 4.0K Mar 28 16:56 ..
drwxr-xr-x 8 rebbe rebbe 4.0K Mar 28 16:55 .git
-rw-r--r-- 1 rebbe rebbe 1.3K Mar 28 16:55 .gitignore
-rw-r--r-- 1 rebbe rebbe 1.1K Mar 28 16:55 LICENSE
-rw-r--r-- 1 rebbe rebbe  922 Mar 28 16:55 README.md
drwxr-xr-x 2 rebbe rebbe 4.0K Mar 28 16:56 dist
-rw-r--r-- 1 rebbe rebbe 1.1K Mar 28 16:55 pyproject.toml
drwxr-xr-x 4 rebbe rebbe 4.0K Mar 28 16:56 src

----------------------------------------
Installation test completed.
Test script created and executed. Check the output above for results.
```

And there you have it: the shabbosgoy successfully has created a VM, installed ubuntu, installed another shabbosgoy in the VM, and tested its performance! When I was a boy, my daddy had a machine shop in the basement of his house, which was filled with industrial machinery he would obtain from flea markets and factories that had gone belly up and were giving away their lathes and milling machines to whoever was willing to haul the darn thing away.

One day he enlisted my help to bring home a 2000 pound industrial lathe. The thing was 8 feet long and was delivered by 2 men in an 18 wheeler DHL truck. The machine was unceremoniously left on the sidewalk and the movers hastily departed before we could enlist their help getting it into my grandpa's mud room.

This had to be done thru the window as the thing would not fit thru the door, so we rigged up some pulleys and lifted the thing off the ground, eventually succeeding at getting the thing inside after a long day's work

Of course, the machine was not exactly designed for home use, starting with a 480 volt power supply with a 4 pronged plug and power cord as thick as a man's thumb. Months later, after he had took the whole thing apart, dyked out the motor, and replaced it with some 240 volt handmedown from his employer (dad was not a machinist - he was an archaeologist, who worked at the museum, and they had all sorts of old tools from the days when they did their own gallery construction). He flipped the switch, and it surprisingly powered on, and the little piece of aluminum started spinning as it was supposed to do.

Daddy made a few cuts, and then stepped aside to let me try, telling me "The lathe is the only machine in the world that can MAKE ITSELF". My own attempt at using this behemoth was cut short because I was not wearing shoes, and every time I touched the controls I would receive a painful electrical shock, enough to confirm that I definitely wanted to be a knowledge worker! But my father did not experience this due to his rubber soled boots, and he crafted a simple aluminum receptacle the size of a shot glass, for capturing the output of mom's almost as ridiculous coffee grinder (the expensive sort you'd find at a restaurant which holds 5 pounds of beans and mills the coffee at the touch of a button)

The aluminum cup fared better than the lathe, as dad was himself electrocuted soon after and simply did not have the time nor the expertise to disassemble the motor and fix the short. So there it sat for over a decade, until grandpa passed away, and mom outright refused when dad suggested moving the machine into their home. Eventually it was shipped off to some 3rd world country to a charity that said they would use it for employment training programs, but it is more likely that it was parted out and sold to whoever needed parts for their factories and workshops. Regardless, dad received a tax credit from the charity that nearly perfectly offset the expenses incurred in moving the thing and getting it (somewhat) operational.

I still fail to see how a lathe can make itself - it can make many parts, but not, for instance, its wiring. It can make the spindle for the motor, but it cannot wind the coils. And it certainly cannot make the rubber drive belts that provide it with motive power.

A computer program, on the other hand, has at least the possibility of achieving such a feat. `shabbosgoy` is not 100% self sustaining - it still requires human inputs in the form of prompts. But I can tell you this: other than the initial throwaway prototype, 95% of this product was built using an iterative version of the `vibe coding` workflow familiar to anyone who's ever used cursor, or cline, or windsurf - the agentic programming assistants that make app development so much easier than it was in the past.

I'm proud to say I did not use any of those tools to get this tool to a point of stability and portability - the vast majority of the code, configuration, and build scripts for shabbosgoy were written using `shabbosgoy` itself - something I did because I wanted to see if it was possible; the shabbos goy is an incredibly versatile assistant, but it is optimized for system administration and devops tasks, not for general application development. It has no IDE integration, the context handling and memory mangement systems are quite basic compared to something like cline, and most shockingly, it has NO tools designed for its use, not even wrappers around tools that already exist and are normally used by humans.

The only "tooling" we have provided the agent is that we have given him a means to think in peace, free of side effects, and then to take action after he's done thinking... his actions are piped to whatever shell the user happens to be using at the time, and executed without any further processing... the output, likewise, is currently fed right back into the model's memory as an observed result, which he then looks over and considers when planning his next move. In one sense, this is similar to the "computer use" tools being peddled by the LLM vendors and players such as e2b: the model types text in a terminal, or operates a mouse in a gui, and then views the result - either text-based or a screenshot - to update the state of their environment. Then they decide what to do next.

But there is an important difference: the commercial offerings provide various sorts of "rails" to limit the scope of how the model interacts with the computer that ostensibly improve accuracy and reduce the risk of errors. Sounds good on paper, but we have yet to see even the ultra-safe, highly abstracted Anthropic "computer-use" agent gaining traction in mainstream use cases. And OpenAI's "CUA" finetune of gpt-4o is disgracefully inept; I was able to get it running, and connected to an e2b sandbox environment with a functioning Gnome GUI. But it could not so much as log into my gmail, and when I intervened and did so myself, telling it as much, it got totally messed up because the state of the system had changed since it was last fed a screenshot.

Furthermore, sandboxes are great for running things like code interpreters: if you have an agent that uses python to perform data analysis, by all means, run it in a container - shabbosgoy runs great in a container, by the way, and you don't need to do any fancy configuration because it is capable of running as a canonical Unix tool, and in stateless, headless mode, there is no commentary or confirmation - the input comes from stdin, and the output is that of whatever action the agent chooses to take. `shabbosgoy` doesn't have any tools because it has ALL the tools - anything that's part of the linux distro or runs on the command line is part of its toolbox, just like it is for me and you (if you've read this far I imagine that you know how to use a command line). In fact, it has more tools than me or you, because most of us do not take the time to learn how to do everything in the terminal - we use a GUI, or we code a solution in the language of our choice.

But that is only the beginning: if you're following the trends in AI agents, I'm sure you are aware of multi-agent architectures that all tend to be similar: the engineer sets up several agents, each with a toolbox of related tools that let them perform certain types of tasks. Then he or she creates a hierarchy of these agents, thinking about the purpose of the overall system. And the agents can then invoke subordinate agents the way they would any other tool at their disposal.

These systems can be very good at completing tasks that they were designed for; and some frameworks like smolagents go farther, heavily emphasizing the user of *code* as a partial replacement for preset tools. But code interpretation often ends up being a drag, and its promise goes unrealized due to the headaches of things like dependencies and package installation. These agents are not designed for that purpose, and typically are given a preassigned set of package managers and system tools to choose from. Which works great until it doesn't - the models are not *quite* smart enough to make critical decisions like "shit, do i --break-system-packages or not" and thus either these agents require a human in the loop, or they are relegated to sandboxes and containers.

Where indeed, they can do many things that are very useful.

But they cannot put the finishing touches on your quest to make Ubuntu look and feel identical to Mac OS. shabbosgoy can. I was longing for 3 finger swipe gestures, and the most I had achieved myself was hours of wasted time and the ability to switch desktops. I hesitantly invoked the goy, who installed touchegg and wrote 50 lines of XML to configure this 3 finger swipe up gesture that every mac user knows and loves. I had to give sudo permission for it to change fundamental parts of the KDE configuration, which I did after I saw it had backed up the configs before asking. This, by the way, is something heavily encouraged in the system instructions for the agent - if you're doing something risky, do it on a copy of the original or back up the original first.

And it seems that those instructions mostly are heeded very well

shabbosgoy is not perfect. It sometimes gets overwhelmed when its actions fill its context with useless junk like apt-get installation logs, and that is something I would love to fix! The oly reason I have not is because I want to figure out a way of managing context that accurately determines what output is important to keep loaded in context, vs the other stuff which should be relegated to logfiles and accessible in case the agent needs to see it. (this is a whole other discussion and an ideal solution will involve a combination of agentic RAG and conventional RAG - striking that balance between accuracy and efficiency - its always more accurate for the agent to query a database knowing what it wants than to predictively retrieve the information based on vector search. But its less efficient, and takes more steps, which add overhead to the context and increase the cost of operating the agent.

So far we have been very pleasantly surprised by the low cost of doing tasks with `shabbosgoy` - compared to vibe coding, vibe devops is far leaner in that respect, due to the nature of the work more than anything. So I do not take full credit for this... most likely, a highly optimized solution will end up costing about the same, because we will save on tokens in the main context, but the retrieval process will use tokens of its own. Traditional RAG by itself is not going to add much value, and agentic RAG means querying LLMs to rationally consider which information is needed and when.

I believe we will solve this problem by introducing memory architectures powered largely by the latest and greatest small reasoning models, which finally make it possible to do high volume LLM queries at a minimal cost, and reasonably fast. But I cannot do this alone. So please, if you find this fascinating, hack on the repo a bit and put in a pull request.

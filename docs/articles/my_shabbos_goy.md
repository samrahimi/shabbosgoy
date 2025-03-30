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

But shabbosgoy did more than clone itself in its current state. You see, the tool may not be *designed* for vibe coding - its more of a vibe devops / sysadmin / root mah phone kinda agent. But it is certainly very capable of writing code and building small to medium sized apps, particularly command-line tools written in bash and/or Python.

And just for fun I decided to iteratively build shabbosgoy itself using shabbosgoy. Starting from an initial 50 line script to prove the concept, I used shabbosgoy to improve the code and give itself new features. Then I used the new and improved version to do the same. Eventually I had something stable that was easily installable via package manager and handled things like API keys in ways that were reasonably robust and secure. 

Could it have been done even easier with an agent designed specifically for app development? Most likely. But the point was not to bash this out in an hour - its a pretty simple concept and I could have created it in a few days by hand if vibe coding were not an option. I just wanted to see if it could be done. And for the most part, it could: it went from doing 80% of the development work at first to 95% by the firset stable release, and it saved me perhaps 75% of the time it would have taken to build by hand. Usually I can do even better than that with vibe coding agents, but not always.

This tells me that we are much closer to the Singularity and to ASI than most believe. Because once we reach AGI, an agent powered by the right model will be able to iteratively improve itself without human supervision. And the progressively larger productivity gains I experienced while using shabbosgoy to build shabbosgoy will be a much sharper curve, on a much shorter timelines - especially if the next generation of models are capable of iteratively improving their own capabilities. Its certainly not impossible to believe this will happen fairly soon: models already have the programming and analytical skills needed to set up training and data acquisition pipelines and to optimize them based on observed results. And I don't see any reason why a model could not supervise its own fine tuning. Consider, for a moment:

acc(p, M(p + k)) > acc(p, M(p)) when acc(p, p+k) > 0
acc(p, p) = 0       (always)
acc(p, M(p)) > 0    the output for any given prompt p is more accurate than simply echoing back p (duh) 


therefore, model inference function M produces a net gain in accuracy of output vs input (we hope!)
M(p) = 



 acc(p, p) - model accuracy with prompt + context > accuracy with prompt alone, assuming the context itself has a positive accuracy for that prompt. 

acc(p, p+k) > 0 
acc(p,p) = 0  //the prompt itself has a neutral accuracy score, as it does not add value vs the input because they are identical



. accuracy is an arbitrary scoring functio 
acc(M(p + k)) - acc(M(p)) = C(acc(p+k) - acc(p)) + E 

    :     model accuracy for prompt p improves when additional high quality context is provided
if follows that

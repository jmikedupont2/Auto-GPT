# What's Turbo

Turbo's an Auto-GTP v0.4.7 fork that adds the following enhancements:

#. Faster, cheaper GPT-4 support: 3X cheaper and 2X faster than the default Auto-GPT 0.4.7
#. Better pair coder: I use Auto-GPT to help with coding. The goal is to enable it to work on bigger, more complex software projects 
#. Multiple Personas: Choose the best "flavor" of Auto-GPT specialized for your task.
#. Multi-Agent support: Enables Auto-GPT to launch additional agents to complete specific tasks
#. Composability: easy way to create custom personas and prompts, and to pre-configure a multi-agent setup. I intend to provide some pre-configured setups for co-operation, adversity, various personalities, etc.

## Research

Some of these enhancements have come out of my desire to make it easier to setup and test various scenarios using Auto-GPT. My current area of interest are [multi-persona prompting](https://www.prompthub.us/blog/exploring-multi-persona-prompting-for-better-outputs), various multi-agent configurations and various memory extending techniques that do not involve third party software. I'm also exploring Auto-GPT as a conductor or orchestrator of other agents.

# Faster, cheaper GPT-4

GPT-4 is way more powerful than 3.5-turbo. It experiences fewer loops and JSON formating errors. It can handle more complex tasks and is better at logic. But, it's also 10X pricier, and no where near as fast as 3.5-turbo.

I believe GPT-4 shall become cheaper & faster over time, but until then, it needs all the help it can get :-D.

Turbo tries to squeeze every bit of time and cost saving out by testing various techniques including reducing verbosity of the command-json exchange 

# Better pair coding

GPT-4 is a very capable coder already. With some help from multiple agents, preset prompts and code, Turbo's trying to push the limit of how we can get Auto-GPT to product Product Specs, Documentation & actual working code.

I've added an examples folder that showcases some of the code output. More to come!

# Multiple Personas

This is an area of interest of mine. There are lots of recent papers on [multi-persona prompting](https://arxiv.org/pdf/2307.05300.pdf), and projects like [Synapse_COR](https://github.com/ProfSynapse/Synapse_CoR) which enables ChatGPT to call up (take on) various personalities within the same conversation. 
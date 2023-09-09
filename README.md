# What's Turbo

Turbo's an Auto-GTP v0.4.7 fork that adds various enhancements.

The current enhancements are focused on:

1/ Making GPT-4 faster & cheaper

GPT-4 is way more powerful than 3.5-turbo. Fewer loops, fewer JSON formating errors, more complex tasks, name it - But, it's also 10X pricier, and no where near as fast.

Turbo is 3X cheaper and 2X faster than the default Auto-GPT 0.4.7.

2/ Making Auto-GPT's prompts more accessible

It's astounding how much LLM behavior and agent performance can vary with different prompts. Turbo aims to make it easy for anyone to tweak Auto-GPT's prompts, and also comes with a growing library of pre-defined prompts for various tasks (aka personas or presets). 

3/ Making Auto-GPT mult-agent interactions more composable

Auto-GPT has more than oen inbuilt agents like a planner and executor, and more to come.

Turbo allows you to define any number of agents, and define their tasks, personas and roles. You can enable inter-agent communication, and can also allow Turbo agents to spin up other agents by replicating themselves or loading any of the preset agents.



 the cost of using GPT-4 3X over the default Auto-GPT 0.4.7, and is about 2X faster than the default Auto-GPT 0.4.7 (benchmark data coming soon)
Can we make it faster & cheaper? two go hand in hand. GPT-4's speed is greatly affected by the number of output tokens (input tokens do not affect speed as much)

2- GPT-4 (Currently, )
3- Lower cost for GPT-4

is the high-octane testing ground for experimental Auto-GPT features. Will these next-gen innovations race into Auto-GPT's lineup or get left in the dust?

[ [Setup Auto-GPT-Turbo](/turbo/docs/setup.md) | [Presets](/turbo/docs/presets.md) ]

## Revving Up Performance
- In gear with the latest stable Auto-GPT (v0.4.7)
- Precision-tuned with Auto-GPT-Benchmarks [link]
- Fueled by your drive – use, test, vote [link]

## The PitStop

What we're testing ...

### A. Presets

> _Customized AI roles, goals & settings for instant execution_

- turbo - The default. Enhanced for speed with one-shot responses and batch command execution.
- codezilla.planner - Transform a simple idea into a development plan - complete with requirements and data structures.
- codezilla.engineer - Evolve your development plan into a fully-integrated codebase.
- kerouac - Unleash your literary instincts and write like a seasoned novelist.
- madison - A haven for creativity and innovation.

Prompts can change the way the LLMs respond and ultimately make them more or less effective. Use presets to speed up your tasks,fulfill specialized tasks, or as examples of Auto-GPT's capabilities.

Presets are pre-configured roles, goals, and prompts that modify the LLM behavior. You can elevate your productivity with the packaged Presets or change them to create your own. The roadmap includes task-level auto-selection, goal-level perset switching, and the ability to save and share presets.

See [Presets](/turbo/docs/presets.md) for more details.

### B. Agent Orchestrator

> _Route jobs to The Best Agent :tm:_

Several impressive AI agent projects exist today, each with unique capabilities. 

Turbo Orchestrator leverages Auto-GPT-Benchmark data to route jobs to the most capable agent. Additionally, you can send your task to multiple agents and rate the results. Planned features include turning goals & results into portable benchmark challenges and feeding the human eval back to Auto-GPT-Benchmarks.

### Other Turbo Features

#### 1. Helicone support
- Enables LLM query caching and monitoring of LLM latency, costs, and benchmarks.

#### 2. Profiler support
- Turbo ships with configurable Wall & CPU profiling of benchmark runs and LLM cycles.

To be continued...

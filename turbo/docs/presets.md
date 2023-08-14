# Presets

> _Customized AI roles, goals & settings for instant execution_

- **turbo** - The default. Enhanced for speed with one-shot responses and batch command execution.
- **codezilla.planner** - Transform a simple idea into a development plan - complete with requirements and data structures.
- **codezilla.engineer** - Evolve your development plan into a fully-integrated codebase.
- **kerouac** (in development) - Unleash your literary instincts and write like a seasoned novelist.
- **madison** (in development) - A haven for creativity and innovation.

Prompts can change the way the LLMs respond and ultimately make them more or less effective. Use presets to speed up your tasks,fulfill specialized tasks, or as examples of Auto-GPT's capabilities.

Presets are pre-configured roles, goals, and prompts that modify the LLM behavior. You can elevate your productivity with the packaged Presets or change them to create your own. The roadmap includes task-level auto-selection, goal-level preset switching, and the ability to save and share presets.

## How to install Presets

To access Presets install Auto-GPT Turbo, then follow the instructions below to run Auto-GPT Turbo with a Preset.

See [Setting Up Auto-GPT-Turbo](/turbo/docs/setup.md) for installation instructions.

## How to use Presets

This feature adds 3 new options to the autogpt CLI; 
- `autogpt --preset <preset>` - Load the preset, overriding any name, role and goal settings.
- `autogpt --inherit-preset <preset>` - Inherit the preset prompts and behavior, but keep the current name, role and goal settings. 
- `autogpt --presets` - List the available presets.

For example, to use the `codezilla.planner` preset, run the following command:

```bash
python -m autogpt --preset codezilla.planner
```

or

```bash
./run.sh --preset codezilla.planner
```

## Preset Details

### turbo
Auto-GPT Turbo loads this preset by default. 
  - **Speed**: Compared to the base 0.4.7 profile, `turbo` is tuned for a balance between speed and efficiency. 

  - **One-shot responses**: It's more likely to give one-shot responses when it can, rather than do a web search for information that GPT-4 already knows.

  - **Batch command execution**: `turbo` is more likely to leverage Auto-GPT Turbo's batch command execution feature. 
  
    This feature anticipates the commands that will need to be run, and decides whether some of them can be run in one go. As a result, it can save time, system resources and money by reducing the number of API calls, and Agent cycles.

### codezilla.planner

Planning is the first step in the software development lifecycle. It's the process of defining the problem, identifying the requirements, and creating a development plan. 

`codezilla.planner` is optimized for this phase. It'll ask you questions about your idea, and then generate a development plan, which can be fed to `codezilla.engineer` to build out your project.

### codezilla.engineer

`codezilla.engineer` is optimized for the development phase. It expects to find the development plan produced by `codezilla.planner` in the workspace in a file named "3_specification.txt", and will generate code to implement the plan.

## Contributing

What Presets would you like to see? Is there a Preset you'd like to contribute?

Share your feedback on discord (@lc0rp), or by opening an issue on GitHub.




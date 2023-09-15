# Dolly - Cloner Plugin for Auto-GPT

Dolly is a plugin designed to extend Auto-GPT with multi-agent capabilities. With Dolly, Auto-GPT can spawn sub-agents that have similar functionalities to the main Auto-GPT instance. These agents can work in parallel to perform tasks, facilitating faster and more collaborative results.

## Compatibility
- **Optimized for**: `gpt-4-0314`
- **Variable Performance**: Results may differ when used with other GPT-4 models.
- **Contributions**: Pull Requests for optimization with other models are welcome.

## Future Roadmap
- Asynchronous, multi-threaded, and distributed modes are planned for future releases.

## Installation and Setup
This plugin is included in Turbo. Git clone the Turbo repository, or use one of Auto-GPT's installation methods.

## Commands

### 1. `clone_agent`
Creates a new agent with the same settings as the current agent but with new goals.

- **Usage**: In your goals, include phrases like "clone agent" or "clone yourself".
- **Parameters**: 
  - `goals` (list[str]): A list of tasks the new agent should focus on.

### 2. `create_bg_agent`
Creates a background agent that operates continuously.

- **Usage**: In your goals, include phrases like "create a background agent" or "create a non-interactive agent".
- **Parameters**: 
  - `name` (str): The name of the new agent.
  - `role_backstory_traits` (str): The role, history, and personality of the new agent.
  - `goals` (list[str]): A list of tasks for the agent.

### 3. `create_bg_agent_from_persona`
Creates a background agent based on a predefined persona.

- **Usage**: Include "Create a background agent with persona='<persona.name>'" in your goals.
- **Parameters**: 
  - `persona` (str): The desired persona.

### 4. `create_interactive_agent`
Creates an agent that operates in manual mode.

- **Parameters**: 
  - `name` (str): The name of the new agent.
  - `role_backstory_traits` (str): The role, history, and personality of the new agent.
  - `goals` (list[str]): A list of tasks for the agent.

## Help and Discussion
For further help and community discussions, join our [Discord Channel](https://discord.com/channels/1092243196446249134/1099609931562369024).

## Contributing
If you'd like to contribute, especially to make this plugin compatible with other GPT-4 models, please refer to the Contributing Guidelines.

## Changelog

### 0.3.0 - Sept 1 2023
- Rewritten from the ground up to work with Turbo (Auto-GPT 0.4.7)

### 0.2.0 - May 1 2023
- Personality Prompting
Dolly now lets you alter the clone personalities using the wellknown BIG 5 personality traits: AKA OCEAN: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism. See: Personality Prompting below.

- 'Act As' Attributes
Related, you can define a set of attributes for each clone - lazy, witty, talkative, anything goes.

- Better Monitoring
One key piece of feedback was that it was hard to see what each clone was doing. Now each clone gets their own output and erorr log files.
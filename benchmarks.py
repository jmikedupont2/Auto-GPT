from pathlib import Path

from autogpt.agents import Agent
from autogpt.app.main import construct_main_ai_config, run_interaction_loop
from autogpt.commands import COMMAND_CATEGORIES
from autogpt.config import AIConfig, ConfigBuilder
from autogpt.config.prompt_config import PromptConfig
from autogpt.memory.vector import get_memory
from autogpt.models.command_registry import CommandRegistry
from autogpt.prompts.prompt import DEFAULT_TRIGGERING_PROMPT
from autogpt.workspace import Workspace
from turbo.personas.manager import PersonaManager

PROJECT_DIR = Path().resolve()


def run_task(task) -> None:
    agent = bootstrap_agent(task)
    run_interaction_loop(agent)


def bootstrap_agent(task) -> Agent:
    prompt_settings_file = PersonaManager.load_prompts("turbo")

    config = ConfigBuilder.build_config_from_env(workdir=PROJECT_DIR)
    config.prompt_settings_file = prompt_settings_file
    config.debug_mode = True
    config.continuous_mode = False
    config.temperature = 0.2
    config.plain_output = True
    command_registry = CommandRegistry.with_command_modules(COMMAND_CATEGORIES, config)
    config.memory_backend = "no_memory"
    config.workspace_path = Workspace.init_workspace_directory(config)
    config.file_logger_path = Workspace.build_file_logger_path(config.workspace_path)

    ai_config = construct_main_ai_config(
        config,
        name="Auto-GPT-Turbo",
        role="a multi-purpose AI assistant that autonomously achieves its GOALS",
        goals=[task],
    )

    ai_config.command_registry = command_registry
    return Agent(
        memory=get_memory(config),
        command_registry=command_registry,
        ai_config=ai_config,
        config=config,
        triggering_prompt=PromptConfig(config.prompt_settings_file).triggering_prompt,
    )

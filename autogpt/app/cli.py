"""Main script for the autogpt package."""
from pathlib import Path
from typing import Optional

import click


@click.group(invoke_without_command=True)
@click.option("-c", "--continuous", is_flag=True, help="Enable Continuous Mode")
@click.option(
    "--skip-reprompt",
    "-y",
    is_flag=True,
    help="Skips the re-prompting messages at the beginning of the script",
)
@click.option(
    "--ai-settings",
    "-C",
    help=(
        "Specifies which ai_settings.yaml file to use, relative to the Auto-GPT"
        " root directory. Will also automatically skip the re-prompt."
    ),
)
@click.option(
    "--prompt-settings",
    "-P",
    help="Specifies which prompt_settings.yaml file to use.",
)
@click.option(
    "-l",
    "--continuous-limit",
    type=int,
    help="Defines the number of times to run in continuous mode",
)
@click.option("--speak", is_flag=True, help="Enable Speak Mode")
@click.option("--debug", is_flag=True, help="Enable Debug Mode")
@click.option("--gpt3only", is_flag=True, help="Enable GPT3.5 Only Mode")
@click.option("--gpt4only", is_flag=True, help="Enable GPT4 Only Mode")
@click.option(
    "--use-memory",
    "-m",
    "memory_type",
    type=str,
    help="Defines which Memory backend to use",
)
@click.option(
    "-b",
    "--browser-name",
    help="Specifies which web-browser to use when using selenium to scrape the web.",
)
@click.option(
    "--allow-downloads",
    is_flag=True,
    help="Dangerous: Allows Auto-GPT to download files natively.",
)
@click.option(
    "--skip-news",
    is_flag=True,
    help="Specifies whether to suppress the output of latest news on startup.",
)
@click.option(
    # TODO: this is a hidden option for now, necessary for integration testing.
    #   We should make this public once we're ready to roll out agent specific workspaces.
    "--workspace-directory",
    "-w",
    type=click.Path(),
    hidden=True,
)
@click.option(
    "--install-plugin-deps",
    is_flag=True,
    help="Installs external dependencies for 3rd party plugins.",
)
@click.option(
    "--ai-name",
    type=str,
    help="AI name override",
)
@click.option(
    "--ai-role",
    type=str,
    help="AI role override",
)
@click.option(
    "--ai-goal",
    type=str,
    multiple=True,
    help="AI goal override; may be used multiple times to pass multiple goals.",
)
@click.option(
    "--persona",
    "--preset",
    type=str,
    help="Load peset AI config Persona.",
)
@click.option(
    "--persona-prompts-only",
    "--preset-prompts-only",
    type=str,
    help="Load preset prompts, while enabling you to set your own AI name, role, and goals.",
)
@click.option(
    "--personas",
    "--presets",
    is_flag=True,
    default=True,
    help="List available AI config Personas and ask the user to choose one.",
)
@click.pass_context
def main(
    ctx: click.Context,
    continuous: bool,
    continuous_limit: int,
    ai_settings: str,
    prompt_settings: str,
    skip_reprompt: bool,
    speak: bool,
    debug: bool,
    gpt3only: bool,
    gpt4only: bool,
    memory_type: str,
    browser_name: str,
    allow_downloads: bool,
    skip_news: bool,
    workspace_directory: str,
    install_plugin_deps: bool,
    ai_name: Optional[str],
    ai_role: Optional[str],
    ai_goal: Optional[tuple[str]],
    persona: Optional[str],
    persona_prompts_only: Optional[str],
    personas: bool,
) -> None:
    """
    Welcome to AutoGPT an experimental open-source application showcasing the capabilities of the GPT-4 pushing the boundaries of AI.

    Start an Auto-GPT assistant.
    """
    # Put imports inside function to avoid importing everything when starting the CLI
    from autogpt.app.main import run_auto_gpt
    from turbo.personas import PersonaManager

    # Turbo: skip_news = True
    skip_news = True

    if persona:
        ai_settings, prompt_settings = PersonaManager.load(persona)
        ai_name = ai_role = ai_goal = None
        skip_reprompt = True

    elif persona_prompts_only:
        prompt_settings = PersonaManager.load_prompts(persona_prompts_only)

    # Default to turbo prompts
    if not (persona or persona_prompts_only or prompt_settings):
        prompt_settings = PersonaManager.load_prompts("turbo")
    else:
        personas = False  # Don't prompt for personas if we've selected one

    if ctx.invoked_subcommand is None:
        run_auto_gpt(
            continuous=continuous,
            continuous_limit=continuous_limit,
            ai_settings=ai_settings,
            prompt_settings=prompt_settings,
            skip_reprompt=skip_reprompt,
            speak=speak,
            debug=debug,
            gpt3only=gpt3only,
            gpt4only=gpt4only,
            memory_type=memory_type,
            browser_name=browser_name,
            allow_downloads=allow_downloads,
            skip_news=skip_news,
            working_directory=Path(
                __file__
            ).parent.parent.parent,  # TODO: make this an option
            workspace_directory=workspace_directory,
            install_plugin_deps=install_plugin_deps,
            ai_name=ai_name,
            ai_role=ai_role,
            ai_goals=ai_goal,
            personas=personas,
        )


if __name__ == "__main__":
    main()

from autogpt.config.config import Config
from autogpt.config.prompt_config import PromptConfig
from autogpt.prompts.generator import PromptGenerator

DEFAULT_TRIGGERING_PROMPT = (
    "1. Using available commands, work out all remaining steps to accomplish your goals, accounting for progress made so far. "
    "2. Consider whether consecutive commands can be executed at once. You can use '<prev_result>' to pass command outputs to the next command. "
    "3. Respond with the best list of commands to use. The list must have at least one command. Execution results shall be returned to you. "
    "4. Your response MUST use the JSON schema specified previously:"
)


def build_default_prompt_generator(config: Config) -> PromptGenerator:
    """
    This function generates a prompt string that includes various constraints,
        commands, resources, and best practices.

    Returns:
        str: The generated prompt string.
    """

    # Initialize the PromptGenerator object
    prompt_generator = PromptGenerator()

    # Initialize the PromptConfig object and load the file set in the main config (default: prompts_settings.yaml)
    prompt_config = PromptConfig(config.prompt_settings_file)

    # Add constraints to the PromptGenerator object
    for constraint in prompt_config.constraints:
        prompt_generator.add_constraint(constraint)

    # Add resources to the PromptGenerator object
    for resource in prompt_config.resources:
        prompt_generator.add_resource(resource)

    # Add best practices to the PromptGenerator object
    for best_practice in prompt_config.best_practices:
        prompt_generator.add_best_practice(best_practice)

    return prompt_generator

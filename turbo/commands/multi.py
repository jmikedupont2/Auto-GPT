"""Commands to perform operations on files"""

from __future__ import annotations

COMMAND_CATEGORY = "file_operations"
COMMAND_CATEGORY_TITLE = "File Operations"
from autogpt.agents.agent import Agent, execute_command
from autogpt.command_decorator import command


@command(
    "xcmds",
    "Efficiently execute many commands. Can use <prev_result> to pass command output to the next command, if necessary.",
    {
        "cmds": {
            "type": "list[{name: str, args: dict[str, object]}]",
            "description": "A list of command names (name) and their arguments (args).",
            "required": True,
        },
    },
    aliases=["exec_commands", "execute_commands", "exc_cmds"],
)
def execute_commands(cmds: list, agent: Agent) -> str:
    """Execute commands consecutively with no intervention.

    Args:
        commands (list): The commands to execute

    Returns:
        str: Execution results of each command as a numbered list
    """
    results = []
    prev_result = None
    for item in cmds:
        command_name = item["name"]
        command_args = item["args"]
        new_command_args = {}
        for arg in command_args:
            if prev_result is not None and isinstance(command_args[arg], str):
                new_command_args[arg] = command_args[arg].replace(
                    "<prev_result>", str(prev_result)
                )
            else:
                new_command_args[arg] = command_args[arg]
        result = execute_command(command_name, new_command_args, agent)

        if result is None:
            results.append((command_name, "Error: Unable to execute command."))
        else:
            results.append((command_name, result))

        prev_result = result

    return "\n##Execution Results:\n" + "\n".join(
        f"{i}. {command_name} returned: {result}"
        for i, (command_name, result) in enumerate(results, 1)
    )

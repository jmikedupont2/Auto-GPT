"""Commands to perform operations on files"""

from __future__ import annotations

COMMAND_CATEGORY = "file_operations"
COMMAND_CATEGORY_TITLE = "File Operations"
from autogpt.agents.agent import Agent, execute_command
from autogpt.command_decorator import command


@command(
    "exec",
    "Efficiently execute many commands. Can use <prev_output> to pass command output to the next command, if necessary.",
    {
        "cmds": {
            "type": "list[list[cmd, arg1, arg2...]]",
            "description": "A list of lists, each containing a command name as the first element and args as the rest of the elements.",
            "required": True,
        },
    },
    aliases=["exec_commands", "execute_commands", "exc_cmds"],
)
def execute_commands(*cmds: list, agent: Agent) -> str:
    """Execute commands consecutively with no intervention.

    Args:
        commands (list): The commands to execute

    Returns:
        str: Execution results of each command as a numbered list
    """
    results = []
    prev_output = None
    for item in cmds:
        command_name = item.pop(0)
        command_args = item
        new_command_args = [
            arg.replace("<prev_output>", str(prev_output))
            if prev_output is not None and isinstance(arg, str)
            else arg
            for arg in command_args
        ]
        result = execute_command(command_name, new_command_args, agent)

        if result is None:
            results.append((command_name, "Error: Unable to execute command."))
        else:
            results.append((command_name, result))

        prev_output = result

    return "\n## Results:\n" + "\n".join(
        f"{i}. '{command_name}' returned: {result}"
        for i, (command_name, result) in enumerate(results, 1)
    )

"""Commands to perform operations on files"""

from __future__ import annotations
from autogpt.command_decorator import command
from autogpt.agents.agent import Agent
from autogpt.memory.message_history import MessageHistory

COMMAND_CATEGORY = "system"
COMMAND_CATEGORY_TITLE = "System"

@command(
    "wipe",
    "Clear memory of all commands executed so far, with a note of the last command executed.",
    {
        "message": {
            "type": "string",
            "description": "The message to save in place of wiped memory.",
            "required": True,
        },
    },
    aliases=["wipe_memory", "clear_memory", "clear", "forget"],
)
def wipe(message: str, agent: Agent) -> str:
    """Wipe memory

    Args:
        message (str): The message to save in place of wiped memory.",

    Returns:
        str: Execution results of each command as a numbered list
    """
    message_summary = agent.history.trim_messages([], agent.config)
    agent.history = MessageHistory(
        agent.llm
    )
    agent.history.add_message(message_summary)
    return "MEMORY CHECKPOINT: " + message

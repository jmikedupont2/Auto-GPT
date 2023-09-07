"""Commands to execute code"""

COMMAND_CATEGORY = "system"
COMMAND_CATEGORY_TITLE = "System"

import contextlib
import hashlib
import io
import os
import subprocess
import sys
from pathlib import Path
from colorama import Fore

import docker
from docker.errors import DockerException, ImageNotFound
from docker.models.containers import Container as DockerContainer

from autogpt.agents.agent import Agent
from autogpt.command_decorator import command
from autogpt.config import Config
from autogpt.logs import logger

from autogpt.commands.decorators import run_in_workspace, sanitize_path_arg

TIMEOUT_SECONDS: int = 900
PAUSE_SECONDS: int = 10

@command(
    "ask",
    "Ask user a series of questions <qs>. Interactive.",
    {
        "qs": {
            "type": "list[str]",
            "description": "The questions to ask the user.",
            "required": True,
        }
    },
    aliases=["ask_user"],
)
def ask_user(qs: list[str], agent: Agent) -> list[str]:
    """Ask the user a series of prompts and return the responses

    Args:
        qs (list[str]): The prompts to ask the user
        agent (Agent): The agent that is executing the command

    Returns:
        list[str]: The responses from the user
    """
    from pytimedinput import timedInput
    
    results = []
    for prompt in qs:
        prompt = (
            f"{Fore.CYAN}"
            "\n================================================================\n"
            f"{prompt}:"
            "\n> "
        )
        response, timedout = timedInput(prompt, timeout=TIMEOUT_SECONDS, resetOnInput=False)
        if response:
            results.append(response)
        if timedout:
            results.append(f"Timed out after {TIMEOUT_SECONDS} seconds.")
            break
    return results

@command(
    "tell",
    "Show <text> to user. Non-interactive.",
    {
        "text": {
            "type": "str",
            "description": "The text to say.",
            "required": True,
        }
    },
    aliases=["tell_user"],
)
def tell(text: str, agent: Agent) -> str:
    """Show text to the user

    Args:
        text (str): The text to say
        agent (Agent): The agent that is executing the command

    Returns:
        str: The key that was pressed, or an error message
    """
    from pytimedinput import timedKey
    
    prompt = (
        f"{Fore.CYAN}"
        "\n================================================================\n"
        f"{text}"
        "\nPress any key to continue..."
        "\n================================================================\n"
    )
    response, timedout = timedKey(prompt=prompt, resetOnInput=False, timeout=PAUSE_SECONDS)
    return None
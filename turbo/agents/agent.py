from __future__ import annotations

import json
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from autogpt.config import AIConfig, Config
    from autogpt.llm.base import ChatModelResponse, ChatSequence
    from autogpt.memory.vector import VectorMemory
    from autogpt.models.command_registry import CommandRegistry

from autogpt.json_utils.utilities import extract_dict_from_response, validate_dict
from autogpt.llm.api_manager import ApiManager
from autogpt.llm.base import Message
from autogpt.llm.utils import count_string_tokens
from autogpt.logs import logger
from autogpt.logs.log_cycle import (
    CURRENT_CONTEXT_FILE_NAME,
    FULL_MESSAGE_HISTORY_FILE_NAME,
    NEXT_ACTION_FILE_NAME,
    USER_INPUT_FILE_NAME,
    LogCycleHandler,
)
from autogpt.workspace import Workspace

from autogpt.agents.agent import Agent
from .base import TurboBaseAgent, CommandName

class TurboAgent(Agent, TurboBaseAgent):
    """Auto-GPT Turbo Agent."""

    def parse_and_process_response(
        self, llm_response: ChatModelResponse, *args, **kwargs
    ) -> tuple[list[tuple[CommandName | None, CommandArgs | None]], AgentThoughts]:
        if not llm_response.content:
            raise SyntaxError("Assistant response has no text content")

        assistant_reply_dict = extract_dict_from_response(llm_response.content)

        valid, errors = validate_dict(assistant_reply_dict, self.config)
        if not valid:
            raise SyntaxError(
                "Validation of response failed:\n  "
                + ";\n  ".join([str(e) for e in errors])
            )

        for plugin in self.config.plugins:
            if not plugin.can_handle_post_planning():
                continue
            assistant_reply_dict = plugin.post_planning(assistant_reply_dict)

        response = (None, None), assistant_reply_dict

        # Print Assistant thoughts
        if assistant_reply_dict != {}:
            # Get command name and arguments
            try:
                commands = extract_commands(
                    assistant_reply_dict, llm_response, self.config
                )
                response = commands, assistant_reply_dict
            except Exception as e:
                logger.error("Error: \n", str(e))

        self.log_cycle_handler.log_cycle(
            self.ai_config.ai_name,
            self.created_at,
            self.cycle_count,
            assistant_reply_dict,
            NEXT_ACTION_FILE_NAME,
        )
        return response


def extract_commands(
    assistant_reply_json: dict, assistant_reply: ChatModelResponse, config: Config
) -> list[tuple[str, dict[str, str]]]:
    """Parse the response and return the command name and arguments

    Args:
        assistant_reply_json (dict): The response object from the AI
        assistant_reply (ChatModelResponse): The model response from the AI
        config (Config): The config object

    Returns:
        tuple: The command name and arguments

    Raises:
        json.decoder.JSONDecodeError: If the response is not valid JSON

        Exception: If any other error occurs
    """
    if config.openai_functions:
        if assistant_reply.function_call is None:
            return "Error:", {"message": "No 'function_call' in assistant reply"}
        assistant_reply_json["command"] = {
            "name": assistant_reply.function_call.name,
            "args": json.loads(assistant_reply.function_call.arguments),
        }
    try:
        if "commands" not in assistant_reply_json:
            return "Error:", {"message": "Missing 'command' object in JSON"}

        if not isinstance(assistant_reply_json, dict):
            return (
                "Error:",
                {
                    "message": f"The previous message sent was not a dictionary {assistant_reply_json}"
                },
            )

        commands = assistant_reply_json["commands"]
        if not isinstance(commands, list):
            return "Error:", {"message": "'commands' object is not a list"}

        parsed_commands = []
        for command in commands:
            if not isinstance(command, dict):
                return "Error:", {"message": "'command' object is not a dictionary"}

            if "name" not in command:
                return "Error:", {"message": "Missing 'name' field in 'command' object"}

            command_name = command["name"]

            # Use an empty dictionary if 'args' field is not present in 'command' object
            arguments = command.get("args", {})

            parsed_commands.append((command_name, arguments))

        return parsed_commands
    except json.decoder.JSONDecodeError:
        return [("Error:", {"message": "Invalid JSON"})]
    # All other errors, return "Error: + error message"
    except Exception as e:
        return [("Error:", {"message": str(e)})]

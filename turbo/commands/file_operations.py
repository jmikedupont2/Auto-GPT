"""Commands to perform operations on files"""

from __future__ import annotations

from autogpt.commands.decorators import sanitize_path_arg

COMMAND_CATEGORY = "file_operations"
COMMAND_CATEGORY_TITLE = "File Operations"
from autogpt.agents.agent import Agent
from autogpt.command_decorator import command

@command(
    "write_to_file",
    "Writes to a file. if_exists: prepend, append, overwrite, skip or fail.",
    {
        "filename": {
            "type": "string",
            "description": "The name of the file to write to",
            "required": True,
        },
        "text": {
            "type": "string",
            "description": "The text to write to the file",
            "required": True,
        },
        "if_exists": {
            "type": "string",
            "description": "One of 'overwrite', 'prepend', 'append', 'skip' or 'fail'",
            "required": True,
        },
    },
    aliases=["write_file", "create_file"],
)
@sanitize_path_arg("filename")
def write_to_file(filename: str, text: str, if_exists: str, agent: Agent) -> str:
    """Write text to a file

    Args:
        filename (str): The name of the file to write to
        text (str): The text to write to the file
        if_exists (str): One of 'overwrite', 'prepend', 'append', 'skip' or 'fail'

    Returns:
        str: A message indicating success or failure
    """
    ACTIONS = {
        "overwrite": lambda p, _txt: p.write_text(_txt, encoding="utf-8"),
        "prepend": lambda p, _txt: p.write_text(_txt + p.read_text(encoding="utf-8")),
        "append": lambda p, _txt: open(p, "a", encoding="utf-8").write(_txt),
        "skip": (
            lambda p, _txt: "File exists, skipping."
            if p.exists()
            else p.write_text(_txt, encoding="utf-8")
        ),
        "fail": (
            lambda p, _txt: "Error: File exists, failing."
            if p.exists()
            else p.write_text(_txt, encoding="utf-8")
        ),
    }

    checksum = text_checksum(text)
    if is_duplicate_operation("write", filename, agent, checksum):
        return "Error: File has already been updated."

    path = Path(filename)
    directory = path.parent
    os.makedirs(directory, exist_ok=True)

    try:
        result = ACTIONS.get(
            if_exists, lambda p, _txt: "Error: Invalid value for 'if_exists'."
        )(path, text)

        if isinstance(result, str):  # If the result is a string, return it
            return result

        return "File written to successfully."
    except Exception as err:
        return f"Error: {err}"
    finally:
        log_operation("write", filename, agent, checksum)

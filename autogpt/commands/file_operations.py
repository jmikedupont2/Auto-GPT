"""Commands to perform operations on files"""

from __future__ import annotations

from enum import Enum

COMMAND_CATEGORY = "file_operations"
COMMAND_CATEGORY_TITLE = "File Operations"

import contextlib
import hashlib
import os
import os.path
from pathlib import Path
from typing import Generator, Literal, Optional

from autogpt.agents.agent import Agent
from autogpt.command_decorator import command
from autogpt.logs import logger
from autogpt.memory.vector import MemoryItem, VectorMemory

from .decorators import sanitize_path_arg
from .file_operations_utils import read_textual_file


class Operations(Enum):
    WRITE = "write"
    APPEND = "append"
    DELETE = "delete"


Operation = Literal["write", "append", "delete"]


def text_checksum(text: str) -> str:
    """Get the hex checksum for the given text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def operations_from_log(
    log_path: str | Path,
) -> Generator[tuple[Operation, str, Optional[str]], None, None,]:
    """Parse the file operations log and return a tuple containing the log entries"""
    try:
        log = open(log_path, "r", encoding="utf-8")
    except FileNotFoundError:
        return

    for line in log:
        line = line.replace("File Operation Logger", "").strip()
        if not line:
            continue
        operation, tail = line.split(": ", maxsplit=1)
        operation = operation.strip()
        if operation in (Operations.WRITE.value, Operations.APPEND.value):
            try:
                path, checksum = (x.strip() for x in tail.rsplit(" #", maxsplit=1))
            except ValueError:
                logger.warn(f"File log entry lacks checksum: '{line}'")
                path, checksum = tail.strip(), None
            yield (Operations[operation.upper()].value, path, checksum)
        elif operation == "delete":
            yield (Operations.DELETE.value, tail.strip(), None)

    log.close()


def file_operations_state(log_path: str | Path) -> dict[str, Optional[str]]:
    """Iterates over the operations log and returns the expected state.

    Parses a log file at config.file_logger_path to construct a dictionary that maps
    each file path written or appended to its checksum. Deleted files are removed
    from the dictionary.

    Returns:
        A dictionary mapping file paths to their checksums.

    Raises:
        FileNotFoundError: If config.file_logger_path is not found.
        ValueError: If the log file content is not in the expected format.
    """
    state = {}
    for operation, path, checksum in operations_from_log(log_path):
        if operation in ("write", "append"):
            state[path] = checksum
        elif operation == "delete":
            del state[path]
    return state


@sanitize_path_arg("filename")
def is_duplicate_operation(
    operation: Operation, filename: str, agent: Agent, checksum: str | None = None
) -> bool:
    """Check if the operation has already been performed

    Args:
        operation: The operation to check for
        filename: The name of the file to check for
        agent: The agent
        checksum: The checksum of the contents to be written

    Returns:
        True if the operation has already been performed on the file
    """
    # Make the filename into a relative path if possible
    with contextlib.suppress(ValueError):
        filename = str(Path(filename).relative_to(agent.workspace.root))

    state = file_operations_state(agent.config.file_logger_path)
    if operation == "delete" and filename not in state:
        return True
    if operation == "write" and state.get(filename) == checksum:
        return True
    return False


@sanitize_path_arg("filename")
def log_operation(
    operation: Operation, filename: str, agent: Agent, checksum: str | None = None
) -> None:
    """Log the file operation to the file_logger.txt

    Args:
        operation: The operation to log
        filename: The name of the file the operation was performed on
        checksum: The checksum of the contents to be written
    """
    # Make the filename into a relative path if possible
    with contextlib.suppress(ValueError):
        filename = str(Path(filename).relative_to(agent.workspace.root))

    log_entry = f"{operation}: {filename}"
    if checksum is not None:
        log_entry += f" #{checksum}"
    logger.debug(f"Logging file operation: {log_entry}")
    append_to_file(
        agent.config.file_logger_path, f"{log_entry}\n", agent, should_log=False
    )


@command(
    "read_file",
    "Return <file> contents.",
    {
        "file": {
            "type": "string",
            "description": "The path of the file to read",
            "required": True,
        }
    },
    aliases=[
        "read", "read_file", "cat"
    ],
)
@sanitize_path_arg("file")
def read_file(file: str, agent: Agent) -> str:
    """Read a file and return the contents

    Args:
        file (str): The name of the file to read

    Returns:
        str: The contents of the file
    """
    try:
        content = read_textual_file(file, logger)

        # TODO: invalidate/update memory when file is edited
        file_memory = MemoryItem.from_text_file(content, file, agent.config)
        if len(file_memory.chunks) > 1:
            return file_memory.summary
        
        return f"{Path(file).name} contents:\n" + content
    except Exception as e:
        return f"Error: {str(e)}"


def ingest_file(
    filename: str,
    memory: VectorMemory,
) -> None:
    """
    Ingest a file by reading its content, splitting it into chunks with a specified
    maximum length and overlap, and adding the chunks to the memory storage.

    Args:
        filename: The name of the file to ingest
        memory: An object with an add() method to store the chunks in memory
    """
    try:
        logger.info(f"Ingesting file {filename}")
        content = read_file(filename)

        # TODO: differentiate between different types of files
        file_memory = MemoryItem.from_text_file(content, filename)
        logger.debug(f"Created memory: {file_memory.dump(True)}")
        memory.add(file_memory)

        logger.info(f"Ingested {len(file_memory.e_chunks)} chunks from {filename}")
    except Exception as err:
        logger.warn(f"Error while ingesting file '{filename}': {err}")


@command(
    "write_file",
    "Overwrite <file> with <text>.",
    {
        "file": {
            "type": "string",
            "description": "The name of the file to write to",
            "required": True,
        },
        "text": {
            "type": "string",
            "description": "The text to write to the file",
            "required": True,
        },
    },
    aliases=["write_to_file", "write", "create_file", "put"],
)
@sanitize_path_arg("file")
def write_to_file(file: str, text: str, agent: Agent) -> str:
    """Write text to a file

    Args:
        file (str): The name of the file to write to
        text (str): The text to write to the file

    Returns:
        str: A message indicating success or failure
    """
    checksum = text_checksum(text)
    if is_duplicate_operation("write", file, agent, checksum):
        return "Info: File has already been updated. Change the text to write to update the file."
    try:
        directory = os.path.dirname(file)
        os.makedirs(directory, exist_ok=True)
        with open(file, "w", encoding="utf-8") as _f:
            _f.write(text)
        log_operation("write", file, agent, checksum)
        return "Successful."
    except Exception as err:
        return f"Error: {err}"


@sanitize_path_arg("filename")
def append_to_file(
    filename: str, text: str, agent: Agent, should_log: bool = True
) -> str:
    """Append text to a file

    Args:
        filename (str): The name of the file to append to
        text (str): The text to append to the file
        should_log (bool): Should log output

    Returns:
        str: A message indicating success or failure
    """
    try:
        directory = os.path.dirname(filename)
        os.makedirs(directory, exist_ok=True)
        with open(filename, "a", encoding="utf-8") as f:
            f.write(text)

        if should_log:
            with open(filename, "r", encoding="utf-8") as f:
                checksum = text_checksum(f.read())
            log_operation("append", filename, agent, checksum=checksum)

        return "Text appended successfully."
    except Exception as err:
        return f"Error: {err}"


@command(
    "list_files",
    "List files in <dir> recursively.",
    {
        "dir": {
            "type": "string",
            "description": "The directory to list files in",
            "required": True,
        }
    },
    aliases=["list", "ls"],
)
@sanitize_path_arg("dir")
def list_files(dir: str, agent: Agent) -> list[str]:
    """lists files in a directory recursively

    Args:
        dir (str): The directory to search in

    Returns:
        list[str]: A list of files found in the directory
    """
    found_files = []

    for root, _, files in os.walk(dir):
        for file in files:
            if file.startswith("."):
                continue
            relative_path = os.path.relpath(
                os.path.join(root, file), agent.config.workspace_path
            )
            found_files.append(relative_path)

    return found_files

"""Commands to execute code"""

COMMAND_CATEGORY = "execute_code"
COMMAND_CATEGORY_TITLE = "Execute Code"

import contextlib
import hashlib
import io
import os
import subprocess
import sys
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound
from docker.models.containers import Container as DockerContainer

from autogpt.agents.agent import Agent
from autogpt.command_decorator import command
from autogpt.config import Config
from autogpt.logs import logger

from .decorators import run_in_workspace, sanitize_path_arg

ALLOWLIST_CONTROL = "allowlist"
DENYLIST_CONTROL = "denylist"
TIMEOUT_SECONDS: int = 900
PAUSE_SECONDS: int = 10


@command(
    name="execute_python_code",
    description="Exec() Python <code> str, return STDOUT,STDERR",
    parameters={
        "code": {
            "type": "string",
            "description": "The Python code to execute",
            "required": True,
        },
    },
    aliases=["exec_python_code", "py"],
)
def execute_python_code(code: str, agent: Agent) -> str:
    """Execute a string Python <code> using exec() and return the STDOUT output.

    Args:
        code (str): The Python code to run
        agent (Agent): The agent that is executing the command

    Returns:
        str: The STDOUT captured from the code when it ran
    """
    if we_are_running_in_a_docker_container():
        logger.debug("Running in a Docker container; executing the code directly...")
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(code)
            return output.getvalue()
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        logger.debug("Not running in a Docker container")

        ai_name = agent.ai_config.ai_name
        code_dir = agent.workspace.get_path(Path(ai_name, "executed_code"))
        os.makedirs(code_dir, exist_ok=True)

        # The `name` arg is not covered by @sanitize_path_arg,
        # so sanitization must be done here to prevent path traversal.
        hash_object = hashlib.md5()
        hash_object.update(code.encode("utf-8"))
        file = hash_object.hexdigest() + ".py"
        file_path = agent.workspace.get_path(code_dir / file)
        if not file_path.is_relative_to(code_dir):
            return "Error: 'filename' argument resulted in path traversal, operation aborted."

        try:
            with open(file_path, "w+", encoding="utf-8") as f:
                f.write(code)

            return execute_python_file(str(file_path), agent)
        except Exception as e:
            return f"Error: {str(e)}"


@command(
    "execute_python_file",
    "Exec 'python <path>' (must end in .py), return STDOUT,STDERR",
    {
        "path": {
            "type": "string",
            "description": "The file path execute",
            "required": True,
        },
    },
    aliases=["pyf", "exec_python_file"],
)
@sanitize_path_arg("path")
def execute_python_file(path: str, agent: Agent) -> str:
    """Execute a Python file in a Docker container and return the output

    Args:
        path (str): The name of the file to execute
        agent (Agent): The agent that is executing the command

    Returns:
        str: The output of the file
    """
    logger.info(
        f"Executing python file '{path}' in working directory '{agent.config.workspace_path}'"
    )

    if not path.endswith(".py"):
        return "Error: Invalid file type. Only .py files are allowed."

    # If we're in continuous mode, check that the file doesn't contain interactive commands
    if agent.config.continuous_mode:
        with open(path, "r") as f:
            file_contents = f.read()
        if "input(" in file_contents:
            return f"Error: {path} contains interactive commands. The current automated execution mode cannot accept user inputs. Try another command."

    file_path = Path(path)
    if not file_path.is_file():
        # Mimic the response that you get from the command line so that it's easier to identify
        return f"python: can't open file '{path}': [Errno 2] No such file or directory"

    if we_are_running_in_a_docker_container():
        logger.debug(
            f"Running in a Docker container; executing {file_path} directly..."
        )
        result = subprocess.run(
            ["python", str(file_path)],
            capture_output=True,
            encoding="utf8",
            cwd=agent.config.workspace_path,
        )
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"

    logger.debug("Not running in a Docker container")
    try:
        client = docker.from_env()
        # You can replace this with the desired Python image/version
        # You can find available Python images on Docker Hub:
        # https://hub.docker.com/_/python
        image_name = "python:3-alpine"
        try:
            client.images.get(image_name)
            logger.debug(f"Image '{image_name}' found locally")
        except ImageNotFound:
            logger.info(
                f"Image '{image_name}' not found locally, pulling from Docker Hub..."
            )
            # Use the low-level API to stream the pull response
            low_level_client = docker.APIClient()
            for line in low_level_client.pull(image_name, stream=True, decode=True):
                # Print the status and progress, if available
                status = line.get("status")
                progress = line.get("progress")
                if status and progress:
                    logger.info(f"{status}: {progress}")
                elif status:
                    logger.info(status)

        logger.debug(f"Running {file_path} in a {image_name} container...")
        container: DockerContainer = client.containers.run(
            image_name,
            [
                "python",
                file_path.relative_to(agent.workspace.root).as_posix(),
            ],
            volumes={
                str(agent.config.workspace_path): {
                    "bind": "/workspace",
                    "mode": "rw",
                }
            },
            working_dir="/workspace",
            stderr=True,
            stdout=True,
            detach=True,
        )  # type: ignore

        container.wait()
        logs = container.logs().decode("utf-8")
        container.remove()

        # print(f"Execution complete. Output: {output}")
        # print(f"Logs: {logs}")

        return logs

    except DockerException as e:
        logger.warn(
            "Could not run the script in a container. If you haven't already, please install Docker https://docs.docker.com/get-docker/"
        )
        return f"Error: {str(e)}"

    except Exception as e:
        return f"Error: {str(e)}"


def validate_command(command: str, config: Config) -> bool:
    """Validate a command to ensure it is allowed

    Args:
        command (str): The command to validate
        config (Config): The config to use to validate the command

    Returns:
        bool: True if the command is allowed, False otherwise
    """
    if not command:
        return False

    command_name = command.split()[0]

    if config.shell_command_control == ALLOWLIST_CONTROL:
        return command_name in config.shell_allowlist
    else:
        return command_name not in config.shell_denylist


@command(
    "execute_shell_command",
    "Exec non-interactive shell cmd string (<cmd>), return STDOUT,STDERR",
    {
        "cmd": {
            "type": "string",
            "description": "The command line to execute",
            "required": True,
        }
    },
    enabled=lambda config: config.execute_local_commands,
    disabled_reason="You are not allowed to run local shell commands. To execute"
    " shell commands, EXECUTE_LOCAL_COMMANDS must be set to 'True' "
    "in your config file: .env - do not attempt to bypass the restriction.",
    aliases=["sh", "exec_shell"],
)
@run_in_workspace
def execute_shell(cmd: str, agent: Agent) -> str:
    """Execute a shell command and return the output

    Args:
        cmd (str): The command line to execute
        agent (Agent): The agent that is executing the command

    Returns:
        str: The output of the command
    """
    if not validate_command(cmd, agent.config):
        logger.info(f"Command '{cmd}' not allowed")
        return "Error: This Shell Command is not allowed."

    logger.info(f"Executing command '{cmd}' in working directory '{os.getcwd()}'")

    result = subprocess.run(cmd, capture_output=True, shell=True)
    output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    logger.debug(f"output: {output}")
    return output


@command(
    "execute_shell_popen",
    "Executes a Shell Command, non-interactive commands only",
    {
        "command_line": {
            "type": "string",
            "description": "The command line to execute",
            "required": True,
        }
    },
    enabled=False,  # old: lambda config: config.execute_local_commands,
    disabled_reason="You are not allowed to run local shell commands. To execute"
    " shell commands, EXECUTE_LOCAL_COMMANDS must be set to 'True' "
    "in your config. Do not attempt to bypass the restriction.",
)
@run_in_workspace
def execute_shell_popen(command_line: str, agent: Agent) -> str:
    """Execute a shell command with Popen and returns an english description
    of the event and the process id

    Args:
        command_line (str): The command line to execute
        agent (Agent): The agent that is executing the command

    Returns:
        str: Description of the fact that the process started and its id
    """
    if not validate_command(command_line, agent.config):
        logger.info(f"Command '{command_line}' not allowed")
        return "Error: This Shell Command is not allowed."

    logger.info(
        f"Executing command '{command_line}' in working directory '{os.getcwd()}'"
    )

    do_not_show_output = subprocess.DEVNULL
    process = subprocess.Popen(
        command_line, shell=True, stdout=do_not_show_output, stderr=do_not_show_output
    )

    return f"Subprocess started with PID:'{str(process.pid)}'"


def we_are_running_in_a_docker_container() -> bool:
    """Check if we are running in a Docker container

    Returns:
        bool: True if we are running in a Docker container, False otherwise
    """
    return os.path.exists("/.dockerenv")


@command(
    "execute_interactive_shell",
    "Executes a Shell Command that needs interactivity and return the output.",
    {
        "command_line": {
            "type": "string",
            "description": "The command line to execute",
            "required": True,
        }
    },
    lambda config: config.execute_local_commands and not config.continuous_mode,
    "Either the agent is running in continuous mode, or "
    "you are not allowed to run local shell commands. To execute"
    " shell commands, EXECUTE_LOCAL_COMMANDS must be set to 'True' "
    "in your config file: .env - do not attempt to bypass the restriction.",
)
@run_in_workspace
def execute_interactive_shell(command_line: str, agent: Agent) -> list[dict]:
    """Execute a shell command that requires interactivity and return the output.

    Args:
        command_line (str): The command line to execute
        agent (Agent): The agent that is executing the command

    Returns:
        list[dict]: The interaction between the user and the process,
        as a list of dictionaries:
        [
            {
                role: "user"|"system"|"error",
                content: "The content of the interaction."
            },
            ...
        ]
    """
    if not validate_command(command_line, agent.config):
        logger.info(f"Command '{command_line}' not allowed")
        return [{"role": "error", "content": "This Shell Command isn't allowed."}]

    if sys.platform == "win32":
        conversation = _exec_cross_platform(command_line)
    else:
        conversation = _exec_linux(command_line)

    return conversation


def _exec_linux(command_line: str) -> list[dict]:
    """
    Execute a linux shell command and return the output.

    Args:
        command_line (str): The command line to execute

    Returns:
        list[dict]: The interaction between the user and the process,
        as a list of dictionaries:
        [
            {
                role: "user"|"system"|"error",
                content: "The content of the interaction."
            },
            ...
        ]
    """
    import select

    process = subprocess.Popen(
        command_line,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # To capture the conversation, we'll read from one set of descriptors, save the output and write it to the other set descriptors.
    fd_map = {
        process.stdout.fileno(): ("system", sys.stdout.buffer),
        process.stderr.fileno(): ("error", sys.stderr.buffer),
        sys.stdin.fileno(): ("user", process.stdin),  # Already buffered
    }

    conversation = []

    while True:
        read_fds, _, _ = select.select(list(fd_map.keys()), [], [])
        input_fd = next(fd for fd in read_fds if fd in fd_map)
        role, output_buffer = fd_map[input_fd]

        input_buffer = os.read(input_fd, 1024)
        if input_buffer == b"":
            break
        output_buffer.write(input_buffer)
        output_buffer.flush()
        content = input_buffer.decode("utf-8")
        content = (
            content.replace("\r", "").replace("\n", " ").strip() if content else ""
        )
        conversation.append({"role": role, "content": content})

    try:
        process.wait(timeout=TIMEOUT_SECONDS)
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
    except subprocess.TimeoutExpired:
        conversation.append(
            {"role": "error", "content": f"Timed out after {TIMEOUT_SECONDS} seconds."}
        )

    return conversation


def _exec_cross_platform(command_line: str) -> list[dict]:
    """
    Execute a shell command that requires interactivity and return the output.
    This can also work on linux, but is less native than the other function.

    Args:
        command_line (str): The command line to execute
        agent (Agent): The agent that is executing the command

    Returns:
        list[dict]: The interaction between the user and the process,
        as a list of dictionaries:
        [
            {
                role: "user"|"system"|"error",
                content: "The content of the interaction."
            },
            ...
        ]
    """
    from sarge import Capture, Command

    command = Command(
        command_line,
        stdout=Capture(buffer_size=1),
        stderr=Capture(buffer_size=1),
    )
    command.run(input=subprocess.PIPE, async_=True)

    # To capture the conversation, we'll read from one set of descriptors,
    # save the output and write it to the other set descriptors.
    fd_map = {
        command.stdout: ("system", sys.stdout.buffer),
        command.stderr: ("error", sys.stderr.buffer),
    }

    conversation = []

    while True:
        output = {fd: fd.read(timeout=0.1) for fd in fd_map.keys()}
        if not any(output.values()):
            break

        content = ""
        for fd, output_content in output.items():
            if output_content:
                output_content = (
                    output_content + b"\n"
                    if not output_content.endswith(b"\n")
                    else output_content
                )
                fd_map[fd][1].write(output_content)
                fd_map[fd][1].flush()

                content = output_content.decode("utf-8")
                content = (
                    content.replace("\r", "").replace("\n", " ").strip()
                    if content
                    else ""
                )
                conversation.append({"role": fd_map[fd][0], "content": content})

        if any(output.values()):
            prompt = "Response [None]: "
            os.write(sys.stdout.fileno(), prompt.encode("utf-8"))
            stdin = os.read(sys.stdin.fileno(), 1024)
            if stdin != b"":
                try:
                    command.stdin.write(stdin)
                    command.stdin.flush()
                    content = stdin.decode("utf-8")
                    content = (
                        content.replace("\r", "").replace("\n", " ").strip()
                        if content
                        else ""
                    )
                    conversation.append({"role": "user", "content": content})
                except (BrokenPipeError, OSError):
                    # Child process already exited
                    print("Command exited... returning.")

    try:
        command.wait(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        conversation.append(
            {"role": "error", "content": f"Timed out after {TIMEOUT_SECONDS} seconds."}
        )

    return conversation

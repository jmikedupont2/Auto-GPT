"""
Tests for the InteractiveShellCommands class.
"""
from unittest.mock import patch


def test_ask_user() -> None:
    """Test that the ask_user method returns the expected responses."""
    prompts = ["Question 1: ", "Question 2: ", "Question 3: "]
    expected_responses = ["Answer 1", "Answer 2", "Answer 3"]
    with patch("inputimeout.inputimeout", side_effect=expected_responses):
        responses = sut.ask_user(prompts)

    assert (
        responses == expected_responses
    ), f"Expected {expected_responses} but got {responses}"


def test_ask_user_timeout() -> None:
    """Test that the ask_user method returns the expected responses when a timeout occurs."""
    prompts = ["Prompt 1:"]
    timeout = 900

    from inputimeout import TimeoutOccurred

    with patch("inputimeout.inputimeout", side_effect=TimeoutOccurred):
        responses = sut.ask_user(prompts, timeout)

    assert responses == [f"Timed out after {timeout} seconds."]

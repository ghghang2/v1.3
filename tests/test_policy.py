"""Tests for the simple policy hook.
"""

import pytest

import os
import sys
# Ensure the repository root is on sys.path for imports.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.agent import AgentEvent
from app.policy import should_interject


@pytest.mark.parametrize(
    "content,expected",
    [
        ("This is fine", False),
        ("There was an error in the calculation", True),
        ("I made a mistake on the previous step", True),
        ("No issues", False),
    ],
)
def test_should_interject(content: str, expected: bool) -> None:
    event = AgentEvent(role="assistant", content=content)
    assert should_interject(event) is expected

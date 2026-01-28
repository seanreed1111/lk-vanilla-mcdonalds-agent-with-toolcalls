"""Unit tests for ConversationLogger."""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from conversation_logger import ConversationLogger


@pytest.fixture
def temp_logs_dir(tmp_path):
    """Create temporary logs directory."""
    return str(tmp_path / "logs")


@pytest.fixture
def logger(temp_logs_dir):
    """Create ConversationLogger with temp directory."""
    return ConversationLogger(session_id="test-session-123", output_dir=temp_logs_dir)


def test_logger_creates_directory(logger, temp_logs_dir):
    """Test that logger creates output directory."""
    assert Path(temp_logs_dir).exists()


def test_logger_creates_log_file_path(logger, temp_logs_dir):
    """Test that logger creates correct log file path."""
    expected = Path(temp_logs_dir) / "conversation_test-session-123.jsonl"
    assert logger.log_file == expected


def test_log_message_creates_file(logger):
    """Test that logging a message creates the file."""
    logger.log_message(role="user", content="Hello")
    assert logger.log_file.exists()


def test_log_message_writes_json(logger):
    """Test that logged message is valid JSON."""
    logger.log_message(role="user", content="Hello")

    with open(logger.log_file) as f:
        line = f.readline()
        data = json.loads(line)

    assert data["role"] == "user"
    assert data["content"] == "Hello"
    assert data["session_id"] == "test-session-123"
    assert "timestamp" in data


def test_log_multiple_messages(logger):
    """Test logging multiple messages."""
    logger.log_message(role="user", content="Hello")
    logger.log_message(role="assistant", content="Hi there!")
    logger.log_message(role="user", content="How are you?")

    with open(logger.log_file) as f:
        lines = f.readlines()

    assert len(lines) == 3
    data = [json.loads(line) for line in lines]
    assert data[0]["content"] == "Hello"
    assert data[1]["content"] == "Hi there!"
    assert data[2]["content"] == "How are you?"


def test_log_message_with_metadata(logger):
    """Test logging message with metadata."""
    metadata = {"interrupted": True, "has_image": False}
    logger.log_message(role="assistant", content="Response", metadata=metadata)

    with open(logger.log_file) as f:
        data = json.loads(f.readline())

    assert data["metadata"]["interrupted"] is True
    assert data["metadata"]["has_image"] is False


def test_on_conversation_item_added(logger):
    """Test event handler for conversation_item_added."""
    # Create mock event
    event = Mock()
    event.item.role = "user"
    event.item.text_content = "I want a Big Mac"
    event.item.interrupted = False

    # Call handler
    logger.on_conversation_item_added(event)

    # Verify logged
    with open(logger.log_file) as f:
        data = json.loads(f.readline())

    assert data["role"] == "user"
    assert data["content"] == "I want a Big Mac"
    assert data["metadata"]["interrupted"] is False


def test_skip_empty_messages(logger):
    """Test that empty messages are skipped."""
    event = Mock()
    event.item.role = "assistant"
    event.item.text_content = ""
    event.item.interrupted = False

    logger.on_conversation_item_added(event)

    # File should not exist (no messages logged)
    assert not logger.log_file.exists()


def test_skip_whitespace_only_messages(logger):
    """Test that whitespace-only messages are skipped."""
    event = Mock()
    event.item.role = "assistant"
    event.item.text_content = "   \n\t  "
    event.item.interrupted = False

    logger.on_conversation_item_added(event)

    assert not logger.log_file.exists()


def test_multiple_sessions_separate_files(temp_logs_dir):
    """Test that different sessions create separate log files."""
    logger1 = ConversationLogger(session_id="session-1", output_dir=temp_logs_dir)
    logger2 = ConversationLogger(session_id="session-2", output_dir=temp_logs_dir)

    logger1.log_message(role="user", content="Message 1")
    logger2.log_message(role="user", content="Message 2")

    assert logger1.log_file.exists()
    assert logger2.log_file.exists()
    assert logger1.log_file != logger2.log_file

    # Verify contents
    with open(logger1.log_file) as f:
        data1 = json.loads(f.readline())
    with open(logger2.log_file) as f:
        data2 = json.loads(f.readline())

    assert data1["session_id"] == "session-1"
    assert data2["session_id"] == "session-2"

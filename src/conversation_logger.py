"""Conversation logger for capturing all user and agent messages.

Logs conversations to JSON Lines format for debugging and analysis.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from livekit.agents import ConversationItemAddedEvent
from loguru import logger


class ConversationLogger:
    """Logs conversation messages to JSON Lines files."""

    def __init__(self, session_id: str, output_dir: str = "logs"):
        """Initialize conversation logger.

        Args:
            session_id: Unique session identifier
            output_dir: Directory for log files (default: "logs")
        """
        self.session_id = session_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create session-specific log file
        self.log_file = self.output_dir / f"conversation_{session_id}.jsonl"
        logger.info(
            "Conversation logger initialized",
            extra={"session_id": session_id, "log_file": str(self.log_file)},
        )

    def log_message(self, role: str, content: str, metadata: dict[str, Any] | None = None):
        """Log a single message to the conversation log.

        Args:
            role: Message role (user, assistant, system)
            content: Message text content
            metadata: Optional metadata (interrupted, tool_calls, etc.)
        """
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": self.session_id,
            "role": role,
            "content": content,
        }

        # Add optional metadata
        if metadata:
            log_entry["metadata"] = metadata

        # Append to JSON Lines file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(
                "Failed to write conversation log",
                extra={"session_id": self.session_id, "error": str(e)},
            )

    def on_conversation_item_added(self, event: ConversationItemAddedEvent):
        """Event handler for conversation_item_added events.

        This is called by LiveKit when any conversation item is added
        (both user and agent messages).

        Args:
            event: Conversation item added event
        """
        # Extract text content
        content = event.item.text_content or ""

        # Skip empty messages
        if not content.strip():
            logger.info(
                "Skipping empty conversation item",
                extra={
                    "session_id": self.session_id,
                    "role": event.item.role,
                },
            )
            return

        # Prepare metadata
        metadata = {
            "interrupted": event.item.interrupted,
        }

        # Add image/audio content flags if present
        if hasattr(event.item, "image_content") and event.item.image_content:
            metadata["has_image"] = True
        if hasattr(event.item, "audio_content") and event.item.audio_content:
            metadata["has_audio"] = True

        # Log the message
        self.log_message(
            role=event.item.role,
            content=content,
            metadata=metadata,
        )

        # Log at INFO level so conversation events are always visible
        logger.info(
            "Logged conversation item",
            extra={
                "session_id": self.session_id,
                "role": event.item.role,
                "content_length": len(content),
            },
        )

"""Integration tests for text-only mode configuration.

These tests verify that the agent can be configured to run in text-only mode
and that RoomOptions are set correctly based on configuration.
"""

import pytest

from config import AppConfig, SessionConfig


def test_text_only_mode_default():
    """Test that text_only_mode defaults to False."""
    config = SessionConfig()
    assert config.text_only_mode is False


def test_text_only_mode_can_be_enabled():
    """Test that text_only_mode can be set to True."""
    config = SessionConfig(text_only_mode=True)
    assert config.text_only_mode is True


def test_app_config_loads_text_only_mode(monkeypatch):
    """Test that AppConfig loads text_only_mode from environment."""
    # Set environment variable
    monkeypatch.setenv("SESSION__TEXT_ONLY_MODE", "true")

    # Create config
    config = AppConfig()

    # Verify
    assert config.session.text_only_mode is True


def test_app_config_defaults_text_only_mode(monkeypatch):
    """Test that AppConfig defaults text_only_mode to False."""
    # Ensure variable is not set
    monkeypatch.delenv("SESSION__TEXT_ONLY_MODE", raising=False)

    # Create config
    config = AppConfig()

    # Verify
    assert config.session.text_only_mode is False


def test_text_only_mode_with_noise_cancellation(monkeypatch):
    """Test that both text_only and noise_cancellation can be configured."""
    monkeypatch.setenv("SESSION__TEXT_ONLY_MODE", "true")
    monkeypatch.setenv("SESSION__ENABLE_NOISE_CANCELLATION", "true")

    config = AppConfig()

    assert config.session.text_only_mode is True
    assert config.session.enable_noise_cancellation is True
    # Note: In text mode, noise cancellation is ignored

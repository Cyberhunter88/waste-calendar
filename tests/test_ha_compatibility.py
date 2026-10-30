"""Check that the integration imports against the installed Home Assistant."""

import importlib

import pytest

pytest.importorskip("homeassistant")


def test_home_assistant_platforms_import() -> None:
    """Import all platform and setup modules with real Home Assistant APIs."""
    for module in ("coordinator", "config_flow", "sensor", "calendar"):
        importlib.import_module(f"custom_components.zweibruecken_waste.{module}")

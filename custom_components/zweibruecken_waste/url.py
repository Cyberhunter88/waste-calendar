"""URL helpers for the Zweibruecken waste calendar integration."""

from __future__ import annotations


def normalize_ics_url(ics_url: str) -> str:
    """Normalize user-provided ICS calendar URLs."""

    normalized_url = ics_url.strip()
    if normalized_url.lower().startswith("webcal://"):
        return f"https://{normalized_url[9:]}"
    return normalized_url

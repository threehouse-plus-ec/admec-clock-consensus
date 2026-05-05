"""Non-load-bearing placeholder for future information-theoretic extensions.

ARP v0.2 does not claim or replicate Cramer-Rao bounds. This module exists only
to reserve the extension point and to keep that limitation explicit in code.
"""

from __future__ import annotations

from .reference_model import ENDORSEMENT_MARKER


def unavailable_in_v02() -> None:
    """Raise for callers that try to use Fisher-information machinery in v0.2."""

    raise NotImplementedError(
        "Fisher-information and CRLB machinery are outside ARP v0.2. "
        f"Endorsement marker: {ENDORSEMENT_MARKER}"
    )


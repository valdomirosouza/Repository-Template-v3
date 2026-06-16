"""Cursor pagination helpers for list endpoints.

Backward-compatible by design: endpoints keep returning a JSON **array** body (so existing consumers
are unaffected) and expose pagination metadata in response headers — ``X-Limit``,
``X-Total-Returned`` and, when more results remain, ``X-Next-Cursor``. The cursor is opaque; clients
echo it back via ``?cursor=`` to fetch the next page (api-standards.md §5).

Internally the cursor encodes an offset; it is opaque to clients so the implementation can change
(e.g. to a keyset cursor) without breaking the contract.
"""

from __future__ import annotations

import base64
import binascii

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

_CURSOR_PREFIX = "o:"


def encode_cursor(offset: int) -> str:
    """Encode an offset as an opaque, URL-safe cursor token."""
    raw = f"{_CURSOR_PREFIX}{offset}".encode()
    return base64.urlsafe_b64encode(raw).decode()


def decode_cursor(cursor: str | None) -> int:
    """Decode an opaque cursor to an offset. ``None`` → 0. Raises ``ValueError`` if malformed."""
    if cursor is None or cursor == "":
        return 0
    try:
        decoded = base64.urlsafe_b64decode(cursor.encode()).decode()
    except (binascii.Error, UnicodeDecodeError, ValueError) as exc:
        raise ValueError("malformed cursor") from exc
    if not decoded.startswith(_CURSOR_PREFIX):
        raise ValueError("malformed cursor")
    offset = int(decoded[len(_CURSOR_PREFIX) :])  # raises ValueError on non-int
    if offset < 0:
        raise ValueError("negative offset")
    return offset


def paginate[T](items: list[T], limit: int, offset: int) -> tuple[list[T], str | None]:
    """Return ``(page, next_cursor)``. ``next_cursor`` is None when there are no more items."""
    page = items[offset : offset + limit]
    next_offset = offset + limit
    next_cursor = encode_cursor(next_offset) if next_offset < len(items) else None
    return page, next_cursor

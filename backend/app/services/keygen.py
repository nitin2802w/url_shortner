"""
Module 2 — Key Generation Engine
=================================
Responsibilities:
  1. Base62 encoder / decoder  (0-9, a-z, A-Z  →  62 symbols)
  2. Unique ID generator        (Snowflake-style 64-bit integer)
  3. Reserved word filter       (blocks api, docs, health, admin …)

No external dependencies beyond the stdlib — fully unit-testable without
a running database or Redis instance.
"""

import time
import threading

# ---------------------------------------------------------------------------
# 1. Base62 alphabet & codec
# ---------------------------------------------------------------------------

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)  # 62


def encode_base62(number: int) -> str:
    """
    Convert a positive integer into a Base62 string.

    Examples:
        0        → "0"
        61       → "Z"
        62       → "10"
        100_000  → "q0U"
    """
    if number < 0:
        raise ValueError(f"encode_base62 requires a non-negative integer, got {number}")
    if number == 0:
        return ALPHABET[0]

    chars: list[str] = []
    while number:
        number, remainder = divmod(number, BASE)
        chars.append(ALPHABET[remainder])

    return "".join(reversed(chars))


def decode_base62(short_code: str) -> int:
    """
    Convert a Base62 string back into its original integer.

    Examples:
        "0"   → 0
        "Z"   → 61
        "10"  → 62
        "q0U" → 100_000
    """
    number = 0
    for char in short_code:
        if char not in ALPHABET:
            raise ValueError(f"Invalid Base62 character: {char!r}")
        number = number * BASE + ALPHABET.index(char)
    return number


# ---------------------------------------------------------------------------
# 2. Snowflake-style unique ID generator
# ---------------------------------------------------------------------------
#
# Layout of the 64-bit ID (inspired by Twitter Snowflake):
#
#   [ 41 bits timestamp (ms since epoch) ]
#   [ 10 bits machine/worker id          ]
#   [ 12 bits sequence counter           ]
#
# This guarantees:
#   - Monotonically increasing IDs  →  no collisions
#   - ~4096 IDs per millisecond per worker
#   - IDs stay sortable by creation time

_EPOCH = 1_700_000_000_000        # custom epoch (ms) — Nov 2023
_WORKER_ID = 1                    # change per deployment instance (0-1023)
_SEQUENCE_BITS = 12
_WORKER_BITS = 10
_TIMESTAMP_BITS = 41

_MAX_SEQUENCE = (1 << _SEQUENCE_BITS) - 1   # 4095
_MAX_WORKER   = (1 << _WORKER_BITS)   - 1   # 1023

_lock = threading.Lock()
_last_timestamp: int = -1
_sequence: int = 0


def _current_ms() -> int:
    return int(time.time() * 1000)


def generate_unique_id() -> int:
    """
    Generate a globally unique, time-ordered 64-bit integer.
    Thread-safe — uses a lock to guard the sequence counter.
    """
    global _last_timestamp, _sequence

    with _lock:
        now = _current_ms()

        if now == _last_timestamp:
            _sequence = (_sequence + 1) & _MAX_SEQUENCE
            if _sequence == 0:
                # Sequence exhausted — busy-wait for the next millisecond
                while now <= _last_timestamp:
                    now = _current_ms()
        else:
            _sequence = 0

        _last_timestamp = now

        unique_id = (
            ((now - _EPOCH) << (_WORKER_BITS + _SEQUENCE_BITS))
            | (_WORKER_ID   << _SEQUENCE_BITS)
            | _sequence
        )
        return unique_id


def generate_short_code() -> str:
    """
    Generate a short code by:
      1. Creating a unique Snowflake-style integer ID
      2. Base62-encoding it into a compact string (~7-10 chars)

    Example output:  "2b9A4xQ"
    """
    unique_id = generate_unique_id()
    code = encode_base62(unique_id)

    # Guard: should never be reserved, but filter just in case
    if is_reserved(code):
        # Extremely unlikely — regenerate once
        code = encode_base62(generate_unique_id())

    return code


# ---------------------------------------------------------------------------
# 3. Reserved word filter
# ---------------------------------------------------------------------------

RESERVED_WORDS: frozenset[str] = frozenset({
    "api", "docs", "redoc", "health", "static",
    "admin", "login", "logout", "register", "favicon.ico",
    "robots.txt", "sitemap.xml", "assets", "media",
})


def is_reserved(alias: str) -> bool:
    """Return True if the alias clashes with a reserved application route."""
    return alias.lower() in RESERVED_WORDS

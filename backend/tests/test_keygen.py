"""
Module 2 – Unit test stubs for the keygen service.
These tests will be fleshed out when Module 2 (keygen.py) is implemented.
"""
import pytest


@pytest.mark.skip(reason="Module 2 not yet implemented")
def test_base62_encode_decode():
    """Round-trip: encode then decode should return original integer."""
    from app.services.keygen import encode_base62, decode_base62
    for n in [0, 1, 100, 999_999, 2**32]:
        assert decode_base62(encode_base62(n)) == n


@pytest.mark.skip(reason="Module 2 not yet implemented")
def test_no_collisions():
    """10,000 sequential IDs must produce 10,000 unique short codes."""
    from app.services.keygen import encode_base62
    codes = [encode_base62(i) for i in range(10_000)]
    assert len(set(codes)) == 10_000

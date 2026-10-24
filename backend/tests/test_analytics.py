"""
Unit tests for Module 5: Analytics Service (device/browser parsing, IP hashing, stats).
"""

import hashlib
import pytest
from app.models.url import ClickAnalytic
from app.services.analytics_service import detect_device, detect_browser


def test_detect_device():
    # Mobile
    assert detect_device("Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148") == "mobile"
    assert detect_device("Mozilla/5.0 (Linux; Android 10; SM-G981B) Mobile Safari/537.36") == "mobile"
    
    # Tablet
    assert detect_device("Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X)") == "tablet"
    assert detect_device("Mozilla/5.0 (Linux; Android 10; Tablet) AppleWebKit/537.36") == "tablet"

    # Desktop
    assert detect_device("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36") == "desktop"
    assert detect_device("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36") == "desktop"
    assert detect_device(None) == "desktop"
    assert detect_device("") == "desktop"


def test_detect_browser():
    # Edge
    assert detect_browser("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59") == "Edge"
    
    # Chrome
    assert detect_browser("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") == "Chrome"
    
    # Firefox
    assert detect_browser("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0") == "Firefox"
    
    # Safari
    assert detect_browser("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15") == "Safari"

    # Opera
    assert detect_browser("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172") == "Opera"

    # Other / None
    assert detect_browser("curl/7.68.0") == "Other"
    assert detect_browser(None) == "Other"


def test_ip_hash_privacy():
    raw_ip = "192.168.1.100"
    hashed = ClickAnalytic.hash_ip(raw_ip)
    
    # Correct SHA-256 hash length
    assert len(hashed) == 64
    assert hashed == hashlib.sha256(raw_ip.encode()).hexdigest()
    # Consistent hashing
    assert ClickAnalytic.hash_ip(raw_ip) == hashed

"""
Interactive URL Shortener — Module 2 Local Demo
================================================
Run from the backend/ folder:
    python test_keygen_local.py

Type any URL and get a short code back.
Type 'quit' or press Ctrl+C to exit.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.services.keygen import generate_short_code, is_reserved

# ── ANSI colours ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

BASE_URL = "http://localhost:8000"

# Keep a history of this session
history: list[tuple[str, str]] = []


def print_banner():
    print(f"""
{BOLD}{CYAN}
  ╔══════════════════════════════════════════╗
  ║        🔗  URL Shortener — Module 2      ║
  ║         Interactive Local Demo           ║
  ╚══════════════════════════════════════════╝
{RESET}{DIM}  Type any URL to shorten it.
  Commands:  'history'  →  show all this session
             'quit'     →  exit
{RESET}""")


def shorten(url: str) -> str:
    """Generate a short code and return the full short URL."""
    code = generate_short_code()
    short_url = f"{BASE_URL}/{code}"
    return code, short_url


def print_result(original: str, code: str, short_url: str):
    original_display = original if len(original) <= 60 else original[:57] + "..."
    print(f"""
  {DIM}Original  →{RESET}  {original_display}
  {GREEN}{BOLD}Short URL →  {short_url}{RESET}
  {DIM}Code      →  {code}   ({len(code)} chars){RESET}
""")


def print_history():
    if not history:
        print(f"\n  {YELLOW}No URLs shortened yet this session.{RESET}\n")
        return
    print(f"\n  {BOLD}Session History ({len(history)} URLs){RESET}")
    print(f"  {'─'*60}")
    for i, (orig, short) in enumerate(history, 1):
        trunc = orig if len(orig) <= 45 else orig[:42] + "..."
        print(f"  {DIM}{i:>2}.{RESET}  {trunc:<47}  {GREEN}{short}{RESET}")
    print()


def main():
    print_banner()

    while True:
        try:
            user_input = input(f"  {CYAN}Enter URL{RESET} › ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {YELLOW}Bye! 👋{RESET}\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print(f"\n  {YELLOW}Bye! 👋{RESET}\n")
            break

        if user_input.lower() == "history":
            print_history()
            continue

        # Basic check — warn but still shorten
        if not user_input.startswith(("http://", "https://")):
            print(f"  {YELLOW}⚠  Tip: URLs usually start with https:// — shortening anyway...{RESET}")

        code, short_url = shorten(user_input)
        history.append((user_input, short_url))
        print_result(user_input, code, short_url)


if __name__ == "__main__":
    main()

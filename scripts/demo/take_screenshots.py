"""Screenshot Taker"""

import argparse

from demo_creator import DemoBuilder

DEFAULT_PAGES = [
    "dashboard",
]


def main():
    parser = argparse.ArgumentParser(description="Take screenshots of app pages")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--dark-mode", action="store_true", help="Enable dark mode")
    args = parser.parse_args()

    taker = DemoBuilder(
        width=int(1920 * 0.8),
        height=int(1080 * 0.8),
        dark_mode=True,
        scale_factor=1,
        headless=False,
    )
    taker.screenshot(DEFAULT_PAGES)


if __name__ == "__main__":
    main()

"""Screenshot Taker"""

import argparse

from demo_creator import DemoBuilder

DEFAULT_PAGES = [
    "dashboard",
    "scraped-jobs",
]


def main():
    parser = argparse.ArgumentParser(description="Take screenshots of app pages")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--dark-mode", action="store_true", help="Enable dark mode")
    args = parser.parse_args()

    taker = DemoBuilder(
        width=1920,
        height=1080,
        dark_mode=True,
        headless=not args.no_headless,
    )
    taker.screenshot(DEFAULT_PAGES)


if __name__ == "__main__":
    main()

"""Small CLI exposing `uv run` to start the GridWalker app."""
import sys
import argparse

from gridwalker_lib.app import App


def main():
    parser = argparse.ArgumentParser(prog="uv", description="Project runner similar to MatEst's uv")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="Run the GridWalker GUI")
    args = parser.parse_args()

    if args.command == "run":
        App().mainloop()
    else:
        parser.print_help()
        sys.exit(1)

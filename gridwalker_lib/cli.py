"""CLI helpers for gridwalker package (used by the `uv` console script)."""
import sys
import argparse

from .app import App


def main():
    parser = argparse.ArgumentParser(prog="uv", description="Project runner similar to MatEst's uv")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Run the GridWalker GUI or execute a file/module")
    run_p.add_argument("target", nargs="?", help="Optional file path or module name to run")
    # accept extra args to forward to executed script/module
    run_p.add_argument("--", dest="dash", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

    args, extras = parser.parse_known_args()

    if args.command != "run":
        parser.print_help()
        sys.exit(1)

    target = getattr(args, "target", None)
    # If no target specified, launch default GUI
    if not target:
        App().mainloop()
        return

    # If target is a path to an existing file, run it as a script
    import os
    import runpy

    try:
        if os.path.exists(target):
            runpy.run_path(target, run_name="__main__")
        else:
            # try to run as module
            runpy.run_module(target, run_name="__main__")
    except Exception as e:
        print(f"Error running target '{target}': {e}")
        sys.exit(2)

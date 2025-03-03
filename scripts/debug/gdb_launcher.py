#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess

# default extension path
DEFAULT_EXTENSION_FILE_NAME = "gdb_extension.py"

# global variable to store tty value
PROGRAM_TTY_STDOUT = None
# global variable to indicate verbose mode
VERBOSE_PRINT = 0
# global variable to store STDOUT linked target
STDOUT_LINK = None


def v_print(msg):
    if VERBOSE_PRINT:
        print(f"[VERBOSE]: {msg}", flush=True)


def find_stdfileno():
    global STDOUT_LINK
    stdout_target = os.readlink('/proc/self/fd/1')
    if stdout_target is not None:
        STDOUT_LINK = stdout_target


def get_default_extension_path():
    try:
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        return os.path.join(current_dir, DEFAULT_EXTENSION_FILE_NAME)
    except:
        return None


def parse_args():
    """
    create an argument parser and parse known arguments.
    this function sets global variables based on provided options.
    """
    # create a new ArgumentParser instance with description
    parser = argparse.ArgumentParser(
        description="parse command line arguments",
        add_help=True  # this enables the -h/--help automatically
    )

    # add optional argument --tty; not required, value stored if provided
    parser.add_argument("--tty", help="set tty value", required=False)

    # add optional argument --verbose; if present, store_true action is triggered
    parser.add_argument("--verbose", action="store_true",
                        help="enable verbose mode")

    # add optional argument -s / --source; expects a string argument
    parser.add_argument(
        "-s", "--source", help="set python extension path", required=False)

    # parse known args while allowing unknown arguments to pass through
    args, unknown = parser.parse_known_args()

    # set global variables based on parsed arguments
    global PROGRAM_TTY_STDOUT, VERBOSE_PRINT
    if args.tty:
        PROGRAM_TTY_STDOUT = args.tty
    if args.verbose:
        VERBOSE_PRINT = 1

    return args, unknown


if __name__ == "__main__":
    # parse the arguments and obtain unknown arguments as well
    args, unknown = parse_args()

    gdb_path = shutil.which("gdb")
    if gdb_path is None:
        raise FileNotFoundError("gdb not found")

    find_stdfileno()
    if STDOUT_LINK is not None:
        v_print(f"STDOUT file link is: {STDOUT_LINK}")

    # if there's no --tty arg: run by user
    if args.tty:
        PROGRAM_TTY_STDOUT = args.tty

    # format gdb cmd
    gdb_cmd = [gdb_path]

    if args.tty is not None:
        gdb_cmd += ["--tty", args.tty]

    default_extension_path = get_default_extension_path()
    if os.path.isfile(default_extension_path):
        gdb_cmd += ["-ex", f"source {default_extension_path}"]
    else:
        print(f"[WARNING] No such file: {default_extension_path}", flush=True)
        print(f"[WARNING] Ignore default extension script", flush=True)
    if args.source is not None:
        gdb_cmd += ["-ex", f"source {args.source}"]

    gdb_cmd += unknown

    # custom your gdb_cmd here

    print(f"[INFO] Launching gdb using: {gdb_cmd}", flush=True)

    # RUN BY USER, use CREATE_NEW_CONSOLE flags
    if args.tty is None:
        # TODO: use typescript to call vscode newterminal api in the future
        # using the gdb file for workaround
        pass

    process = subprocess.Popen(gdb_cmd)
    process.wait()

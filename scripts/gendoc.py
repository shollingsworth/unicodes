#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import sys
import argparse
from argparse import ArgumentParser
import ps1api
import subprocess
import shlex

ME = Path(__file__)
BASE = Path(__file__).resolve().parent.parent
BINDIR = BASE.joinpath("bin")
README = BASE.joinpath("README.md")
MEDIA_DIR = BASE.joinpath("media")
sys.path.append(str(BINDIR.absolute()))

GITHUB_BASE = "https://github.com/shollingsworth/unicodes"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/shollingsworth/unicodes"


def main():
    """Run main function."""
    mod = __import__("ps1")
    template_map = mod._gen_template(ps1api)
    parser = mod._get_parser(template_map, ps1api.Base)  # type: ArgumentParser

    with README.open("r+") as fileh:
        fmt = _get_ps1_cmd_output(parser)
        data = fileh.read()
        fileh.seek(0)
        data = data.replace("__PS1__", fmt)
        fileh.write(data)
        fileh.flush()

    with README.open("r+") as fileh:
        fmt = _get_example_output()
        data = fileh.read()
        fileh.seek(0)
        data = data.replace("__EXAMPLES__", fmt)
        fileh.write(data)
        fileh.flush()


if __name__ == "__main__":
    main()

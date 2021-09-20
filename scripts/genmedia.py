#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate PS1 images from examples."""
from pathlib import Path
import subprocess
import shlex
import argparse
from contextlib import contextmanager

# pylint: disable=consider-using-with
# pylint: disable=invalid-name

BDIR = Path(__file__).parent.parent
EXAMPLE_DIR = BDIR.joinpath("media/demo")
DSTDIR = BDIR.joinpath("media")

KONS_GEO = "1400x1000,0+0"
CAP_GEO = "1400x1000+1920+60"


@contextmanager
def konsole(rcfile: Path):
    """launch konsole / program."""
    cmd = shlex.split(
        f"konsole --nofork --geometry {KONS_GEO} -e bash --rcfile {rcfile.resolve()}"
    )
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    try:
        yield p
    finally:
        p.terminate()


@contextmanager
def screencap(dstfile: Path):
    """Get screencap."""
    cmd = shlex.split(
        f"import -window root -pause 3 -crop {CAP_GEO} {dstfile.resolve()}"
    )
    p = subprocess.Popen(cmd)
    try:
        yield p
    finally:
        p.terminate()


def iter_media_files():
    """Iterate through examples."""
    for i in EXAMPLE_DIR.iterdir():
        if not i.name.endswith(".sh"):
            continue
        yield i, DSTDIR.joinpath(f"{i.name}.png")


def clean():
    """Clean media files."""
    for file in DSTDIR.iterdir():
        if file.is_dir():
            continue
        print(f"Deleting {file}")
        file.unlink()


def check():
    """Check if files exist."""
    noexist = []
    for srcfile, dfile in iter_media_files():
        if not dfile.exists():
            noexist.append(srcfile.name)
    if noexist:
        out = ",".join(noexist)
        raise SystemExit(f"The following media files need to be created for: {out}")


def main(overwrite=False):
    """Run main function."""
    for srcfile, dfile in iter_media_files():
        if not overwrite and dfile.exists():
            continue
        print(f"Creating: {dfile}")
        with konsole(srcfile) as kons, screencap(dfile) as sc:
            sc.communicate()
            kons.kill()


MAP = {
    "create": [main],
    "overwrite": [lambda: main(True)],
    "clean": [clean],
    "check": [check],
    "regen": [
        clean,
        main,
    ],
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    parser.add_argument(
        "command",
        choices=MAP.keys(),
        type=str,
    )
    # args = parser.parse_args(["regen"])
    args = parser.parse_args()
    for func in MAP[args.command]:
        func()

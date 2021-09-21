#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate documentation for project."""
from pathlib import Path
import sys
from freeplane_tools.github import MindMap2GithubMarkdown
from unicodes_api.cli import SUBCOMMANDS
from unicodes_api.parser import ParserOpts

ME = Path(__file__)
BASE = Path(__file__).resolve().parent.parent
BINDIR = BASE.joinpath("bin")
README = BASE.joinpath("README.mm")
DEST_README = BASE.joinpath("README.md")
MEDIA_DIR = BASE.joinpath("media")
DEMO_DIR = BASE.joinpath("media/demo")
sys.path.append(str(BINDIR.absolute()))

GITHUB_BASE = "https://github.com/shollingsworth/unicodes/blob/main"
GITHUB_RAW = "https://github.com/shollingsworth/unicodes/raw/main"


def _code_section(txt):
    val = []
    val.append(
        "\n".join(
            [
                "```",
                txt,
                "```",
            ]
        )
    )
    return "\n".join(val)


def _getdesc(file: Path):
    content = file.read_text()
    arr = content.splitlines()
    for i in arr:
        _a2 = i.split("=")
        if len(_a2) != 2:
            continue
        name, desc = _a2
        if name != "DESC":
            continue
        return desc.strip('"')
    return None


def _examples():
    sections = []
    for _mf in sorted(MEDIA_DIR.iterdir()):
        sect = []
        if _mf.is_dir():
            continue
        _bn = _mf.name.replace(_mf.suffix, "")
        script = DEMO_DIR.joinpath(_bn)
        desc = _getdesc(script)
        desc = f"> {desc}" if desc else ""
        srcpath = script.relative_to(BASE)
        medpath = _mf.relative_to(BASE)
        srclink = f"[{script.name}]({GITHUB_BASE}/{srcpath})"
        medlink = f"![{script.name}]({GITHUB_RAW}/{medpath})"
        sect.append(f"## {srclink}")
        sect.append(desc)
        sect.append(f"{medlink}")
        sections.append("\n".join(sect))
    return "\n".join(sections)


def main():
    """Run main function."""
    _ = SUBCOMMANDS
    extxt = _examples()
    repl_map = {
        "__HELP__": [],
        "__EXAMPLES__": [extxt],
    }
    repl_map["__HELP__"].append("# Main")
    repl_map["__HELP__"].append(_code_section(ParserOpts.MAIN.format_help()))
    for i in ParserOpts.SUBCMDS:
        repl_map["__HELP__"].append(f"## {i.name}")
        repl_map["__HELP__"].append(_code_section(i.get_help()))

    obj = MindMap2GithubMarkdown(str(README))
    data = obj.get_document()
    for k, arr in repl_map.items():
        data = data.replace(k, "\n".join(arr))

    with DEST_README.open("wb") as fileh:
        fileh.write(data.encode())
        fileh.flush()

    print(DEST_README.read_text())


if __name__ == "__main__":
    main()

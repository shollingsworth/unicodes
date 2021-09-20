#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cli Commands Module."""
from typing import Iterator, Iterable, Dict, Any, List
from abc import ABC, abstractmethod
import json
import inspect
import argparse

# pylint: disable=protected-access,invalid-name


SKIPS = ["tokens", "chr", "name"]
"""During line generation these are called out, the rest are dynamic."""
SEP = "   "
"""Default separater when indenting."""


class ParserOpts:
    """Parser options."""

    MAIN = None  # type: Any | argparse.ArgumentParser
    """Main ArgumentParser class."""
    SUBPARSERS = None  # type: Any | argparse.ArgumentParser
    """List of subparsers."""
    SUBCMDS = []  # type: List[ParserOpts]
    """Collection of this instances of this class."""

    def __init__(self, name: str, pcls: type):
        """initialize ParserOpts."""
        if not self.MAIN:
            ParserOpts.MAIN = argparse.ArgumentParser(
                formatter_class=argparse.RawTextHelpFormatter,
            )
            ParserOpts.SUBPARSERS = self.MAIN.add_subparsers(
                title="subcommands",
            )
        self.pcls = pcls  # type: Any
        """Parent class (from which I was called)."""
        self.name = name
        """command name."""
        ParserOpts.SUBCMDS.append(self)
        self.parser = ParserOpts.SUBPARSERS.add_parser(
            self.name,
            formatter_class=argparse.RawTextHelpFormatter,
            help=inspect.cleandoc(pcls.__doc__ or ""),
        )
        """Current parser."""
        self.parser.set_defaults(func=name)
        self.args_setup()

    def args_setup(self):
        """Setup args."""
        fsig = inspect.signature(self.pcls.setup)
        arg_arr = [k for k, _ in fsig.parameters.items() if k != "self"]
        defaults = {}  # type: Dict[Any, Any]
        if not arg_arr:
            defaults["args"] = []
        self.parser.set_defaults(**defaults)
        if arg_arr:
            arg_names = " ".join(arg_arr)
            self.parser.add_argument(
                "args", nargs=argparse.REMAINDER, help=f"{arg_names}"
            )

    def add_filter(self):
        """Add filter argument."""
        self.parser.add_argument(
            "--filter",
            "-f",
            help="filter values",
            action="extend",
            default=[],
            nargs="*",
        )

    def add_exclude(self):
        """Add exclude argument."""
        self.parser.add_argument(
            "--exclude",
            "-e",
            help="reverse filter",
            action="extend",
            default=[],
            nargs="*",
        )

    def add_details(self):
        """Add detail argument."""
        self.parser.add_argument(
            "--detail",
            "-d",
            help="print details",
            action="store_true",
            default=False,
        )

    def add_json(self):
        """Add json argument."""
        self.parser.add_argument(
            "--json",
            "-j",
            help="print in json format",
            action="store_true",
            default=False,
        )

    def get_help(self):
        """Get help doc."""
        sub = self._get_subparser()
        return sub.format_help()

    def _get_subparser(self) -> argparse.ArgumentParser:
        """Get self subparser."""
        # retrieve subparsers from parser
        subparsers_actions = [
            action
            for action in self.MAIN._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                if choice == self.name:
                    return subparser
        raise RuntimeError("Could not find subparser")


class Formatter(ABC):
    """Formatter class."""

    NAME = None  # type: Any
    """subcommand name."""

    def __init__(self):
        """instantiate Formatter class."""
        self.popts = ParserOpts(self.NAME, self.__class__)
        """ParserOpts instance."""
        self.setup_popts()
        self._iterator = None  # type: Any | Iterator
        """Iterator if set."""
        self.args = None  # type: Any | argparse.Namespace
        """argparse.Namespace value."""

    def setup(self, iterator):
        """setup class for run."""
        self._iterator = iterator

    def set_args(self, args: argparse.Namespace):
        """set arguments."""
        self.args = args

    @abstractmethod
    def setup_popts(self):
        """setup parser options."""

    @abstractmethod
    def run(self):
        """Run program."""

    def iterator(self) -> Iterator[Dict]:
        """Iterator."""
        try:
            inc = self.args.filter
        except AttributeError:
            inc = []
        try:
            excl = self.args.exclude
        except AttributeError:
            excl = []

        for dval in self._iterator:
            name = dval["name"]
            if not any([inc, excl]):
                yield dval
            else:
                pval = all(
                    [
                        all(i in name for i in inc),
                        not any(i in name for i in excl),
                    ]
                )
                if pval:
                    yield dval

    @staticmethod
    def fmt_single_normal(dval):
        """format unicode value normally."""
        char = dval["chr"]
        name = dval["name"]
        line = " ".join([f"{k}:{v}" for k, v in dval.items() if k not in SKIPS])
        retval = f"{char} {name} {line}"
        return retval

    @staticmethod
    def fmt_dval_sub_lines(dval):
        """Format unicode value as staggered line."""
        char = dval["chr"]
        name = dval["name"]
        lines = [f"{char} {name}"]
        for k, v in dval.items():
            if k in SKIPS:
                continue
            lines.append(f"{SEP}{k}: {v}")
        return "\n".join(lines)

    @staticmethod
    def tab_shift(txtblock: str, shift_len: int):
        """Shift text over."""
        sep = " " * shift_len
        txt = f"\n{sep}".join([f"{sep}{line}" for line in txtblock.splitlines()])
        return f"{sep}{txt}"

    @staticmethod
    def fmt_group_multi_detail(title, dvals: Iterable[Dict]):
        """Format group with detail."""
        txt = Formatter.tab_shift(
            "\n".join(
                [
                    Formatter.fmt_single_normal(dval)
                    for dval in sorted(dvals, key=lambda x: x["int"])
                ]
            ),
            4,
        )
        return f"{title}\n{txt}"

    @staticmethod
    def fmt_group_multi_detail_staggered_lines(title, dvals: Iterable[Dict]):
        """Format group with staggered lines."""
        txt = Formatter.tab_shift(
            "\n".join(
                [
                    Formatter.fmt_dval_sub_lines(dval)
                    for dval in sorted(dvals, key=lambda x: x["int"])
                ]
            ),
            4,
        )
        return f"{title}\n{SEP}{txt}"

    def fmt_group_normal(self) -> Iterator[str]:
        """Format group normally."""
        for i in self.iterator():
            yield self.fmt_single_normal(i)

    def fmt_json(self) -> Iterable[str]:
        """Format as parsable json."""
        retdict = []
        for i in self.iterator():
            retdict.append(i)
        yield json.dumps(retdict)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cli Commands Module."""
import sys
import json
import textwrap
from typing import Dict, Iterator, Tuple
from argparse import ArgumentParser
import curses
from unicodes_api.screen import (
    BidirectionalNewIterator,
    BidirectionalStaticRevolvingIterator,
    NavItem,
)
from unicodes_api import Groups, iter_unicodes, LetterMixer, PairsGroups
from unicodes_api.parser import Formatter

# pylint: disable=invalid-name,too-many-instance-attributes
# pylint: disable=arguments-differ
# pylint: disable=pointless-string-statement


class InteractAllGroups(BidirectionalStaticRevolvingIterator):
    """Explore the tokenized unicode data."""

    NAME = "explore"
    """subcommand name."""

    def __init__(self):
        super().__init__()
        self.highlight_pos = 0
        """highlight position from iterative cursor."""

        self.is_detail = False
        """print detailed lines (can be a lot of txt)."""
        self.gobj = Groups()
        """Groups instance."""
        self.txt = []
        """Supplemental text messages."""
        self.index = 0
        """current value location."""

    def setup_popts(self):
        """setup parser options."""

    def mouse_callback(self, value: Dict[str, str]):
        """mouse callback function."""
        char = value["word"]
        if not char.strip():
            return
        pos = self.highlight_pos
        for idx, i in enumerate(self.detail_arr):
            if i["chr"] == char:
                pos = idx
                break
        self.highlight_pos = pos
        self._dowrite()

    def _reset_hightlight(self):
        """reset highlight position."""
        self.highlight_pos = 0

    def setup(self):
        """Scroll through all unicodes token groups."""
        super().setup([])
        self.nav.values[ord("n")].add_callback(self._reset_hightlight).add_alias(
            ord("j")
        )
        self.nav.values[ord("p")].add_callback(self._reset_hightlight).add_alias(
            ord("k")
        )
        self.nav.add_item(
            NavItem(
                "s",
                "search start text",
            )
            .set_func(self.search)
            .add_callback(self._reset_hightlight),
        )
        self.nav.add_item(
            NavItem(
                "d",
                "toggle show all details",
            ).set_func(self.toggle_detail),
        )
        self.nav.add_item(
            NavItem(
                "h",
                "previous character",
            )
            .set_func(self.shift_right)
            .add_alias(curses.KEY_LEFT),
        )
        self.nav.add_item(
            NavItem(
                "l",
                "next character",
            )
            .set_func(self.shift_left)
            .add_alias(curses.KEY_RIGHT),
        )
        self.nav.add_item(
            NavItem(
                "m",
                "toggle mouse interaction",
            ).set_func(self.toggle_mouse),
        )
        for token, vals in self.gobj.iter_all_groups():
            fmt_line = " ".join(sorted(i["chr"] for i in vals))
            self.collection.append(f"{token} {fmt_line}")

    def shift_left(self):
        """Shift highlight position left."""
        clen = len(self.detail_arr)
        self.highlight_pos += 1
        if self.highlight_pos >= clen - 1:
            self.highlight_pos = clen - 1
            return

    def shift_right(self):
        """Shift highlight position right."""
        self.highlight_pos -= 1
        self.highlight_pos = max(self.highlight_pos, 0)

    @property
    def cur_token(self):
        """Current token."""
        return self.current_value.split()[0]

    @property
    def detail_arr(self):
        """Current detail array."""
        vals = list(sorted(self.gobj.get_vals(self.cur_token), key=lambda x: x["chr"]))
        return vals

    @property
    def cur_detail(self):
        """Current token detail."""
        return self.detail_arr[self.highlight_pos]

    @property
    def cur_char(self):
        """Current character."""
        return self.cur_detail["chr"]

    @property
    def _detail_lines(self):
        """Detail lines."""
        if self.is_detail:
            self.highlight_vals = []
            return Formatter.fmt_group_multi_detail("Details:", self.detail_arr)
        self.highlight_vals = [self.cur_char]
        return "\n".join(
            [
                "Details:",
                Formatter.fmt_single_normal(self.cur_detail),
            ]
        )

    def _print_menu(self):
        """menu output."""

        disp_lines = [self.cur_token]
        setwidth = max(self.width - 40, 20)

        main = "\n".join(
            textwrap.wrap(
                " ".join(i["chr"] for i in self.detail_arr),
                width=setwidth,
            )
        )
        main = textwrap.indent(main, " " * 2)
        disp_lines += [main]

        output = [
            f"index:{self.index} cur_pos:{self.highlight_pos} mouse_enabled:{self.is_mouse}",
            "",
            "\n".join(disp_lines),
            "",
            self._detail_lines,
            "",
            "\n".join(self.txt),
            "",
            self.nav.get_menu_text(),
        ]
        lout = "\n".join(output).replace("\0", "NULL")
        self.txt = []
        return lout

    def toggle_detail(self):
        """toggle detail switch."""
        if self.is_detail:
            self.is_detail = False
        else:
            self.is_detail = True

    def search(self):
        """get search results."""
        kp = self.get_input("Search string")
        for idx, line in enumerate(self.collection):
            if line.lower().startswith(kp):
                self.index = idx
                return
        self.txt.append(f"Could not find anything starting with: '{kp}'")


class all_to_stdout(Formatter):
    """Output all unicode values to STDOUT."""

    NAME = "all"
    """subcommand name."""

    def setup_popts(self):
        """setup parser options."""
        self.popts.add_filter()
        self.popts.add_exclude()
        self.popts.add_json()

    def setup(self):
        """Setup iterator."""
        super().setup(iter_unicodes())

    def run(self):
        """Run program."""
        if self.args.json:
            itervals = self.fmt_json()
        else:
            itervals = self.fmt_group_normal()
        sys.stdout.write("%s\n" % "\n".join(itervals))


class HackerMixerInteractive(BidirectionalNewIterator):
    """Hacker mixer upper / scramble letters with variations of unicode."""

    NAME = "hackermix"
    """subcommand name."""

    def mouse_callback(self, _):
        """no action."""

    # pylint: disable=arguments-differ
    # pylint: disable=attribute-defined-outside-init
    def setup(self, word: str):
        """Scroll through all Variations of a word with mixed unicode values for letters."""
        self.seen = set()
        """keep track of what's been seen."""
        self.mixer = LetterMixer()
        """Main mixer class."""
        self.alphabet_dict = self.mixer.alphabet_dict
        """main alphabet dict."""
        self.object_dict = self.mixer.object_dict
        """letter object dictionary map."""
        # Unset scroll values, we're going to reuse them
        try:
            del self.nav.values[curses.KEY_UP]
            del self.nav.values[curses.KEY_DOWN]
        except KeyError:
            pass

        self.set_word(word)
        # order is important here
        super().setup()

        self.let_idx = self._get_lpos()
        """letter index."""
        self.nav.add_item(
            NavItem(
                "n",
                "Random Next",
            ).set_func(self.new)
        )
        self.nav.add_item(
            NavItem(
                "p",
                "Previous",
            ).set_func(self.prev)
        )
        self.nav.add_item(
            NavItem(
                "l",
                "shift right",
            )
            .set_func(self.shift_left)
            .add_alias(curses.KEY_RIGHT)
        )
        self.nav.add_item(
            NavItem(
                "h",
                "shift left",
            )
            .set_func(self.shift_right)
            .add_alias(curses.KEY_LEFT)
        )
        self.nav.add_item(
            NavItem(
                "k",
                "previous letter",
            )
            .set_func(self.next_letter)
            .add_alias(curses.KEY_DOWN)
        )
        self.nav.add_item(
            NavItem(
                "j",
                "next letter",
            )
            .set_func(self.previous_letter)
            .add_alias(curses.KEY_UP)
        )
        self.nav.add_item(
            NavItem(
                "c",
                "change text",
            ).set_func(self.change_text)
        )
        self.is_mouse = False

    def set_word(self, word: str):
        """Set word."""
        self.word = word
        """currently manipulated word."""
        self.letter_pos = 0
        """setup existing (or new) word."""

    def setup_popts(self):
        """setup parser options."""

    def _has_letter(self):
        """return true if letter position is valid."""
        letter = self.word[self.letter_pos]
        if letter not in self.alphabet_dict:
            return False
        return True

    def _get_lpos(self):
        """Get letter position."""
        lpos = {}
        uni_word = self.collection[self.index]
        for ltr_idx in range(len(self.word)):
            normal_let = self.word[ltr_idx]
            uni_val = uni_word[ltr_idx]
            uni_arr = self.alphabet_dict.get(normal_let, [normal_let])
            uni_idx = uni_arr.index(uni_val)
            lpos[ltr_idx] = (normal_let, uni_idx)
        return lpos

    @property
    def uni_word(self):
        """whole unicode mixed word."""
        word = []
        for _, (normal_let, uni_idx) in self.let_idx.items():
            larr = self.alphabet_dict.get(normal_let, [normal_let])
            word.append(larr[uni_idx])
        return "".join(word)

    @property
    def uni_dict(self):
        """value dictionary."""
        normal_let, uni_idx = self.let_idx[self.letter_pos]
        larr = self.alphabet_dict.get(normal_let, [normal_let])
        uni_chr = larr[uni_idx]
        uni_dict = {}
        for v in self.object_dict.get(normal_let, [{"chr": normal_let}]):
            if v["chr"] == uni_chr:
                uni_dict = v
        return {
            "letter": normal_let,
            "uni_arr": larr,
            "uni_idx": uni_idx,
            "uni_chr": uni_chr,
            "uni_dict": uni_dict,
        }

    def _save(self):
        """Save (overwrite entry)."""
        self.collection[self.index] = str(self.uni_word)

    def previous_letter(self):
        """scroll to previous letter in letter_pos."""
        c_let, c_idx = self.let_idx[self.letter_pos]
        larr = self.alphabet_dict.get(c_let, [c_let])
        if c_idx == len(larr) - 1:
            return
        c_idx += 1
        self.let_idx[self.letter_pos] = c_let, c_idx
        self._save()

    def next_letter(self):
        """scroll to next letter in letter_pos."""
        c_let, c_idx = self.let_idx[self.letter_pos]
        if c_idx == 0:
            return
        c_idx -= 1
        self.let_idx[self.letter_pos] = c_let, c_idx
        self._save()

    def shift_left(self):
        """Move letter position left."""
        if self.letter_pos == len(self.word) - 1:
            return
        self.letter_pos += 1
        while not self._has_letter():
            self.letter_pos += 1

    def shift_right(self):
        """Move letter position right."""
        if self.letter_pos == 0:
            return
        self.letter_pos -= 1
        while not self._has_letter():
            self.letter_pos -= 1

    def new(self):
        """Generate new random value."""
        val = self.mixer.mix_word(self.word)
        if val in self.seen:
            self.txt.append(
                f"{val} has been seen before, try again (possibly ran out of values)"
            )
            return
        self.seen.add(val)
        self.collection.append(val)
        self.index += 1

        self.let_idx = self._get_lpos()

    def prev(self):
        """go to previous collection value."""
        super().prev()
        self.let_idx = self._get_lpos()

    def change_text(self):
        """Replace current word / text block."""
        newtxt = self.get_input("Set new text")
        self.setup(newtxt)

    def next(self):
        """move to next random value."""
        super().next()
        self.let_idx = self._get_lpos()

    def obj_display(self):
        """Set object display."""
        udict = self.uni_dict["uni_dict"]
        self.txt.append(Formatter.fmt_single_normal(udict))
        self.txt.append("")

    def _print_menu(self):
        """output menu."""
        sel_txt = self.nav.get_menu_text()
        self.obj_display()

        ulen = len(self.uni_dict["uni_arr"])
        uidx = self.uni_dict["uni_idx"] + 1
        lpos_pad = " " * self.letter_pos
        output = [
            f"index:{self.index} pos:{self.letter_pos} uidx:{uidx}/{ulen}",
            "",
            f"{self.uni_word}",
            f"{lpos_pad}^",
            "\n".join(self.txt),
            sel_txt,
        ]
        self.txt = []
        """placeholder for txt messages."""
        return "\n".join(output)


class PairsDisplay(Formatter):
    """Output all unicode values to STDOUT."""

    NAME = "pairs"
    """subcommand name."""

    def __init__(self):
        """initialize PairsDisplay class."""
        self.pg = PairsGroups()
        """main data class PairsGroups."""
        self.options = []
        """options list for populating calls."""
        self.options.extend(["all"])
        self.options.extend(["_".join(k) for k in self.pg.PAIR_LIST])
        super().__init__()

    def setup_popts(self):
        """setup parser values."""
        parser = self.popts.parser  # type: ArgumentParser
        self.popts.add_filter()
        self.popts.add_exclude()
        self.popts.add_json()
        parser.add_argument(
            "--detail",
            "-d",
            action="store_true",
            default=False,
            help="turn on detailed output",
        )
        parser.add_argument(
            "name",
            type=str,
            default="all",
            choices=self.options,
            help="select pair to output",
        )

    def all(self):
        """Output all the pairs."""
        for tup in self.pg.PAIR_LIST:
            p1, p2 = tup
            yield from self.pg.iter_pair(p1, p2, self.args.filter, self.args.exclude)

    def setup(self):
        """Setup iterator."""

    @staticmethod
    def output_json(iterator: Iterator[Tuple[Tuple[str, str], Tuple[str, Dict, Dict]]]):
        """Output json."""
        retval = {}
        for basename, (name, left, right) in iterator:
            title = " ".join(list(basename) + [name])
            retval.setdefault(title, {})
            retval[title]["pair"] = [left["chr"], right["chr"]]
            retval[title]["p1"] = left
            retval[title]["p2"] = right
        yield json.dumps(retval)

    @staticmethod
    def output_lines(
        iterator: Iterator[Tuple[Tuple[str, str], Tuple[str, Dict, Dict]]],
        detail=False,
    ):
        """Output standard lines."""
        lines = []
        for basename, (name, left, right) in iterator:
            output = []
            output += [
                left["chr"],
                right["chr"],
            ]
            output += list(basename) + [name]
            if detail:
                sublines = "\n".join(
                    [Formatter.fmt_single_normal(i) for i in [left, right]]
                )
                output += [Formatter.tab_shift(sublines, 4)]
            lines.append(" ".join(output))
        yield "\n".join(lines)

    def run(self, override=None):
        """left / right pairs."""
        name = override if override else self.args.name
        if name == "all":
            _iter = self.all()
        else:
            p1, p2 = name.split("_")
            _iter = self.pg.iter_pair(p1, p2, self.args.filter, self.args.exclude)

        if self.args.json:
            itervals = self.output_json(_iter)
        elif self.args.detail:
            itervals = self.output_lines(_iter, True)
        else:
            itervals = self.output_lines(_iter)
        sys.stdout.write("%s\n" % "\n".join(itervals))


SUBCOMMANDS = {
    all_to_stdout.NAME: all_to_stdout(),
    InteractAllGroups.NAME: InteractAllGroups(),
    HackerMixerInteractive.NAME: HackerMixerInteractive(),
    PairsDisplay.NAME: PairsDisplay(),
}
"""Main subcommand dict, this is what the main unicodes cli program uses."""

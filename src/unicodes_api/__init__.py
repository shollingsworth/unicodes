#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print / show characters."""
from typing import Iterator, Dict, List, Any, Tuple, Set
import random
import unicodedata
from unicodes_api.ascii import ASCII_MAP

# pylint: disable=too-few-public-methods,invalid-name
# pylint: disable=pointless-string-statement


LETTERS_NUMBERS = list(
    map(chr, list(range(ord("a"), ord("z") + 1)) + list(range(ord("0"), ord("9") + 1)))
)
"""letters and numbers we want to track for LetterMixer."""


def iter_unicodes() -> Iterator[Dict]:
    """yield all Unicode values.

    returns iterator of dictionaries in the following format::
        {
            "int": i,
            "hex": hval,
            "chr": char,
            "name": name.lower(),
            "pref": pref,
            "htmlent": htmlent,
            "tokens": list,
        }

    example for letter "a"::
        {
            "int": 97,
            "hex": "61",
            "chr": "a",
            "name": "latin small letter a",
            "pref": "\\\\u0061",
            "htmlent": "&#97;"
            "tokens": ["latin", "small", "letter", "a"],
        }
    """
    for i in range(0x10FFFF):
        try:
            name = unicodedata.name(chr(i))
        except ValueError:
            name = ""
        if not name and i in ASCII_MAP:
            name = ASCII_MAP[i]["description"]
        if not name:
            continue
        char = chr(i)
        hval = str(hex(i)).replace("0x", "")
        if i < 0xFFFF:
            pref = f"\\u{hval.zfill(4)}"
        else:
            pref = f"\\U{hval.zfill(8)}"

        htmlent = f"&#{i};"

        tokens = [i.lower() for i in " ".join(name.split("-")).split()]
        try:
            yield {
                "chr": char,
                "name": name.lower(),
                "int": i,
                "hex": hval,
                "python": pref,
                "html": htmlent,
                "tokens": tokens,
            }
        except UnicodeEncodeError:
            pass


class Pairs:
    """Pre built filter for pairs of unicode objects."""

    def __init__(
        self,
        left: str,
        right: str,
        include_tokens=None,  # type: Any | List
        exclude_tokens=None,  # type: Any | List
    ):
        """initialize pairs class."""
        self.include_tokens = include_tokens or []
        """include tokens."""
        self.exclude_tokens = exclude_tokens or []
        """exclude tokens."""
        self.left = left
        """current left position."""
        self.right = right
        """current right position."""
        self.groups = Groups()
        """main groups class."""
        self.groups.make_tokenized()
        self.vals = self._setup()
        """token values."""

    def _setup(self):
        """Setup data."""
        vals = {}
        for key in [self.left, self.right]:
            for v in self.groups.get_vals(key):
                name = v["name"]
                toks = v["tokens"]
                if any(i in toks for i in self.exclude_tokens):
                    continue
                if self.include_tokens and any(i in toks for i in self.include_tokens):
                    vals[name] = v
                    continue
                vals[name] = v
        return vals

    def _pairs(
        self, includes: list = None, excludes: list = None
    ) -> Iterator[Tuple[str, Dict, Dict]]:
        """Base iterator."""
        stubs = []
        includes = includes or []
        excludes = excludes or []

        def _pname(val):
            arr = val.replace("__STUB__", "").split()
            return " ".join(i.strip().strip("-") for i in arr)

        for name, _ in self.vals.items():
            if self.left in name:
                stub = name.replace(self.left, "__STUB__")
                stubs.append(stub)

        for stub in stubs:
            key1, key2 = (
                stub.replace("__STUB__", self.left),
                stub.replace("__STUB__", self.right),
            )
            left = self.vals.get(key1, {})
            right = self.vals.get(key2, {})
            if all([left, right]):
                name = _pname(stub)
                toks = left["tokens"]
                toks += right["tokens"]
                if any(i in toks for i in excludes):
                    continue
                if includes and not all(i in toks for i in includes):
                    continue
                yield name, left, right

    def pairs(self, includes: list, excludes: list):
        """return sorted pairs."""
        _sort = lambda x: (x[1]["chr"], x[2]["chr"])
        yield from sorted(self._pairs(includes, excludes), key=_sort)


class Groups:
    """Pre built filter for groups of unicode objects."""

    CACHED = {}
    """Cached iter_unicodes List[Dict]."""
    TOKENIZED = {}
    """Cached tokenized dict of set of keys."""

    @staticmethod
    def _make_cache():
        """Make cache."""
        if Groups.CACHED:
            return
        for dval in iter_unicodes():
            key = tuple(dval["tokens"])
            Groups.CACHED[key] = dval

    def make_tokenized(self):
        """Make tokenized data."""
        # already been here
        if Groups.TOKENIZED:
            return

        if not Groups.CACHED:
            self._make_cache()

        for key in self.CACHED:
            for token in key:
                Groups.TOKENIZED.setdefault(token, set())
                Groups.TOKENIZED[token].add(key)
        tkeys = list(Groups.TOKENIZED.keys())
        for token in tkeys:
            try:
                int(token)
                del Groups.TOKENIZED[token]
                continue
            except ValueError:
                pass
            if len(Groups.TOKENIZED[token]) < 3:
                del Groups.TOKENIZED[token]

    def grouping(
        self,
        include_tokens: list,
        exclude_tokens: list = None,
    ):
        """Group token values."""
        self.make_tokenized()
        exclude_tokens = exclude_tokens or []
        includes = [self.TOKENIZED[i] for i in include_tokens]
        excludes = [self.TOKENIZED[i] for i in exclude_tokens]
        _inc = set.intersection(*includes)
        _inc.difference_update(*excludes)
        for i in _inc:
            yield self.CACHED[i]

    def get_vals(self, token) -> Iterator[Dict]:
        """Get dictionary values for token."""
        self.make_tokenized()
        for key in self.TOKENIZED[token]:
            yield self.CACHED[key]

    def iter_all_groups(self) -> Iterator[Tuple[str, List[Dict]]]:
        """Iterate through all groups."""
        self.make_tokenized()
        for tup in sorted(self.TOKENIZED.items()):
            token = tup[0]  # type: str
            tset = tup[1]  # type: Set
            tsets = [self.CACHED[i] for i in tset]
            yield token, tsets

    def group_names(self) -> Iterator[Tuple[str, int]]:
        """Iterate through group names."""
        self.make_tokenized()
        groups = []
        for token, keys in self.TOKENIZED.items():
            groups.append((len(keys), token))
        for tlen, token in sorted(groups, reverse=True):
            yield token, tlen


class LetterMixer:
    """Letter mixer clas."""

    def __init__(self):
        """Init class."""
        self.group = Groups()
        """main group data."""
        self.group.make_tokenized()
        self.alphabet_dict = self._alphabet_dict()
        """re-usable alphabet_dict."""
        self.object_dict = self._obj_dict()
        """re-usable object dict."""

    def _yield_letter(self, letter) -> Iterator[Dict]:
        """Yield letter mixer values for letter/digit that corresponds to the unicode varients."""
        excludes = [
            "tag",
            "fullwidth",
            "combining",
            "squared",
            "circled",
            "parenthesized",
        ]
        digit_map = {
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
        }
        alpha_token_groups = [
            "latin",
            "cyrillic",
            "carian",
            "osage",
            "lydian",
            "old",
            "cherokee",
            "rejang",
            "lisu",
            "modifier",
        ]
        digit_token_groups = [
            "mathematical",
            "latin",
            "digit",
            "number",
        ]
        main = "digit" if letter in digit_map else "letter"
        dg = digit_token_groups if letter in digit_map else alpha_token_groups
        for g in dg:
            args = [
                main,
                g,
                digit_map.get(letter, letter),
            ]
            yield from self.group.grouping(args, excludes)

    def _alphabet_dict(self):
        """Generated alphabet_dict."""
        return {
            letter: sorted(list(z["chr"] for z in self._yield_letter(letter)))
            for letter in LETTERS_NUMBERS
        }

    def _obj_dict(self):
        """Generated object dict."""
        return {letter: list(self._yield_letter(letter)) for letter in LETTERS_NUMBERS}

    def mix_word(self, word):
        """Mix up the word with unicode varients."""
        adict = self.alphabet_dict
        avals = [adict.get(i.lower(), [i]) for i in word]
        lens = [len(i) for i in avals]
        rset = [random.randint(0, i - 1) for i in lens]
        return "".join([avals[idx][z] for idx, z in enumerate(rset)])


class PairsGroups:
    """Pair groups class."""

    PAIR_LIST = {
        ("left", "right"): {
            "inc_tokens": ["left", "right"],
            "exl_tokens": [],
        },
        ("top", "bottom"): {
            "inc_tokens": ["top", "bottom"],
            "exl_tokens": [],
        },
        ("horz", "vert"): {
            "inc_tokens": ["horizontal", "vertical"],
            "exl_tokens": [],
        },
        ("upper", "lower"): {
            "inc_tokens": ["upper", "lower"],
            "exl_tokens": [],
        },
    }
    """Static list of pairs."""

    @staticmethod
    def iter_pair(
        p1,
        p2,
        extra_includes: list = None,
        extra_excludes: list = None,
    ) -> Iterator[Tuple[Tuple[str, str], Tuple[str, Dict, Dict]]]:
        """left / right pairs."""
        tup = (p1, p2)
        extra_includes = extra_includes or []
        extra_excludes = extra_excludes or []
        args = PairsGroups.PAIR_LIST[tup]["inc_tokens"]

        excl = PairsGroups.PAIR_LIST[tup]["exl_tokens"]
        excl.extend(extra_excludes)
        obj = Pairs(*args)
        for i in obj.pairs(extra_includes, extra_excludes):
            yield tup, i

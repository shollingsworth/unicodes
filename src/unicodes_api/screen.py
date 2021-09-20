#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test."""
from typing import Any, Callable, Dict, List
import sys
import argparse
import curses
from curses.textpad import Textbox
from abc import abstractmethod, ABC
from unicodes_api.parser import ParserOpts
from unicodes_api.parser import Formatter

# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init
# pylint: disable=arguments-differ

SEP = "    "
"""Default separator."""


class NavItem:
    """Navigation item class."""

    def __init__(self, main_key: Any, description: str):
        """initialize NavItem class."""
        self.description = description
        """Navigation item description."""
        self.key = None  # type: Any | int
        """key integer value."""
        if isinstance(main_key, int):
            self.key = main_key
        else:
            self.key = ord(main_key)
        self.func = None  # type: Any | Callable
        """main Callback function."""
        self.callbacks = []  # type: List[Callable]
        """Additional callback functions."""
        self.aliases = []
        """int key code aliases."""
        self.hidden = False
        """set if menu is hidden."""

    @property
    def key_name(self):
        """Key name."""
        return curses.keyname(self.key).decode()

    def set_hidden(self):
        """Set menu item to hidden."""
        self.hidden = True
        return self

    def set_func(self, func):
        """Set menu item function."""
        self.func = func
        return self

    def add_callback(self, func):
        """Add to menu item callbacks."""
        self.callbacks.append(func)
        return self

    def add_alias(self, alias: int):
        """Add key alias."""
        self.aliases.append(alias)
        return self

    def run(self):
        """Run attached function and callbacks for menu item."""
        for cb in self.callbacks:
            cb()
        self.func()


class NavGroup:
    """Group of NavItems."""

    def __init__(self, controller: Any):
        """Initialize group."""
        self.values = {}  # type: Dict[int, NavItem]
        """collection of navigation menu items."""
        self.controller = controller  # type: BidirectionalIterator
        """calling controller."""
        self.scroll_values = {
            curses.KEY_MOUSE: self.controller.mouseclick,
            curses.KEY_RESIZE: lambda: self.controller.scroll(0),
            curses.KEY_HOME: lambda: self.controller.scroll(0),
            curses.KEY_END: lambda: self.controller.scroll(sys.maxsize),
            curses.KEY_PPAGE: lambda: self.controller.scroll(
                -1 * self.controller.height
            ),
            curses.KEY_NPAGE: lambda: self.controller.scroll(
                1 * self.controller.height
            ),
            curses.KEY_UP: lambda: self.controller.scroll(-1),
            curses.KEY_DOWN: lambda: self.controller.scroll(1),
        }
        """scrolling / mouse related commands."""
        self.add_item(NavItem("q", "Quit").set_func(self.quit))
        for k, func in self.scroll_values.items():
            self.add_item(
                NavItem(k, f"hidden code {k}").set_hidden().set_func(func),
            )

    @staticmethod
    def quit():
        """Quit!."""
        raise KeyboardInterrupt

    def add_item(self, item: NavItem):
        """Add menu item."""
        self.values[item.key] = item
        return self

    def get_menu_text(self):
        """Get menu text."""
        val = f"\n{SEP}".join(
            [
                f"({item.key_name})/{item.description}"
                for _, item in self.values.items()
                if not item.hidden
            ]
        )
        return f"Make Selection:\n{SEP}{val}"

    def get_nav_item(self, kp):
        """Get nav item."""
        retval = None  # type: NavItem | Any
        if kp in self.values:
            return self.values[kp]
        for item in self.values.values():
            if kp in item.aliases:
                return item
        return retval


class BidirectionalIterator(ABC):
    """Base class Terminal keypress class that allows you to navigate collections."""

    NAME = ""
    """subcommand name."""
    PAD_MAX_HEIGHT = 30000
    """initial setting of curses window size."""

    def __init__(self):
        """Init class."""
        self.popts = ParserOpts(self.NAME, self.__class__)
        """Parser options."""
        self.setup_popts()
        self.is_mouse = True
        """initial setting for enabling/disabling mouse interaction."""
        self.args = None  # type: Any | argparse.Namespace
        """future argparse.Namespace value."""
        self.highlight_vals = []
        """values to hightlight."""
        self.height = 0
        """terminal max height."""
        self.width = 0
        """terminal max width."""
        self.nav = NavGroup(self)
        """Navigation group."""
        self.items = []
        """output lines."""

    @abstractmethod
    def mouse_callback(self, value):
        """setup argparse options."""

    @abstractmethod
    def setup_popts(self):
        """setup argparse options."""

    def set_args(self, args: argparse.Namespace):
        """Set argparse args."""
        self.args = args

    def toggle_mouse(self):
        """toggle mouse switch."""
        if self.is_mouse:
            self.is_mouse = False
        else:
            self.is_mouse = True
        curses.mousemask(self.is_mouse)
        self._dowrite()

    def setup(self):
        """Run setup before run."""
        self.collection = []
        """collection of values."""
        self.index = -1
        """Current collection value."""
        self.txt = []
        """supplemental messages."""
        self.kp = "\0"
        """initial key press value."""
        self.nav.add_item(NavItem("n", "Next").set_func(self.next))
        self.nav.add_item(NavItem("p", "Previous").set_func(self.prev))

    def getch(self):
        """Get next keypress."""
        return self.pad.getch()

    @abstractmethod
    def next(self):
        """menu item next."""

    @abstractmethod
    def prev(self):
        """menu item previous."""

    @property
    def current_value(self):
        """return current value."""
        return "".join(i for i in self.collection[self.index] if i)

    def _print_menu(self):
        """Output text."""
        sel_txt = self.nav.get_menu_text()
        output = [
            f"index:{self.index}",
            "",
            self.current_value,
            "\n".join(self.txt),
            sel_txt,
        ]
        lout = "\n".join(output).replace("\0", "NULL")
        self.txt = []
        return lout

    @staticmethod
    def get_input(prompt):
        """Get user input through the user interface and return it."""
        inp = curses.newwin(8, 55, 0, 0)
        inp.addstr(1, 1, prompt)
        sub = inp.subwin(3, 41, 2, 1)
        sub.border()
        sub2 = sub.subwin(1, 40, 3, 2)
        tb = Textbox(sub2)
        inp.refresh()
        tb.edit()
        arr = tb.gather().split()
        if arr[-1] == "x":
            arr.pop()
        return " ".join(arr)

    def _trywrite(self, *args):
        """Attempt to write, and pass if failure occurs."""
        try:
            self.pad.addstr(*args)
            return True
        except curses.error:
            return False

    def _dowrite(self):
        """perform a bunch of operations to ensure the curses screen renders properly."""
        self.pad.clear()
        txt = self._print_menu()
        txt = Formatter.tab_shift(txt, 1)
        self.items = txt.split("\n")
        # insert a new line at top
        self.items.insert(0, "")
        arg_set = []
        pad = " "
        for _, line in enumerate(self.items):
            spl = line.split(" ")
            for v in spl:
                if v in self.highlight_vals:
                    for ch in v:
                        arg_set.append([f"{pad}{ch}{pad}", curses.A_STANDOUT])
                else:
                    for ch in v:
                        arg_set.append([ch])
                arg_set.append([" "])
            arg_set.append(["\n"])
        for arg in arg_set:
            self._trywrite(*arg)
        self.pad_refresh()

    def pad_refresh(self):
        """Refresh screen."""
        height, width = self.win.getmaxyx()
        if (height, width) != (self.height, self.width):
            self._run(self.win)
        self.win.refresh()
        self.pad.refresh(self.pad_pos, 0, 0, 0, self.height - 1, self.width)

    @staticmethod
    def _get_mouse_breakout(line: bytes, y):
        """Get character / word / line from where the mouse is clicked."""
        line = line.decode()
        try:
            char = line[y]
        except IndexError:
            return {
                "chr": "",
                "word": "",
                "line": "",
            }
        words = {}
        word = []
        for idx, _ch in enumerate(line):
            words[idx] = word
            if not _ch.strip():
                word = []
            else:
                word.append(_ch)
        words = {
            idx: "".join(i for i in arr if i.strip()) for idx, arr in words.items()
        }
        word = words[y].strip()
        return {
            "chr": char,
            "word": word,
            "line": line,
        }

    def mouseclick(self):
        """Scrolling the window when pressing up/down arrow keys"""
        if not self.is_mouse:
            return
        try:
            _, y, x, _, _ = curses.getmouse()
        except curses.error:
            return

        line = self.pad.instr(x, 0, self.width)
        self.mouse_callback(self._get_mouse_breakout(line, y))
        self.pad_refresh()

    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        maxnum = len(self.items)
        num = int(self.pad_pos)
        num += direction
        if num < 0:
            num = 0
        elif num > maxnum - self.height:
            num = maxnum - self.height
        self.pad_pos = num
        self.pad_refresh()

    def _run(self, win):
        """run program (for reals)."""
        self.win = win  # type: curses.window
        """Main curses window."""
        self.win.keypad(True)
        self.win.scrollok(True)
        self.height, self.width = self.win.getmaxyx()

        self.pad = curses.newpad(self.PAD_MAX_HEIGHT, self.width)
        """pad value."""

        self.pad.keypad(True)
        self.pad.scrollok(True)

        #  border = ["║", "║", "═", "═", "╔", "╗", "╚", "╝"]
        # border = ["|", "|", "-", "-", "+", "+", "+", "+"]
        # self.pad.border(*border)
        # self.win.border(1)
        # self.pad.border(1)

        self.pad_pos = 0
        """initial pad position."""
        self.pad_refresh()

        self._dowrite()

        while True:
            kp = self.getch()
            item = self.nav.get_nav_item(kp)
            if not item:
                self.txt.append(f"Invalid key / {curses.keyname(kp).decode()}")
                self._dowrite()
            else:
                item.run()
                self._dowrite()

    def run(self):
        """Run cli command."""
        try:
            curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            curses.mousemask(1)
            # wrap the real program
            curses.wrapper(self._run)
        except KeyboardInterrupt:
            curses.endwin()
            sys.stdout.write("Bye!\n")


class BidirectionalNewIterator(BidirectionalIterator):
    """Terminal keypress class that allows you to navigate collections."""

    def setup(self):
        """Setup class."""
        super().setup()
        self.new()

    @abstractmethod
    def new(self):
        """menu item new."""

    def next(self):
        """next navigation."""
        if self.index == len(self.collection) - 1:
            self.new()
        else:
            self.index += 1

    def prev(self):
        """previous navigation."""
        if self.index <= 0:
            self.txt.append("No previous entry")
            return
        self.index -= 1


class BidirectionalStaticStopIterator(BidirectionalIterator):
    """Bidirection static Iterator."""

    def setup(self, collection: list):
        """Setup for run."""
        super().setup()
        self.collection = collection
        self.index = 0

    def next(self):
        """scroll to next value."""
        if self.index == len(self.collection) - 1:
            self.txt.append("No next entry")
            return
        self.index += 1

    def prev(self):
        """Scroll to previous value."""
        if self.index <= 0:
            self.txt.append("No previous entry")
            return
        self.index -= 1


class BidirectionalStaticRevolvingIterator(BidirectionalIterator):
    """Bi directional static revolving iterator."""

    def setup(self, collection: list):
        """Setup class."""
        super().setup()
        self.collection = collection
        self.index = 0

    def next(self):
        """next navigation."""
        if self.index == len(self.collection) - 1:
            self.index = 0
        else:
            self.index += 1

    def prev(self):
        """previous navigation."""
        if self.index == 0:
            self.index = len(self.collection) - 1
        else:
            self.index -= 1

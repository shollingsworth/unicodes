[![github-issues](https://img.shields.io/github/issues/shollingsworth/unicodes?style=plastic "github-issues")](https://github.com/shollingsworth/unicodes/issues) [![github-languages-code-size](https://img.shields.io/github/languages/code-size/shollingsworth/unicodes?style=plastic "github-languages-code-size")](https://github.com/shollingsworth/unicodes) [![github-stars](https://img.shields.io/github/stars/shollingsworth/unicodes?style=plastic "github-stars")](https://github.com/shollingsworth/unicodes/stargazers) [![github-forks](https://img.shields.io/github/forks/shollingsworth/unicodes?style=plastic "github-forks")](https://github.com/shollingsworth/unicodes/network/members) 

[![pypi-v](https://img.shields.io/pypi/v/unicodes?style=plastic "pypi-v")](https://pypi.org/project/unicodes) [![pypi-status](https://img.shields.io/pypi/status/unicodes?style=plastic "pypi-status")](https://pypi.org/project/unicodes) [![pypi-l](https://img.shields.io/pypi/l/unicodes?style=plastic "pypi-l")](https://pypi.org/project/unicodes) [![pypi-dm](https://img.shields.io/pypi/dm/unicodes?style=plastic "pypi-dm")](https://pypi.org/project/unicodes) [![pypi-pyversions](https://img.shields.io/pypi/pyversions/unicodes?style=plastic "pypi-pyversions")](https://pypi.org/project/unicodes) [![pypi-implementation](https://img.shields.io/pypi/implementation/unicodes?style=plastic "pypi-implementation")](https://pypi.org/project/unicodes) 

# TOC
* [Unicodes](#unicodes-)
   * [Installation / Quickstart](#installation---quickstart-)
   * [License](#license-)
   * [Other Docs](#other-docs-)
   * [Examples](#examples-)
   * [Command Help](#command-help-)


# Unicodes [&#8593;](#toc)
This program allows you to interactively explore, search, and output unicode values in the terminal

Pull requests welcome!
## Installation / Quickstart [&#8593;](#toc)
To install this package from [pypy](https://pypi.org/project/unicodes/) run the following command.


```

pip3 install unicodes

```


Run this to show all the unicode values


```

unicodes all

```

## License [&#8593;](#toc)
See: [LICENSE](./LICENSE)
## Other Docs [&#8593;](#toc)
* [Api Docs](https://shollingsworth.github.io/unicodes/)
* [Changelog](./CHANGELOG.md)
## Examples [&#8593;](#toc)
## [all_box_drawings.sh](https://github.com/shollingsworth/unicodes/blob/main/media/demo/all_box_drawings.sh)
> Show all unicode names with 'drawing' and 'box' in their names
![all_box_drawings.sh](https://github.com/shollingsworth/unicodes/raw/main/media/all_box_drawings.sh.png)
## [all_playing_cards_no_trump.sh](https://github.com/shollingsworth/unicodes/blob/main/media/demo/all_playing_cards_no_trump.sh)
> Show all playing cards minus trump string
![all_playing_cards_no_trump.sh](https://github.com/shollingsworth/unicodes/raw/main/media/all_playing_cards_no_trump.sh.png)
## [hacker_mixer.sh](https://github.com/shollingsworth/unicodes/blob/main/media/demo/hacker_mixer.sh)
> hacker mix 'my cool name' in a tui
![hacker_mixer.sh](https://github.com/shollingsworth/unicodes/raw/main/media/hacker_mixer.sh.png)
## [show_all_pairs.sh](https://github.com/shollingsworth/unicodes/blob/main/media/demo/show_all_pairs.sh)
> show pre-defined pairs of unicode objects (i.e. left/right up/down etc.)
![show_all_pairs.sh](https://github.com/shollingsworth/unicodes/raw/main/media/show_all_pairs.sh.png)
## Command Help [&#8593;](#toc)
# Main
```
usage: gendoc.py [-h] {all,explore,hackermix,pairs} ...

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  {all,explore,hackermix,pairs}
    all                 Output all unicode values to STDOUT.
    explore             Explore the tokenized unicode data.
    hackermix           Hacker mixer upper / scramble letters with variations of unicode.
    pairs               Output all unicode values to STDOUT.

```
## all
```
usage: gendoc.py all [-h] [--filter [FILTER [FILTER ...]]] [--exclude [EXCLUDE [EXCLUDE ...]]] [--json]

optional arguments:
  -h, --help            show this help message and exit
  --filter [FILTER [FILTER ...]], -f [FILTER [FILTER ...]]
                        filter values
  --exclude [EXCLUDE [EXCLUDE ...]], -e [EXCLUDE [EXCLUDE ...]]
                        reverse filter
  --json, -j            print in json format

```
## explore
```
usage: gendoc.py explore [-h]

optional arguments:
  -h, --help  show this help message and exit

```
## hackermix
```
usage: gendoc.py hackermix [-h] ...

positional arguments:
  args        word

optional arguments:
  -h, --help  show this help message and exit

```
## pairs
```
usage: gendoc.py pairs [-h] [--filter [FILTER [FILTER ...]]] [--exclude [EXCLUDE [EXCLUDE ...]]] [--json] [--detail]
                       {all,left_right,top_bottom,horz_vert,upper_lower}

positional arguments:
  {all,left_right,top_bottom,horz_vert,upper_lower}
                        select pair to output

optional arguments:
  -h, --help            show this help message and exit
  --filter [FILTER [FILTER ...]], -f [FILTER [FILTER ...]]
                        filter values
  --exclude [EXCLUDE [EXCLUDE ...]], -e [EXCLUDE [EXCLUDE ...]]
                        reverse filter
  --json, -j            print in json format
  --detail, -d          turn on detailed output

```

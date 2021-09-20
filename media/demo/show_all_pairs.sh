#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# shellcheck disable=SC2034
DESC="show pre-defined pairs of unicode objects (i.e. left/right up/down etc.)"

unicodes pairs all
read

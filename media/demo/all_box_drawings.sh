#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# shellcheck disable=SC2034
DESC="Show all unicode names with 'drawing' and 'box' in their names"

unicodes all -f drawing -f box
read

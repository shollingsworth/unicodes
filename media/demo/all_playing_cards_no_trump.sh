#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# shellcheck disable=SC2034
DESC="Show all playing cards minus trump string"

unicodes all -f playing -f card -e trump
read

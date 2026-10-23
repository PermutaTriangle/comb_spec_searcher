#!/bin/sh
set -eu

tilings_dir="${1:-.tilings}"

if [ -d "$tilings_dir/.git" ]
then
    git -C "$tilings_dir" fetch --depth 1 origin develop
    git -C "$tilings_dir" checkout --detach FETCH_HEAD
else
    git clone --depth 1 --branch develop https://github.com/PermutaTriangle/Tilings.git "$tilings_dir"
fi

# tox installs the CSS version under test and Permuta before running this script.
# Keep that CSS installation when adding the downstream project.
python -m pip install --no-deps "$tilings_dir"

#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

SOURCE_URL="git@github.com:4teamwork/opengever.core.git"
TARGET_URL="git@github.com:OneGov/onegov.gever.git"

MIRRORING_DIR="$HOME/opengever.core-mirroring"
BARE_CLONE_DIR="${MIRRORING_DIR}/opengever.core.git"


mkdir -p "${MIRRORING_DIR}"

if [ ! -d "${BARE_CLONE_DIR}" ]; then
    # Create a bare mirrored clone once if it doesn't exist yet
    git clone --mirror "${SOURCE_URL}" "${BARE_CLONE_DIR}"

    # Set the push location to mirror
    cd "${BARE_CLONE_DIR}"
    cat << EOF > ./config
[core]
    repositoryformatversion = 0
    filemode = true
    bare = true
    ignorecase = true
    precomposeunicode = true
[remote "origin"]
    url = git@github.com:4teamwork/opengever.core.git
    mirror = true
    pushurl = git@github.com:OneGov/onegov.gever.git
    fetch = +refs/heads/master:refs/heads/master
    fetch = +refs/tags/*:refs/tags/*
EOF

    rm ./packed-refs
    git fetch --prune origin
fi

# Fetch changes and push to mirror
cd "${BARE_CLONE_DIR}"
git fetch --prune origin
git push --mirror
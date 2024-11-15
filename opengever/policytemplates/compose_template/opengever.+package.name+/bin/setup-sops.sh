#!/usr/bin/env bash

if ! [ -x "$(command -v sops)" ]; then
  echo 'Error: sops command not found.' >&2
  exit 1
fi
if ! [ -x "$(command -v age)" ]; then
  echo 'Error: age command not found.' >&2
  exit 1
fi

root_dir=$(git rev-parse --show-toplevel)
if [ ! -f "$root_dir/.age.key" ]; then
  if [ -x "$(command -v op)" ]; then
    echo "No age key found. Retrieving from 1Password..."
    repo_name="$(basename $(git remote get-url origin))"
    repo_name="${repo_name%.git}"
    op read "op://SOPS/${repo_name}/notesPlain" -o "${root_dir}/.age.key"
  else
    echo "Error: age key not found."
    exit 1
  fi
fi

git config --local filter.sops-dotenv.clean "./bin/sops-encrypt.sh %f"
git config --local filter.sops-dotenv.smudge "./bin/sops-decrypt.sh"
git config --local filter.sops-dotenv.required true
git config --local diff.sops-diff.textconv cat

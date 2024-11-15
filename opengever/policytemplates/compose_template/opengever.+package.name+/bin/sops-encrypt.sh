#!/bin/bash
export SOPS_AGE_KEY_FILE=$(pwd)/.age.key

INPUT=$(cat)
ENCRYPTED=$(sops --encrypt --input-type dotenv --output-type dotenv /dev/stdin <<<"${INPUT}")
CONTENTS=$(git cat-file -p "HEAD:${1}" 2>/dev/null)
DECRYPTED=$(sops --decrypt --input-type dotenv --output-type dotenv /dev/stdin <<<"${CONTENTS}" 2>/dev/null)

if [[ -z "${CONTENTS}" || "${DECRYPTED}" != "${INPUT}" ]]
then
  echo "${ENCRYPTED}"
else
  echo "${CONTENTS}"
fi

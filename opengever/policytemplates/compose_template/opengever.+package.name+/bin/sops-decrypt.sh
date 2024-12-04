#!/bin/bash
export SOPS_AGE_KEY_FILE=$(pwd)/.age.key
sops --decrypt --input-type dotenv --output-type dotenv /dev/stdin

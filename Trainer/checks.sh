#!/bin/bash

set -xe

sudo id

nvidia-smi

for dir in $(find /mnt/ -maxdepth 1 -type d);
do
    echo "Checking ${dir} ..."
    if [ ! -w "${dir}" ]; then
        echo "Directory ${dir} is not writeable, sorry."
	exit 1
    fi;
done;

# Check if push to hub but no token given
if [ "${PUSH_TO_HUB}" == 1 ] && [ -z "${HUB_API_TOKEN}" ]; then
    echo "Cannot push to hub without token, sorry."
    exit 1
fi;

python ${HOMEDIR}/print_gpus.py

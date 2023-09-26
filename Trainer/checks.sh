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

python ${HOMEDIR}/print_gpus.py

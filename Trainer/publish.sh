#!/usr/bin/bash

set -xe

if [ "$USE_PEFT" = 1 ] && ([ "$USE_4BIT" = 1 ] || [ "$USE_8BIT" = 1 ]) ; then 
    python ${HOMEDIR}/push_model.py
fi

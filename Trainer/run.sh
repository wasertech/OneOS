#!/bin/bash

echo You are in `pwd`

${HOMEDIR}/checks.sh
${HOMEDIR}/train.sh
${HOMEDIR}/publish.sh
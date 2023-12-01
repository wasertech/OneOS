#!/usr/bin/env bash

function download_file {
    fileuri=$1
    filename=$2
    curl -o "${filename}" "${fileuri}"
}

base_uri="https://raw.githubusercontent.com/TellinaTool/nl2bash/master/data/bash/"

f="nl2shell.en.nl"
if [ -f ${f} ]; then
    echo "File ${f} already exist"
else
    echo "Downloading ${f}..."
    download_file "${base_uri}/all.nl" "${f}"
fi

f="nl2shell.cm"
if [ -f ${f} ]; then
    echo "File ${f} already exist"
else
    echo "Downloading ${f}..."
    download_file "${base_uri}/all.cm" "${f}"
fi

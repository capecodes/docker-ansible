#!/bin/bash

# see https://pypi.python.org/pypi/ansible

MAJOR_VERSION=latest
EXACT_VERSION=2.4.0.0

./build.sh ${EXACT_VERSION}
./push.sh ${MAJOR_VERSION} ${EXACT_VERSION}
#!/bin/bash

# see https://pypi.python.org/pypi/ansible

MAJOR_VERSION=2.3
EXACT_VERSION=2.3.2.0

./build.sh ${EXACT_VERSION}
./push.sh ${MAJOR_VERSION} ${EXACT_VERSION}
#!/bin/bash

# see https://pypi.python.org/pypi/ansible

MAJOR_VERSION=2.2
EXACT_VERSION=2.2.3.0

./build.sh ${EXACT_VERSION}
./push.sh ${MAJOR_VERSION} ${EXACT_VERSION}
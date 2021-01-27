#!/bin/bash

# (C) 2017, Cape Codes, <info@cape.codes>
# Dual licensed with MIT and GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# see https://pypi.python.org/pypi/ansible

MAJOR_VERSION=2.10
EXACT_VERSION=2.10.5

./build.sh ${EXACT_VERSION} Dockerfile_2.10_up
./push.sh ${MAJOR_VERSION} ${EXACT_VERSION}

MAJOR_VERSION=latest

./push.sh ${MAJOR_VERSION} ${EXACT_VERSION}
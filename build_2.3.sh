#!/bin/bash

# (C) 2017, Cape Codes, <info@cape.codes>
# Dual licensed with MIT and GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# see https://pypi.python.org/pypi/ansible

MAJOR_VERSION=2.3
EXACT_VERSION=2.3.3.0

./build.sh ${EXACT_VERSION} Dockerfile_2.4_down
./push.sh ${MAJOR_VERSION} ${EXACT_VERSION}

#!/bin/bash

# (C) 2017, Cape Codes, <info@cape.codes>
# Dual licensed with MIT and GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

set -e

ANSIBLE_VERSION="$1"

docker build --build-arg ANSIBLE_PIP_VERSION=${ANSIBLE_VERSION} -t capecodes/ansible:${ANSIBLE_VERSION} .
#!/bin/bash

set -e

ANSIBLE_VERSION="$1"

docker build --build-arg ANSIBLE_PIP_VERSION=${ANSIBLE_VERSION} -t capecodes/ansible:${ANSIBLE_VERSION} .
#!/bin/bash

set -e

MAJOR_VERSION="$1"
EXACT_VERSION="$2"

docker push capecodes/ansible:${EXACT_VERSION}

# re-tag with major version and push

echo "Tagging capecodes/ansible:${EXACT_VERSION} to capecodes/ansible:${MAJOR_VERSION}"

docker tag capecodes/ansible:${EXACT_VERSION} capecodes/ansible:${MAJOR_VERSION}

docker push capecodes/ansible:${MAJOR_VERSION}
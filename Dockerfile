FROM alpine:3.6

MAINTAINER Cape Codes <info@cape.codes>

# see https://pypi.python.org/pypi/ansible for published pip versions of ansible

ARG ANSIBLE_PIP_VERSION=2.4.0.0

RUN apk --update add sudo bash krb5 && \
    \
    apk --update add python py-pip openssl ca-certificates sshpass openssh-client && \
    apk --update add --virtual build-dependencies python-dev libffi-dev openssl-dev build-base && \
    \
    pip install ansible==${ANSIBLE_PIP_VERSION} pywinrm cffi netaddr && \
    \
    apk del build-dependencies && \
    rm -rf /var/cache/apk/*

CMD [ "ansible-playbook", "--version" ]

ENV HOME=/root
ENV UID=0
ENV GID=0

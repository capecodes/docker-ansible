# (C) 2017, Cape Codes, <info@cape.codes>
# Dual licensed with MIT and GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

FROM alpine:3.7

MAINTAINER Cape Codes <info@cape.codes>

# see https://pypi.python.org/pypi/ansible for published pip versions of ansible

ARG ANSIBLE_PIP_VERSION=2.4.3.0

RUN apk --update add sudo bash krb5 git expect python py-pip openssl ca-certificates sshpass openssh-client && \
    apk --update add --virtual build-dependencies python-dev libffi-dev openssl-dev build-base && \
    pip install ansible==${ANSIBLE_PIP_VERSION} pywinrm cffi netaddr && \
    apk del build-dependencies && \
    rm -rf /var/cache/apk/*

COPY x_stdout_json_lines.py /x_ansible_stdout_callback/x_stdout_json_lines.py

CMD [ "ansible-playbook", "--version" ]

ENV HOME=/root
ENV UID=0
ENV GID=0

## Versions

# Current
* `latest`, `2.4`, `2.4.0.0`
* `2.3`, `2.3.2.0`
* `2.2`, `2.2.3.0`

## What it contains

# OS
Based on alpine `3.6`, contains OS packages for OpenSSH client (currently `OpenSSH_7.5p1-hpn14v4`), CA certificates, python2, bash, krb5 (kerberos, to support Windows target machines) and any transitive dependencies those bring in.

# Python
Contains `pip` modules for `ansible` and it's transitive dependencies, in addition to `pywinrm` for Windows target machines and `netaddr` to support the Ansible `ipaddr` filter

## How it's built
See https://github.com/capecodes/docker-ansible

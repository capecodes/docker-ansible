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

# Other requirements
The `tail` utility is also utilized, this is included by default in the `alpine` base image

## How it's built
See https://github.com/capecodes/docker-ansible

# LICENSE
Dual licensed under MIT and GNU General Public License v3.0+ (GPLv3)

The user may choose whichever license better suits their needs.

The user should be aware that this Docker image includes the file `x_stdout_json_lines.py` which is an Ansible Callback Plugin which is coded to extend the [default stdout plugin](https://github.com/ansible/ansible/blob/stable-2.4/lib/ansible/plugins/callback/default.py) which itself is GPLv3 licensed.

Therefore, usage of this Ansible Callback Plugin likely implies dynamic linking under the terms of the GPLv3 license, so work based on it likely also needs to be GPLv3 compliant (see the [GPL FAQ here](https://www.gnu.org/licenses/gpl-faq.en.html#GPLStaticVsDynamic)).

However, this licensing restriction should only apply to the source code of the work which encompasses the definition of the Dockerfile for building the Docker image.

Later execution of the Docker image which contains `x_stdout_json_lines.py` from some non-GPL external work should not constituate a "single combined program" with regard to the `x_stdout_json_lines.py` Ansible Callback Plugin.
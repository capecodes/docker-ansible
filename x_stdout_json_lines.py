# (C) 2017, Cape Codes, <info@cape.codes>
# Dual licensed with MIT and GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from io import StringIO

__metaclass__ = type

import sys
import os
import json
import time
import math
import uuid
import pprint
from datetime import date, datetime

# extract a provided UUID used to prefix all outputed lines from this plugin
# this exists so that the external driver knows the key for which to extract
# a known line specification of "UUID { json doc }", that's to say a UUID string
# followed by a space followed by a single line json document
runner_uuid = os.environ['X_ANSIBLE_RUNNER_UUID']

# captures stdout to a list of strings
class CapturingStdout(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

# captures stderr to a list of strings
class CapturingStderr(list):
    def __enter__(self):
        self._stderr = sys.stdout
        sys.stderr = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stderr = self._stderr

# extend the default stdout callback module
from ansible.plugins.callback.default import CallbackModule as DefaultCallbackModule
from ansible.playbook.base import Base
from ansible.executor.task_result import TaskResult
from ansible.inventory.host import Host

class CallbackModule(DefaultCallbackModule):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'x_stdout_json_lines'

    current_play_id = ''
    current_task_id = ''

    def __init__(self):
        self.super_ref = super(CallbackModule, self)

        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.__init__()

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, uuid.UUID):
            return obj.__str__
        elif isinstance(obj, Base):
            return obj.serialize()
        elif isinstance(obj, Host):
            return {
                'name': obj.name,
                'uuid': obj._uuid,
                # 'groups': obj.groups, // groups causes circular reference
                'address': obj.address,
                'implicit': obj.implicit,
                'vars': obj.vars
            }
        elif isinstance(obj, TaskResult):
            return {
                'host': obj._host
                ,
                'task': obj._task
                ,
                'result': obj._result
                ,
                'task_fields': obj._task_fields
            }
        return obj

    def print_json(self, obj):
        """Prints a single compact JSON line to stdout for a given object"""
        try:
            printable_json = json.dumps(obj, indent=None, separators=(',', ':'), default=self.json_serial)
            self.print_uuid_prefixed_line(printable_json)
        except Exception as e:
            self.print_str_lines(['ERROR/print_json: ' + e.message], 'stderr')

    def print_str_lines(self, lines, type):
        """Prints a single compact JSON line to stdout for a given stdout/stderr string"""
        for line in lines:
            obj = {
                'type': type,
                'line': line
            }
            printable_json = json.dumps(obj, indent=None, separators=(',', ':'), default=self.json_serial)
            self.print_uuid_prefixed_line(printable_json)

    def print_uuid_prefixed_line(self, str):
        """Prints a single line with the runner uuid prefix"""
        print(runner_uuid + ' ' + str)

    def v2_playbook_on_play_start(self, play):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_play_start(play)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        self.current_play_id = str(uuid.uuid4())

        try:

            output = {
                'stage': 'on_play_start',
                'type': 'play',
                'epochLong': int(math.floor(time.time() * 1000)),
                'playId': self.current_play_id,
                'data': {
                    'name': play.name
                },
                'raw': play.serialize()
            }

            # remove unused data
            if output['raw']['tasks']:
                del output['raw']['tasks']

            if output['raw']['handlers']:
                del output['raw']['handlers']

            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_playbook_on_play_start: ' + e.message], 'stderr')

    def v2_playbook_on_task_start(self, task, is_conditional):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_task_start(task, is_conditional)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        self.current_task_id = str(uuid.uuid4())

        try:

            output = {
                'stage': 'on_task_start',
                'type': 'task',
                'epochLong': int(math.floor(time.time() * 1000)),
                'taskId': self.current_task_id,
                'playId': self.current_play_id,
                'data': {
                    'name': task.name,
                    'action': task._attributes.get("action"),
                    'attributes': task._attributes,
                    'is_conditional': is_conditional
                },
                'raw': task.serialize()
            }

            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_playbook_on_task_start: ' + e.message], 'stderr')

    def v2_runner_on_ok(self, raw_result, **kwargs):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_on_ok(raw_result, **kwargs)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information

        try:
            # TaskResult has no serialize method, it has a custom clean_copy() instead
            result = raw_result.clean_copy()

            output = {
                'stage': 'on_task_end',
                'type': 'success',
                'epochLong': int(math.floor(time.time() * 1000)),
                'taskId': self.current_task_id,
                'playId': self.current_play_id,
                'data': {
                    'host': str(result._host),
                    'task': str(result._task),
                    'success': True,
                    'changed': result._result.get("changed"),
                    'stdout': result._result.get("stdout"),
                    'stderr': result._result.get("stderr"),
                    'rc': result._result.get("rc"),
                    'result': result._result
                }
            }

            if 'ansible_facts' in output['data']['result']:
                del output['data']['result']['ansible_facts']

            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_runner_on_ok: ' + e.message], 'stderr')

    def v2_runner_on_failed(self, raw_result, ignore_errors=False):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_on_failed(raw_result, ignore_errors)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information

        try:
            # TaskResult has no serialize method, it has a custom clean_copy() instead
            result = raw_result.clean_copy()

            output = {
                'stage': 'on_task_end',
                'type': 'failed',
                'epochLong': int(math.floor(time.time() * 1000)),
                'taskId': self.current_task_id,
                'playId': self.current_play_id,
                'data': {
                    'host': str(result._host),
                    'task': str(result._task),
                    'success': False,
                    'error_message': str(result._result.get("msg")),
                    'stdout': result._result.get("stdout"),
                    'stderr': result._result.get("stderr"),
                    'rc': result._result.get("rc"),
                    'changed': result._result.get("changed"),
                    'result': result._result
                }
            }

            if 'ansible_facts' in output['data']['result']:
                del output['data']['result']['ansible_facts']
                
            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_runner_on_failed: ' + e.message], 'stderr')

    def v2_runner_on_unreachable(self, raw_result):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_on_unreachable(raw_result)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information

        try:
            # TaskResult has no serialize method, it has a custom clean_copy() instead
            result = raw_result.clean_copy()

            output = {
                'stage': 'on_task_end',
                'type': 'unreachable',
                'epochLong': int(math.floor(time.time() * 1000)),
                'taskId': self.current_task_id,
                'playId': self.current_play_id,
                'data': {
                    'host': str(result._host),
                    'task': str(result._task),
                    'success': False,
                    'error_message': str(result._result.get("msg")),
                    'error_type': 'unreachable',
                    'changed': result._result.get("changed")
                }
            }

            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_runner_on_ok: ' + e.message], 'stderr')

    # hook executed when a task is skipped via conditions unmet on a task definition
    def v2_runner_on_skipped(self, raw_result):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_on_skipped(raw_result)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information

        try:
            # TaskResult has no serialize method, it has a custom clean_copy() instead
            result = raw_result.clean_copy()

            output = {
                'stage': 'on_task_end',
                'type': 'skipped',
                'epochLong': int(math.floor(time.time() * 1000)),
                'taskId': self.current_task_id,
                'playId': self.current_play_id,
                'data': {
                    'host': str(result._host),
                    'task': str(result._task),
                    'success': False,
                    'error_message': str(result._result.get("msg")),
                    'error_type': 'skipped',
                    'changed': result._result.get("changed")
                }
            }

            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_runner_on_skipped: ' + e.message], 'stderr')

    def v2_playbook_on_no_hosts_matched(self):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_no_hosts_matched()

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information

        try:

            output = {
                'stage': 'on_play_end',
                'type': 'no_hosts_matched',
                'epochLong': int(math.floor(time.time() * 1000)),
                'playId': self.current_play_id
            }

            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_playbook_on_no_hosts_matched: ' + e.message], 'stderr')

    def v2_playbook_on_no_hosts_remaining(self):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_no_hosts_remaining()

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        try:

            output = {
                'stage': 'on_play_end',
                'type': 'no_hosts_remaining',
                'epochLong': int(math.floor(time.time() * 1000)),
                'playId': self.current_play_id
            }

            self.print_json(output)

        except Exception as e:
            self.print_str_lines(['ERROR/v2_playbook_on_no_hosts_remaining: ' + e.message], 'stderr')

    def v2_playbook_on_stats(self, stats):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_stats(stats)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    # never actually used, see https://github.com/ansible/ansible/issues/19682
    def v2_playbook_on_cleanup_task_start(self, task):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_cleanup_task_start(task)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    def v2_playbook_on_handler_task_start(self, task):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_handler_task_start(task)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        self.current_task_id = str(uuid.uuid4())
        output = {
            'stage': 'on_handler_task_start',
            'type': 'handler_task',
            'epochLong': int(math.floor(time.time() * 1000)),
            'taskId': self.current_task_id,
            'playId': self.current_play_id,
            'data': {
                'name': task.name,
                'action': task._attributes.get("action"),
                'attributes': task._attributes
            },
            'raw': task
        }
        self.print_json(output)
        pass

    def v2_on_file_diff(self, result):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_on_file_diff(result)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    def v2_runner_item_on_ok(self, result):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_item_on_ok(result)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    def v2_runner_item_on_failed(self, result):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_item_on_failed(result)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    def v2_runner_item_on_skipped(self, result):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_item_on_skipped(result)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    def v2_playbook_on_include(self, included_file):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_include(included_file)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    def v2_playbook_on_start(self, playbook):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_playbook_on_start(playbook)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass

    def v2_runner_retry(self, result):
        # run super and capture stdout/stderr
        with CapturingStdout() as stdout_lines:
            with CapturingStderr() as stderr_lines:
                self.super_ref.v2_runner_retry(result)

        # print stdout/stderr as wrapped up single line json documents
        self.print_str_lines(stdout_lines, 'stdout')
        self.print_str_lines(stderr_lines, 'stderr')

        # build up and print custom single line json of hook structured information
        pass




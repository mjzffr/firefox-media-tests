#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""run_media_tests.py
    Assumptions:
    - This script is run from directory ("Jenkins workspace") that contains
      clone of firefox-media-tests repo, including submodule(s).
    - (Is the Jenkins workspace clobbered?)

    Requires:
    - virtualenv, pip
    - Environment variables:
        - MOZHARNESSHOME: path to mozharness source dir
        - MINIDUMP_STACKWALK: path to minidump_stackwalk binary
    - On Windows, the mozilla-build system

"""
import copy
import os
import sys

mozharnesspath = os.environ.get('MOZHARNESSHOME')
if mozharnesspath:
    sys.path.insert(1, mozharnesspath)
else:
    print 'MOZHARNESSHOME not set'

from mozharness.base.script import BaseScript
from mozharness.mozilla.testing.testbase import (TestingMixin,
                                                 testing_config_options)
from mozharness.mozilla.testing.unittest import TestSummaryOutputParserHelper


class FirefoxMediaTest(TestingMixin, BaseScript):
    config_options = [
        [["--symbols-url"],
         {"action": "store",
          "dest": "symbols_url",
          "default": None,
          "help": "URL to the crashreporter-symbols.zip",
          }],
        [["--media-urls"],
         {"action": "store",
          "dest": "media_urls",
          "default": None,
          "help": "Path to ini file that lists media urls for tests.",
          }],
        [["--profile"],
         {"action": "store",
          "dest": "profile",
          "default": None,
          "help": "Path to FF profile that should be used by Marionette",
          }],
        [["--test-timeout"],
         {"action": "store",
          "dest": "test_timeout",
          "default": 10000,
          "help": ("Number of seconds without output before"
                    "firefox-media-tests is killed."
                    "Set this based on expected time for all media to play."),
          }],
        [["--tests"],
         {"action": "store",
          "dest": "tests",
          "default": None,
          "help": ("Test(s) to run. Path to test_*.py or "
                   "test manifest (*.ini)"),
          }],
    ] + copy.deepcopy(testing_config_options)

    marionette_status = 0

    def __init__(self, require_config_file=False):
        super(FirefoxMediaTest, self).__init__(
              config_options=self.config_options,
              all_actions=['clobber',
                           'download-and-extract',
                           'create-virtualenv',
                           'install',
                           'run_marionette_tests',
                           ],
              default_actions=['clobber',
                               'download-and-extract',
                               'create-virtualenv',
                               'install',
                               'run_marionette_tests',
                               ],
              require_config_file=require_config_file,
              config={'download_symbols': True, },
        )
        # cwd is $workspace/build
        # '..' refers to parent of setup.py for firefox-media-tests
        self.register_virtualenv_module(name='firefox-ui-tests',
                                        url=os.path.join('..',
                                                         'firefox-ui-tests'),
                                        method='pip',
                                        editable='true')
        self.register_virtualenv_module(name='firefox-media-tests',
                                        url='..',
                                        method='pip',
                                        editable='true')
        c = self.config
        self.installer_url = c.get('installer_url')
        self.symbols_url = c.get('symbols_url')
        self.media_urls = c.get('media_urls')
        self.profile = c.get('profile')
        self.test_timeout = int(c.get('test_timeout'))
        self.tests = c.get('tests')

    def preflight_download_and_extract(self):
        super(FirefoxMediaTest, self).preflight_download_and_extract()
        message = ''
        if not self.symbols_url:
            message += ("symbols-url isn't set!\n"
                        "You can set this by specifying --symbols-url URL.\n")
        if message:
            self.fatal(message + "Can't run download-and-extract... exiting")

    def _query_cmd(self):
        """ Determine how to call firefox-media-tests """
        if not self.binary_path:
            self.fatal("Binary path could not be determined. "
                       "Should be set by default during 'install' action.")
        cmd = ['firefox-media-tests']
        cmd += ['--binary', self.binary_path,
                '--symbols-path', self.symbols_path]
        if self.media_urls:
            cmd += ['--urls', self.media_urls]
        if self.profile:
            cmd += ['--profile', self.profile]
        if self.tests:
            cmd.append(self.tests)
        return cmd

    def run_marionette_tests(self):
        cmd = self._query_cmd()
        parser = TestSummaryOutputParserHelper(config=self.config,
                                               log_obj=self.log_obj)
        return_code = self.run_command(cmd,
                                       output_timeout=self.test_timeout,
                                       output_parser=parser)
        failure = return_code
        if parser.passed > 0 and parser.failed == 0:
            self.info("Marionette: success")
            failure = 0
        elif parser.failed > 0:
            self.error("Marionette: test failures")
        else:
            self.error("Marionette: harness failures")

        if failure != 0:
            gecko_log = os.path.join(self.config['base_work_dir'], 'gecko.log')
            if os.access(gecko_log, os.F_OK):
                self.info('dumping gecko.log')
                self.run_command(['cat', gecko_log])
                self.rmtree(gecko_log)
            else:
                self.info('gecko.log not found')


if __name__ == '__main__':
    media_test = FirefoxMediaTest()
    media_test.run_and_exit()

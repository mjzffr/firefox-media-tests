# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

from firefox_puppeteer import manifest as puppeteer_manifest
from firefox_ui_harness import cli
from firefox_ui_harness.options import FirefoxUIOptions
from firefox_ui_harness.runners import FirefoxUITestRunner
from firefox_ui_tests import manifest_all as ui_manifest
from firefox_ui_tests import resources as ui_resources

import firefox_media_tests


class MediaTestOptions(FirefoxUIOptions):

    def __init__(self, **kwargs):
        FirefoxUIOptions.__init__(self, **kwargs)

        self.add_option('--urls',
                        dest='urls',
                        action='store',
                        help='ini file of urls to make available to all tests')

    def parse_args(self, *args, **kwargs):
        options, test_files = FirefoxUIOptions.parse_args(self,
                                                          *args, **kwargs)
        # fixme (hack?)
        if options.urls:
            if not os.path.isfile(options.urls):
                self.error('--urls must provide a path to an ini file')
            else:
                p = os.path.abspath(options.urls)
                firefox_media_tests.videos = firefox_media_tests.get_videos(p)

        # replace firefox_ui_tests with firefox_media_tests
        if set(test_files) <= {ui_manifest, puppeteer_manifest}:
            test_files = [firefox_media_tests.manifest]

        return (options, test_files)


class MediaTestRunner(FirefoxUITestRunner):
    def __init__(self, *args, **kwargs):
        FirefoxUITestRunner.__init__(self, *args, **kwargs)
        if not self.server_root or self.server_root == ui_resources:
            self.server_root = firefox_media_tests.resources


def run():
    cli(runner_class=MediaTestRunner, parser_class=MediaTestOptions)


if __name__ == '__main__':
    sys.exit(run())

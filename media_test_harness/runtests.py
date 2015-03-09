# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys

from firefox_puppeteer import manifest as puppeteer_manifest
from firefox_ui_harness.runtests import (FirefoxUIOptions, FirefoxUITestRunner,
                                         cli)
from firefox_ui_tests import manifest as ui_manifest

import firefox_media_tests


class MediaTestOptions(FirefoxUIOptions):

    def parse_args(self, *args, **kwargs):
        options, test_files = FirefoxUIOptions.parse_args(self,
                                                           *args, **kwargs)
        # replace firefox_ui_tests with firefox_media_tests
        if set(test_files) <= {ui_manifest, puppeteer_manifest}:
            test_files = [firefox_media_tests.manifest]

        return (options, test_files)


class MediaTestRunner(FirefoxUITestRunner):
    def __init__(self, *args, **kwargs):
        FirefoxUITestRunner.__init__(self, *args, **kwargs)
        if not kwargs.get('server_root'):
            kwargs['server_root'] = firefox_media_tests.resources


def run():
    cli(runner_class=MediaTestRunner, parser_class=MediaTestOptions)


if __name__ == '__main__':
    sys.exit(run())

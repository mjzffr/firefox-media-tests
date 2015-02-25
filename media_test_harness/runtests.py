# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys

from marionette.runtests import cli
from firefox_ui_harness.runtests import ReleaseTestRunner

import firefox_media_tests

from .arguments import MediaTestParser


class MediaTestRunner(ReleaseTestRunner):
    def __init__(self, *args, **kwargs):
        ReleaseTestRunner.__init__(self, *args, **kwargs)
        if not kwargs.get('server_root'):
            kwargs['server_root'] = firefox_media_tests.resources


def run():
    cli(runner_class=ReleaseTestRunner, parser_class=MediaTestParser)


if __name__ == '__main__':
    sys.exit(run())

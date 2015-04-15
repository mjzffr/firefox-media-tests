# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from firefox_ui_harness.testcase import FirefoxTestCase


class MediaTestCase(FirefoxTestCase):
    def __init__(self, *args, **kwargs):
        self.video_urls = kwargs.pop('video_urls', False)
        FirefoxTestCase.__init__(self, *args, **kwargs)

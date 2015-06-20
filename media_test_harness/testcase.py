# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from firefox_ui_harness.testcase import FirefoxTestCase
from firefox_media_tests.utils import timestamp_now
from media_utils.video_puppeteer import VideoPuppeteer as VP

class MediaTestCase(FirefoxTestCase):

    @property
    def failureException(self):
        class MediaFailureException(AssertionError):
            def __init__(self_, *args, **kwargs):
                self.save_screenshot()
                self.log_video_debug_lines()
                super(MediaFailureException, self_).__init__(*args, **kwargs)
        MediaFailureException.__name__ = AssertionError.__name__
        return MediaFailureException

    def save_screenshot(self):
        screenshot_dir = 'screenshots'
        filename = self.id().replace(' ', '-') + str(timestamp_now()) + '.png'
        path = os.path.join(screenshot_dir, filename)
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        with self.marionette.using_context('content'):
            img_data = self.marionette.screenshot()
        with open(path, 'wb') as f:
            f.write(img_data.decode('base64'))
        self.marionette.log('Screenshot saved in %s' % os.path.abspath(path))

    def log_video_debug_lines(self):
        with self.marionette.using_context('chrome'):
            debug_lines = self.marionette.execute_script(VP._debug_script)
            if debug_lines:
                self.marionette.log('\n'.join(debug_lines))

    def __init__(self, *args, **kwargs):
        self.video_urls = kwargs.pop('video_urls', False)
        FirefoxTestCase.__init__(self, *args, **kwargs)

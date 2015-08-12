# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from marionette_driver import Wait
from marionette_driver.errors import TimeoutException
from marionette.marionette_test import SkipTest

from firefox_ui_harness import FirefoxTestCase
from firefox_media_tests.utils import (timestamp_now, verbose_until)
from media_utils.video_puppeteer import (playback_done, playback_started,
                                         VideoException, VideoPuppeteer as VP)


class MediaTestCase(FirefoxTestCase):

    def __init__(self, *args, **kwargs):
        self.video_urls = kwargs.pop('video_urls', False)
        FirefoxTestCase.__init__(self, *args, **kwargs)

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

    def run_playback(self, video):
        with self.marionette.using_context('content'):
            self.logger.info(video.test_url)
            try:
                verbose_until(Wait(video, interval=video.interval,
                                   timeout=video.expected_duration * 1.3 +
                                   video.stall_wait_time),
                              video, playback_done)
            except VideoException as e:
                raise self.failureException(e)

    def check_playback_starts(self, video):
        with self.marionette.using_context('content'):
            self.logger.info(video.test_url)
            try:
                verbose_until(Wait(video, timeout=video.timeout),
                              video, playback_started)
            except TimeoutException as e:
                raise self.failureException(e)

    def skipTest(self, reason):
        """
        Skip this test.

        Skip with marionette.marionette_test import SkipTest so that it
        gets recognized a skip in marionette.marionette_test.CommonTestCase.run
        """
        raise SkipTest(reason)

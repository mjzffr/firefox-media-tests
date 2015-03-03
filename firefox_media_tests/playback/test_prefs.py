# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from firefox_ui_harness.testcase import FirefoxTestCase
from marionette import Wait

from firefox_media_tests import videos
from media_utils.media_player import YouTubePuppeteer


class TestVideoPlayback(FirefoxTestCase):
    def setUp(self):
        FirefoxTestCase.setUp(self)
        self.test_urls = videos[:2]

    def tearDown(self):
        FirefoxTestCase.tearDown(self)

    def test_mse_is_enabled_by_default(self):
        with self.marionette.using_context('content'):
            youtube = YouTubePuppeteer(self.marionette, self.test_urls[1])
            wait = Wait(youtube.video, timeout=10, interval=2)
            wait.until(lambda v: v.get_attribute('src').startswith('mediasource'))

    def test_mse_prefs(self):
        """ 'mediasource' should only be used if MSE prefs are enabled."""
        self.set_mse_enabled_prefs(False)
        with self.marionette.using_context('content'):
            youtube = YouTubePuppeteer(self.marionette, self.test_urls[0])
            wait = Wait(youtube.video, timeout=10, interval=2)
            wait.until(lambda v: v.get_attribute('src').startswith('http'))

        self.set_mse_enabled_prefs(True)
        with self.marionette.using_context('content'):
            youtube = YouTubePuppeteer(self.marionette, self.test_urls[0])
            wait = Wait(youtube.video, timeout=10, interval=2)
            wait.until(lambda v: v.get_attribute('src').startswith('mediasource'))

    def set_mse_enabled_prefs(self, value):
        with self.marionette.using_context('chrome'):
            self.prefs.set_pref('media.mediasource.enabled', value)
            self.prefs.set_pref('media.mediasource.mp4.enabled', value)
            self.prefs.set_pref('media.mediasource.webm.enabled', value)

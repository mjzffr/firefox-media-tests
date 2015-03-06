# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from firefox_ui_harness.testcase import FirefoxTestCase
from marionette import Wait

from firefox_media_tests import videos
from firefox_media_tests.utils import verbose_until
from media_utils.media_player import YouTubePuppeteer


class TestVideoPlayback(FirefoxTestCase):
    def setUp(self):
        FirefoxTestCase.setUp(self)
        self.test_urls = videos[:2]
        self.max_timeout = 60

    def tearDown(self):
        FirefoxTestCase.tearDown(self)

    def test_mse_is_enabled_by_default(self):
        self.check_src('mediasource', self.test_urls[1])

    def test_mse_prefs(self):
        """ 'mediasource' should only be used if MSE prefs are enabled."""
        self.set_mse_enabled_prefs(False)
        self.check_src('http', self.test_urls[0])

        self.set_mse_enabled_prefs(True)
        self.check_src('mediasource', self.test_urls[0])

    def set_mse_enabled_prefs(self, value):
        with self.marionette.using_context('chrome'):
            self.prefs.set_pref('media.mediasource.enabled', value)
            self.prefs.set_pref('media.mediasource.mp4.enabled', value)
            self.prefs.set_pref('media.mediasource.webm.enabled', value)

    def check_src(self, src_type, url):
        # Why wait to check src until initial ad is done playing?
        # - src attribute in video element is sometimes null during ad playback
        # - many ads still don't use MSE even if main video does
        with self.marionette.using_context('content'):
            youtube = YouTubePuppeteer(self.marionette, url)
            youtube.attempt_ad_skip()
            wait = Wait(youtube,
                        timeout=min(self.max_timeout, youtube.player_duration))

            def cond(y):
                return y.video_src.startswith(src_type)

            verbose_until(wait, youtube, cond)

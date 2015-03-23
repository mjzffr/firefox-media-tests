# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from firefox_ui_harness.testcase import FirefoxTestCase
from marionette_driver import Wait

from firefox_media_tests import videos
from firefox_media_tests.utils import (playback_done, playback_started,
                                       verbose_until, wait_for_ads)
from media_utils.media_player import YouTubePuppeteer


class TestVideoPlayback(FirefoxTestCase):

    def setUp(self):
        FirefoxTestCase.setUp(self)
        self.test_urls = videos

    def tearDown(self):
        FirefoxTestCase.tearDown(self)

    def test_video_playing_in_one_tab(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                wait_for_ads(youtube)
                verbose_until(Wait(youtube,
                                   timeout=youtube.player_duration * 1.3),
                              youtube,
                              playback_done)

    def test_playback_starts(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                # TODO getting timeout on nightly sometimes.
                verbose_until(Wait(youtube, timeout=30), youtube,
                              playback_started)

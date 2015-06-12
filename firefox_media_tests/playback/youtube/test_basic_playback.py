# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from media_test_harness.testcase import MediaTestCase
from marionette_driver import Wait

from firefox_media_tests.utils import verbose_until
from media_utils.youtube_puppeteer import (YouTubePuppeteer, playback_done,
                                           playback_started,
                                           wait_for_almost_done)


class TestBasicYouTubePlayback(MediaTestCase):

    def setUp(self):
        MediaTestCase.setUp(self)
        self.test_urls = self.video_urls

    def tearDown(self):
        MediaTestCase.tearDown(self)

    def test_mse_is_enabled_by_default(self):
        # Why wait to check src until initial ad is done playing?
        # - src attribute in video element is sometimes null during ad playback
        # - many ads still don't use MSE even if main video does
        with self.marionette.using_context('content'):
            youtube = YouTubePuppeteer(self.marionette, self.test_urls[0])
            youtube.attempt_ad_skip()
            wait = Wait(youtube,
                        timeout=min(300, youtube.player_duration * 1.3),
                        interval=1)
            verbose_until(wait, youtube,
                          lambda y: y.video_src.startswith('mediasource'))

    def test_video_playing_in_one_tab(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                youtube.deactivate_autoplay()
                wait_for_almost_done(youtube, final_piece=60)
                self.marionette.log('Almost done: '
                                    '%s - %s seconds left.' %
                                    (youtube.movie_id,
                                     youtube.player_remaining_time))
                verbose_until(Wait(youtube, timeout=300), youtube,
                              playback_done)

    def test_playback_starts(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                verbose_until(Wait(youtube, timeout=60, interval=1), youtube,
                              playback_started)

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette_driver import Wait
from marionette_driver.errors import TimeoutException

from firefox_media_tests.utils import verbose_until
from media_test_harness.testcase import MediaTestCase
from media_utils.video_puppeteer import VideoException
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
            try:
                verbose_until(wait, youtube,
                              lambda y: y.video_src.startswith('mediasource'))
            except TimeoutException as e:
                raise self.failureException(e)

    def test_video_playing_in_one_tab(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                youtube.deactivate_autoplay()
                try:
                    wait_for_almost_done(youtube, final_piece=60)
                except VideoException as e:
                    raise self.failureException(e)
                time_left = youtube.player_remaining_time
                if time_left != 0:
                    self.marionette.log('Almost done: '
                                        '%s - %s seconds left.' %
                                        (youtube.movie_id,
                                         time_left))
                else:
                    self.marionette.log('Duration is 0 - %s' % youtube,
                                        level='WARNING')
                    self.save_screenshot()
                try:
                    verbose_until(Wait(youtube,
                                       timeout=time_left * 1.3,
                                       interval=1),
                                  youtube,
                                  playback_done)
                except TimeoutException as e:
                    raise self.failureException(e)

    def test_playback_starts(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                try:
                    verbose_until(Wait(youtube, timeout=60, interval=1),
                                  youtube, playback_started)
                except TimeoutException as e:
                    raise self.failureException(e)

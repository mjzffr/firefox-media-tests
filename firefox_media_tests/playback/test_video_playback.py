# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from marionette_driver import Wait
from marionette_driver.errors import TimeoutException

from firefox_media_tests.utils import verbose_until
from media_test_harness.testcase import MediaTestCase
from media_utils.video_puppeteer import (playback_done, playback_started,
                                         VideoPuppeteer, VideoException)


class TestVideoPlaybackBase(MediaTestCase):
    """ Test MSE playback in HTML5 video element.

    These tests should pass on any site where a single video element plays
    upon loading and is uninterrupted (by ads, for example)
    """
    def setUp(self):
        MediaTestCase.setUp(self)
        self.test_urls = self.video_urls

    def tearDown(self):
        MediaTestCase.tearDown(self)

    def test_playback_starts(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                video = VideoPuppeteer(self.marionette, url)
                try:
                    verbose_until(Wait(video, timeout=30), video,
                                  playback_started)
                except TimeoutException as e:
                    raise self.failureException(e)
                video.pause()
                src = video.video_src
                if not src.startswith('mediasource'):
                    self.marionette.log('video is not mediasource: %s' % src,
                                        level='WARNING')

    def test_video_playback_partial(self):
        self.run_playback(timeout=120)

    def test_video_playback_full(self):
        self.run_playback()

    def run_playback(self, timeout=0):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                video = VideoPuppeteer(self.marionette, url)
                # Some vendors don't start the videos at the beginning,
                # remembering where you were last time you watched.
                start_time = video.current_time
                verbose_until(Wait(video, timeout=30), video,
                              playback_started)
                duration_timeout = video.duration * 1.3
                time_delta = 2
                if timeout <= 0:
                    duration = duration_timeout
                else:
                    # Looser constraint for partial playback
                    time_delta = 5
                    duration = min(timeout, duration_timeout)

                try:
                    verbose_until(Wait(video, interval=1, timeout=duration),
                                  video, playback_done)
                except TimeoutException:
                    # We want to make sure that the current time is near the
                    # duration we want, especially when testing partial
                    # playback
                    self.assertAlmostEqual(video.current_time,
                                           start_time + duration,
                                           delta=time_delta)
                except VideoException as e:
                    raise self.failureException(e)

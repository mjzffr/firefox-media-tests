# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from marionette_driver.errors import TimeoutException
from marionette_driver import Wait

from firefox_media_tests.utils import (verbose_until)
from media_test_harness.testcase import MediaTestCase
from media_utils.video_puppeteer import (playback_done, playback_started,
                                         VideoPuppeteer, VideoException)


class TestVideoPlaybackBase(MediaTestCase):

    def setUp(self):
        MediaTestCase.setUp(self)
        self.test_urls = self.video_urls

    def tearDown(self):
        MediaTestCase.tearDown(self)

    def test_playback_starts(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                video = VideoPuppeteer(self.marionette, url)
                verbose_until(Wait(video, timeout=30), video,
                              playback_started)
                video.pause()

    def test_video_playback_partial(self):
        self.run_playback(timeout=120)

    def test_video_playback_full(self):
        self.run_playback()

    def run_playback(self, timeout=0):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                video = VideoPuppeteer(self.marionette, url)
                verbose_until(Wait(video, timeout=30), video,
                              playback_started)
                duration_timeout = video.duration * 1.3
                if timeout <= 0:
                    duration = duration_timeout
                else:
                    duration = min(timeout, duration_timeout)

                try:
                    # Some vendors don't start the videos at the beginning,
                    # remembering where you were last time you watched.
                    start_time = video.current_time
                    verbose_until(Wait(video, interval=1, timeout=duration),
                                  video, playback_done)
                except VideoException as e:
                    raise self.failureException(e)

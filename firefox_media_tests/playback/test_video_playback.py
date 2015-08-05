# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from marionette_driver import Wait
from marionette_driver.errors import TimeoutException

from firefox_media_tests.utils import verbose_until
from media_test_harness.testcase import MediaTestCase
from media_utils.video_puppeteer import (playback_started, VideoPuppeteer)


class TestVideoPlayback(MediaTestCase):
    """ Test MSE playback in HTML5 video element.

    These tests should pass on any site where a single video element plays
    upon loading and is uninterrupted (by ads, for example)
    """

    def test_playback_starts(self):
        with self.marionette.using_context('content'):
            for url in self.video_urls:
                self.logger.info(url)
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
        self.run_playback(set_duration=60)

    def test_video_playback_full(self):
        self.run_playback()

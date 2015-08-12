# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette_driver.errors import TimeoutException

from media_test_harness.testcase import MediaTestCase
from media_utils.video_puppeteer import VideoPuppeteer


class TestVideoPlayback(MediaTestCase):
    """ Test MSE playback in HTML5 video element.

    These tests should pass on any site where a single video element plays
    upon loading and is uninterrupted (by ads, for example).

    This test both starting videos and performing partial playback at one
    minute each, and is the test that should be run frequently in automation.
    """

    def test_playback_starts(self):
        with self.marionette.using_context('content'):
            for url in self.video_urls:
                try:
                    video = VideoPuppeteer(self.marionette, url, timeout=60)
                    # Second playback_started check in case video._start_time
                    # is not 0
                    self.check_playback_starts(video)
                    video.pause()
                    src = video.video_src
                    if not src.startswith('mediasource'):
                        self.marionette.log('video is not '
                                            'mediasource: %s' % src,
                                            level='WARNING')
                except TimeoutException as e:
                    raise self.failureException(e)

    def test_video_playback_partial(self):
        """ First 60 seconds of video play well. """
        with self.marionette.using_context('content'):
            for url in self.video_urls:
                video = VideoPuppeteer(self.marionette, url,
                                       stall_wait_time=10,
                                       set_duration=60)
                self.run_playback(video)

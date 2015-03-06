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
        self.test_urls = videos

    def tearDown(self):
        FirefoxTestCase.tearDown(self)

    def test_video_playing_in_one_tab(self):
        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                # skip first ad if possible or wait until ad completes playback
                youtube.attempt_ad_skip()
                verbose_until(Wait(youtube, timeout=360), youtube,
                              lambda yt: yt.ad_inactive)

                # TODO find way to deal with buffering delays
                # add 60s extra timeout room per expected ad break
                timeout = (int(youtube.player_duration) +
                           60 * (youtube.breaks_count + 1))
                verbose_until(Wait(youtube, timeout=timeout), youtube,
                              lambda yt: yt.player_ended)

    def test_playback_starts(self):
        def playback_ok(yt):
            # usually, ad is playing during initial buffering
            return yt.player_state in [yt._yt_player_state['PLAYING'],
                                       yt._yt_player_state['BUFFERING']]

        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                # TODO getting timeout on nightly sometimes.
                verbose_until(Wait(youtube, timeout=30), youtube, playback_ok)

    def test_videos_playing_in_many_tabs(self):
        pass

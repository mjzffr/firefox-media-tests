# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from sys import exc_info

from firefox_ui_harness.testcase import FirefoxTestCase
from marionette import errors, Wait

from firefox_media_tests import videos
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
                # TODO try to click through to non-ad?
                # TODO this only handles ad playing at start
                Wait(youtube, timeout=360).until(lambda yt: yt.ad_inactive)
                # TODO better way to deal with buffering delays?
                timeout = (int(youtube.player_duration) +
                           30 * (youtube.breaks_count + 1))
                wait = Wait(youtube, timeout=timeout)
                try:
                    wait.until(lambda yt: yt.player_ended)
                except errors.TimeoutException as e:
                    message = '\n'.join([e.msg, str(youtube)])
                    raise errors.TimeoutException(message=message,
                                                  cause=exc_info())

    def test_playback_starts(self):
        def playback_ok(yt):
            # usually, ad is playing during initial buffering
            return yt.player_state in [yt._yt_player_state['PLAYING'],
                                       yt._yt_player_state['BUFFERING']]

        with self.marionette.using_context('content'):
            for url in self.test_urls:
                youtube = YouTubePuppeteer(self.marionette, url)
                Wait(youtube, interval=5, timeout=30).until(playback_ok)

    def test_videos_playing_in_many_tabs(self):
        pass

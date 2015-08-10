# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from media_test_harness.testcase import MediaTestCase


class TestFullPlayback(MediaTestCase):
    """ Test MSE playback in HTML5 video element.

    These tests should pass on any site where a single video element plays
    upon loading and is uninterrupted (by ads, for example). This will play
    the full videos, so it could take a while depending on the videos playing.
    It should be run much less frequently in automated systems.
    """

    def test_video_playback_full(self):
        self.run_playback()

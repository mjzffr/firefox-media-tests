# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette import BrowserMobProxyTestCaseMixin

from media_utils.video_puppeteer import VideoPuppeteer
from media_test_harness.testcase import MediaTestCase


class TestPlaybackLimitingBandwidth(MediaTestCase,
                                    BrowserMobProxyTestCaseMixin):

    def __init__(self, *args, **kwargs):
        MediaTestCase.__init__(self, *args, **kwargs)
        BrowserMobProxyTestCaseMixin.__init__(self, *args, **kwargs)
        self.proxy = None

    def setUp(self):
        MediaTestCase.setUp(self)
        BrowserMobProxyTestCaseMixin.setUp(self)
        self.proxy = self.create_browsermob_proxy()

    def tearDown(self):
        MediaTestCase.tearDown(self)
        BrowserMobProxyTestCaseMixin.tearDown(self)
        self.proxy = None

    def run_videos(self):
        with self.marionette.using_context('content'):
            for url in self.video_urls:
                video = VideoPuppeteer(self.marionette, url,
                                       stall_wait_time=10,
                                       set_duration=60)
                self.run_playback(video)

    def test_playback_limiting_bandwidth_160(self):
        self.proxy.limits({'downstream_kbps': 160})
        self.run_videos()

    def test_playback_limiting_bandwidth_250(self):
        self.proxy.limits({'downstream_kbps': 250})
        self.run_videos()

    def test_playback_limiting_bandwidth_500(self):
        self.proxy.limits({'downstream_kbps': 500})
        self.run_videos()

    def test_playback_limiting_bandwidth_1000(self):
        self.proxy.limits({'downstream_kbps': 1000})
        self.run_videos()

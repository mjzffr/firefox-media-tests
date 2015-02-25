# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from time import sleep

from firefox_ui_harness.testcase import FirefoxTestCase
from firefox_media_tests import videos


class TestVideoPlayback(FirefoxTestCase):
    '''
    TODO
    -get the video element
    -from that can get duration and whether it's ended and current time
    -use Wait, with timeout equal to duration?
    '''

    def setUp(self):
        FirefoxTestCase.setUp(self)
        self.prefs.set_pref('media.mediasource.enabled', 'true')
        self.test_urls = videos

    def tearDown(self):
        FirefoxTestCase.tearDown(self)

    def test_access_locationbar_history(self):
        # Open all the videos one after the other in current tab
        def load_urls():
            with self.marionette.using_context('content'):
                for url in self.test_urls:
                    self.marionette.navigate(url)
                    sleep(4)
        self.places.wait_for_visited(self.test_urls, load_urls)

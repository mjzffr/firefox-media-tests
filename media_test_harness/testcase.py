# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from firefox_ui_harness.testcase import FirefoxTestCase

class MediaTestCase(FirefoxTestCase):

    @property
    def failureException(self):
        class MediaFailureException(AssertionError):
            def __init__(self_, *args, **kwargs):
                self.save_screenshot()
                super(MediaFailureException, self_).__init__(*args, **kwargs)
        MediaFailureException.__name__ = AssertionError.__name__
        return MediaFailureException

    def save_screenshot(self):
        screenshot_dir = 'screenshots'
        path = os.path.join(screenshot_dir,
                            self.id().replace(' ', '-') + '.png')
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        with self.marionette.using_context('content'):
            img_data = self.marionette.screenshot()
        with open(path, 'wb') as f:
            f.write(img_data.decode('base64'))
        self.marionette.log('Screenshot saved in %s' % os.path.abspath(path))

    def __init__(self, *args, **kwargs):
        self.video_urls = kwargs.pop('video_urls', False)
        FirefoxTestCase.__init__(self, *args, **kwargs)

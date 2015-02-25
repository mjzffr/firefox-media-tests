# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from firefox_ui_harness.arguments import ReleaseTestParser
from firefox_ui_tests import manifest as ui_manifest
from firefox_puppeteer import manifest as puppeteer_manifest

import firefox_media_tests


class MediaTestParser(ReleaseTestParser):

    def parse_args(self, *args, **kwargs):
        options, test_files = ReleaseTestParser.parse_args(self,
                                                           *args, **kwargs)
        # replace firefox_ui_tests with firefox_media_tests
        if set(test_files) <= {ui_manifest, puppeteer_manifest}:
            test_files = [firefox_media_tests.manifest]

        return (options, test_files)

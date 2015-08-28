# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from manifestparser import read_ini
from marionette.runner import BrowserMobProxyOptionsMixin
import os
import sys

from marionette import BaseMarionetteTestRunner, BaseMarionetteOptions
from marionette.marionette_test import MarionetteTestCase
import mozlog

import firefox_media_tests
from testcase import MediaTestCase
from media_utils.video_puppeteer import debug_script

DEFAULT_PREFS = {
    'app.update.auto': False,
    'app.update.enabled': False,
    'browser.dom.window.dump.enabled': True,
    # Bug 1145668 - Has to be reverted to about:blank once Marionette
    # can correctly handle error pages
    'browser.newtab.url': 'about:newtab',
    'browser.newtabpage.enabled': False,
    'browser.reader.detectedFirstArticle': True,
    'browser.safebrowsing.enabled': False,
    'browser.safebrowsing.malware.enabled': False,
    'browser.search.update': False,
    'browser.sessionstore.resume_from_crash': False,
    'browser.shell.checkDefaultBrowser': False,
    'browser.startup.page': 0,
    'browser.tabs.animate': False,
    'browser.tabs.warnOnClose': False,
    'browser.tabs.warnOnOpen': False,
    'browser.uitour.enabled': False,
    'browser.warnOnQuit': False,
    'datareporting.healthreport.service.enabled': False,
    'datareporting.healthreport.uploadEnabled': False,
    'datareporting.healthreport.documentServerURI': "http://%(server)s/healthreport/",
    'datareporting.healthreport.about.reportUrl': "http://%(server)s/abouthealthreport/",
    'datareporting.policy.dataSubmissionEnabled': False,
    'datareporting.policy.dataSubmissionPolicyAccepted': False,
    'dom.ipc.reportProcessHangs': False,
    'dom.report_all_js_exceptions': True,
    'extensions.enabledScopes': 5,
    'extensions.autoDisableScopes': 10,
    'extensions.getAddons.cache.enabled': False,
    'extensions.installDistroAddons': False,
    'extensions.logging.enabled': True,
    'extensions.showMismatchUI': False,
    'extensions.update.enabled': False,
    'extensions.update.notifyUser': False,
    'focusmanager.testmode': True,
    'geo.provider.testing': True,
    'javascript.options.showInConsole': True,
    'marionette.logging': False,
    'security.notification_enable_delay': 0,
    'signon.rememberSignons': False,
    'startup.homepage_welcome_url': 'about:blank',
    'toolkit.startup.max_resumed_crashes': -1,
    'toolkit.telemetry.enabled': False,
}


class MediaTestOptions(BaseMarionetteOptions,
                       BrowserMobProxyOptionsMixin):

    def __init__(self, **kwargs):
        BaseMarionetteOptions.__init__(self, **kwargs)
        BrowserMobProxyOptionsMixin.__init__(self, **kwargs)

        self.add_option('--urls',
                        dest='urls',
                        action='store',
                        help='ini file of urls to make available to all tests')

    def parse_args(self, *args, **kwargs):
        options, tests = BaseMarionetteOptions.parse_args(self, *args,
                                                          **kwargs)

        if options.urls:
            if not os.path.isfile(options.urls):
                self.error('--urls must provide a path to an ini file')
            else:
                path = os.path.abspath(options.urls)
                options.video_urls = MediaTestOptions.get_urls(path)
        else:
            default = os.path.join(firefox_media_tests.urls, 'default.ini')
            options.video_urls = self.get_urls(default)

        tests = tests or [firefox_media_tests.manifest]

        return options, tests

    @staticmethod
    def get_urls(manifest):
        with open(manifest, 'r'):
            return [line[0] for line in read_ini(manifest)]


class MediaTestRunner(BaseMarionetteTestRunner):
    def __init__(self, **kwargs):
        BaseMarionetteTestRunner.__init__(self, **kwargs)
        if not self.server_root:
            self.server_root = firefox_media_tests.resources
        self.prefs.update(DEFAULT_PREFS)
        self.test_handlers = [MediaTestCase]

        # Used in HTML report (--log-html)
        def gather_media_debug(test, status):
            rv = {}
            marionette = test._marionette_weakref()

            if marionette.session is not None:
                try:
                    with marionette.using_context(marionette.CONTEXT_CHROME):
                        debug_lines = marionette.execute_script(debug_script)
                        if debug_lines:
                            name = 'mozMediaSourceObject.mozDebugReaderData'
                            rv[name] = '\n'.join(debug_lines)
                except:
                    logger = mozlog.get_default_logger()
                    logger.warning('Failed to gather test failure media debug',
                                   exc_info=True)
            return rv

        self.result_callbacks.append(gather_media_debug)


def startTestRunner(runner_class, options, tests):
    if options.pydebugger:
        MarionetteTestCase.pydebugger = __import__(options.pydebugger)

    runner = runner_class(**vars(options))
    runner.run_tests(tests)
    return runner


def cli(runner_class=MediaTestRunner, parser_class=MediaTestOptions):
    parser = parser_class(usage=('%prog [options] test_file_or_dir '
                                 '<test_file_or_dir> ...'))
    mozlog.commandline.add_logging_group(parser)
    options, tests = parser.parse_args()

    parser.verify_usage(options, tests)

    logger = mozlog.commandline.setup_logging(
        options.logger_name, options, {'mach': sys.stdout})

    options.logger = logger
    try:
        runner = startTestRunner(runner_class, options, tests)
        if runner.failed > 0:
            sys.exit(10)

    except Exception:
        logger.error('Failure during execution of the playback test.',
                     exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(cli())

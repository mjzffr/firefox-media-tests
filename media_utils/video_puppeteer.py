# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re
from time import sleep

from marionette_driver import (By, expected, Wait)
from marionette_driver.errors import TimeoutException

from firefox_media_tests.utils import (verbose_until)

# Adapted from https://github.com/gavinsharp/aboutmedia/blob/master/chrome/content/aboutmedia.xhtml
_debug_script = """
var mainWindow = window.QueryInterface(Components.interfaces.nsIInterfaceRequestor)
    .getInterface(Components.interfaces.nsIWebNavigation)
    .QueryInterface(Components.interfaces.nsIDocShellTreeItem)
    .rootTreeItem
    .QueryInterface(Components.interfaces.nsIInterfaceRequestor)
    .getInterface(Components.interfaces.nsIDOMWindow);
var tabbrowser = mainWindow.gBrowser;
for (var i=0; i < tabbrowser.browsers.length; ++i) {
  var b = tabbrowser.getBrowserAtIndex(i);
  var media = b.contentDocumentAsCPOW.getElementsByTagName('video');
  for (var j=0; j < media.length; ++j) {
     var ms = media[j].mozMediaSourceObject;
     if (ms) {
       debugLines = ms.mozDebugReaderData.split(\"\\n\");
       return debugLines;
     }
  }
}"""


def playback_started(video):
    try:
        return video.current_time > 0
    except Exception as e:
        print ('Got exception %s' % e)
        return False


class VideoException(Exception):
    pass

# Debug info looks something like:
# Dumping data for reader d10c000:
#  Dumping Audio Track Decoders: - mLastAudioTime: 9.386666
#   Reader 0: d2df400 ranges=[(0.000000, 16.042666)] active=true size=196456
#  Dumping Video Track Decoders - mLastVideoTime: 8.466791
#	 Reader 2: 13f54400 ranges=[(8.008000, 16.016000)] active=true size=3741917
#	 Reader 1: d2edc00 ranges=[(4.004000, 8.008000)] active=false size=1088692
#	 Reader 0: d2eac00 ranges=[(2.002000, 4.004000)] active=false size=242367

# One simple hack: There should be two active readers at any one time. If
# there are not exactly two, something is horribly wrong.

active_re = re.compile('active=true', re.DOTALL)

def playback_done(video):

    # If we are near the end and there is still a video element, then
    # we are essentially done. Any further progress might set on of
    # the stream active state to false, and we will raise in that
    # case inappropriately.

    if abs(video.remaining_time) < 2.0:
        return True

    # Now, parse out playing info. If there is no debug info, then the
    # video element has disappeared somehow, and that' a problem.
    # Otherwise, there should be one active video and one active audio
    # stream. If not, there is a problem. Past this point, the video is
    # either still playing or there is a problem, so this will never
    # return True.

    debug_lines = video.get_debug_lines()
    if debug_lines is not None:
        num_active = len(active_re.findall(' '.join(debug_lines)))
        if num_active == 2:
            return False

    raise VideoException('Did not find exactly one audio and one video '
                         'active reader - %s'
                         % video)

class VideoPuppeteer:
    """
    Wrapper around an video media-player element
    """

    def __init__(self, marionette, url):
        self.marionette = marionette
        self.url = url
        wait = Wait(self.marionette, timeout=30)
        with self.marionette.using_context('content'):
            self.marionette.navigate(self.url)
            self.video = None
            verbose_until(wait, self, expected.element_present(By.TAG_NAME, 'video'))
            self.video = self.marionette.find_element(By.TAG_NAME, 'video')

    def get_debug_lines(self):
        with self.marionette.using_context('chrome'):
            debug_lines = self.marionette.execute_script(_debug_script)
        return debug_lines

    def play(self):
        self.execute_video_script('arguments[0].wrappedJSObject.play()')

    def pause(self):
        self.execute_video_script('arguments[0].wrappedJSObject.pause()')

    @property
    def duration(self):
        """ Return duration in seconds. """
        if not self.video:
            return ("NA")

        duration = self.execute_video_script('return arguments[0].'
                                             'wrappedJSObject.duration;')
        return duration

    @property
    def current_time(self):
        if not self.video:
            return ("NA")

        state = self.execute_video_script('return arguments[0].'
                                          'wrappedJSObject.currentTime;')
        return state

    @property
    def remaining_time(self):
        return self.duration - self.current_time

    def progress(self):
        initial = self.current_time
        sleep(1)
        return self.current_time - initial

    def execute_video_script(self, script):
        with self.marionette.using_context('content'):
            return self.marionette.execute_script(script,
                                                  script_args=[self.video])

    def __str__(self):
        messages = ['VideoPuppeteer %s: {' % self.url,
                    '\tcurrent_time: {0},'.format(self.current_time),
                    '\tduration: {0},'.format(self.duration),
                    '}']
        return '\n'.join(messages)

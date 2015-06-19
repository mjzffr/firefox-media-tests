# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re
from time import sleep

from marionette_driver import By, expected, Wait

from firefox_media_tests.utils import verbose_until


class VideoPuppeteer(object):
    """
    Wrapper around HTML5 video element
    """

    # Adapted from
    # https://github.com/gavinsharp/aboutmedia/blob/master/chrome/content/aboutmedia.xhtml
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

    def __init__(self, marionette, url, video_selector='video'):
        self.marionette = marionette
        self.test_url = url
        wait = Wait(self.marionette, timeout=30)
        with self.marionette.using_context('content'):
            self.marionette.navigate(self.test_url)
            self.video = None
            verbose_until(wait, self,
                          expected.element_present(By.TAG_NAME, 'video'))
            videos_found = self.marionette.find_elements(By.CSS_SELECTOR,
                                                         video_selector)
            if len(videos_found) > 1:
                self.marionette.log(type(self).__name__ + ': multiple video '
                                                          'elements found. '
                                                          'Using first.')
            if len(videos_found) > 0:
                self.video = videos_found[0]
                self.marionette.execute_script("""
                    log('URL:{} - video element obtained');
                """.format(self.test_url))

    def get_debug_lines(self):
        with self.marionette.using_context('chrome'):
            debug_lines = self.marionette.execute_script(self._debug_script)
        return debug_lines

    def play(self):
        self.execute_video_script('arguments[0].wrappedJSObject.play();')

    def pause(self):
        self.execute_video_script('arguments[0].wrappedJSObject.pause();')

    @property
    def duration(self):
        """ Return duration in seconds. """
        return self.execute_video_script('return arguments[0].'
                                         'wrappedJSObject.duration;') or 0

    @property
    def current_time(self):
        return self.execute_video_script('return arguments[0].'
                                         'wrappedJSObject.currentTime;') or 0

    @property
    def remaining_time(self):
        return self.duration - self.current_time

    @property
    def video_src(self):
        with self.marionette.using_context('content'):
            return self.video.get_attribute('src')

    @property
    def total_frames(self):
        return self.execute_video_script("""
            return arguments[0].getVideoPlaybackQuality()["totalVideoFrames"];
            """)

    @property
    def dropped_frames(self):
        return self.execute_video_script("""return
            arguments[0].getVideoPlaybackQuality()["droppedVideoFrames"];
            """)

    @property
    def corrupted_frames(self):
        return self.execute_video_script("""return
            arguments[0].getVideoPlaybackQuality()["corruptedVideoFrames"];
            """)

    @property
    def video_url(self):
        return self.execute_video_script('return arguments[0].baseURI;')

    def measure_progress(self):
        initial = self.current_time
        sleep(1)
        return self.current_time - initial

    def execute_video_script(self, script):
        """ Execute JS script in 'content' context with access to video element.
        :param script: script to be executed
        `arguments[0]` in script refers to video element.
        :return: value returned by script
        """
        with self.marionette.using_context('content'):
            return self.marionette.execute_script(script,
                                                  script_args=[self.video])

    def __str__(self):
        messages = ['%s - test url: %s: {' % (type(self).__name__,
                                              self.test_url)]
        if self.video:
            messages += ['\t(video)',
                         '\tcurrent_time: {0},'.format(self.current_time),
                         '\tduration: {0},'.format(self.duration),
                         '\turl: {0}'.format(self.video_url),
                         '\tsrc: {0}'.format(self.video_src),
                         '\tframes total: {0}'.format(self.total_frames),
                         '\t - dropped: {0}'.format(self.dropped_frames),
                         '\t - corrupted: {0}'.format(self.corrupted_frames)]
        else:
            messages += ['\tvideo: None']
        messages.append('}')
        return '\n'.join(messages)


class VideoException(Exception):
    pass


def playback_started(video):
    try:
        return video.current_time > 0
    except Exception as e:
        print ('Got exception %s' % e)
        return False

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


def playback_done(video):
    active_re = re.compile('active=true', re.DOTALL)

    # If we are near the end and there is still a video element, then
    # we are essentially done. Any further progress might set on of
    # the stream active state to false, and we will raise in that
    # case inappropriately.

    if abs(video.remaining_time) < 2.0:
        return True

    # Now, parse out playing info. If there is no debug info, then the
    # video element has disappeared somehow, and that' a problem.
    # Otherwise, there should be one active video and one active audio
    # stream. (TODO: what if there are multiple tabs with video content?)
    # If not, there is a problem. Past this point, the video is
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

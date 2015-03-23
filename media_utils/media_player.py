# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from time import sleep
from re import compile

from marionette_driver import By, expected, Wait
from marionette_driver.errors import TimeoutException


class YouTubePuppeteer:
    """
    Wrapper around a YouTube media-player element

    Partial reference: https://developers.google.com/youtube/js_api_reference
    """

    _yt_player_state = {
        'UNSTARTED': -1,
        'ENDED': 0,
        'PLAYING': 1,
        'PAUSED': 2,
        'BUFFERING': 3,
        'CUED': 5
    }

    _yt_player_state_name = {v: k for k, v in _yt_player_state.items()}

    _time_pattern = compile('(?P<minute>\d+):(?P<second>\d+)')

    def __init__(self, marionette, url):
        self.marionette = marionette
        self.url = url
        wait = Wait(self.marionette, timeout=30)
        with self.marionette.using_context('content'):
            self.marionette.navigate(self.url)
            wait.until(expected.element_displayed(By.ID, 'movie_player'))
            self.player = self.marionette.find_element(By.ID, 'movie_player')

            wait.until(expected.element_displayed(By.CSS_SELECTOR,
                                                  '#movie_player video'))
            self.video = self.marionette.find_element(By.CSS_SELECTOR,
                                                      '#movie_player video')

    def attempt_ad_skip(self):
        """
        Attempts to skip ad by clicking on skip-add button.
        Returns True if clicking of ad-skip button occurred.
        """
        # Wait for ad to load and become skippable
        if (self.ad_state == self._yt_player_state['PLAYING'] or
                self.get_player_progress() == 0):
            sleep(10)
        if self.ad_skippable:
            selector = '#movie_player .videoAdUiSkipContainer'
            wait = Wait(self.marionette, timeout=30)
            with self.marionette.using_context('content'):
                wait.until(expected.element_displayed(By.CSS_SELECTOR,
                                                      selector))
                ad_button = self.marionette.find_element(By.CSS_SELECTOR,
                                                         selector)
                ad_button.click()
                return True
        else:
            return False

    def search_ad_duration(self):
        """
        :return: ad duration in seconds, if currently displayed in player
        """
        if not (self.ad_state == self._yt_player_state['PLAYING'] or
                self.get_player_progress() == 0):
            return None
        selector = '#movie_player .videoAdUiAttribution'
        wait = Wait(self.marionette, timeout=5)
        try:
            with self.marionette.using_context('content'):
                wait.until(expected.element_present(By.CSS_SELECTOR,
                                                    selector))
                countdown = self.marionette.find_element(By.CSS_SELECTOR,
                                                         selector)
                ad_time = self._time_pattern.search(countdown.text)
                if ad_time:
                    ad_minutes = int(ad_time.group('minute'))
                    ad_seconds = int(ad_time.group('second'))
                    return 60 * ad_minutes + ad_seconds
                else:
                    return None
        except TimeoutException:
            return None

    @property
    def player_duration(self):
        """ Returns duration in seconds. """
        with self.marionette.using_context('content'):
            duration = self.execute_yt_script('return arguments[0].'
                                              'wrappedJSObject.getDuration();')
        return duration

    @property
    def player_current_time(self):
        with self.marionette.using_context('content'):
            state = self.execute_yt_script('return arguments[0].'
                                           'wrappedJSObject.getCurrentTime();')
        return state

    def _get_player_debug_dict(self):
        # may return None
        with self.marionette.using_context('content'):
            text = self.execute_yt_script('return arguments[0].'
                                          'wrappedJSObject.getDebugText();')
        if text:
            return eval(text)
        else:
            return None

    @property
    def playback_quality(self):
        # may return None
        debug_dict = self._get_player_debug_dict()
        if debug_dict:
            return debug_dict['debug_playbackQuality']
        else:
            return None

    @property
    def video_id(self):
        # may return None
        debug_dict = self._get_player_debug_dict()
        if debug_dict:
            return debug_dict['debug_videoId']
        else:
            return None

    @property
    def video_url(self):
        with self.marionette.using_context('content'):
            url = self.execute_yt_script('return arguments[0].'
                                         'wrappedJSObject.getVideoUrl();')
        return url

    @property
    def video_src(self):
        with self.marionette.using_context('content'):
            return self.video.get_attribute('src')

    @property
    def player_state(self):
        with self.marionette.using_context('content'):
            state = self.execute_yt_script('return arguments[0].'
                                           'wrappedJSObject.getPlayerState();')
        return state

    @property
    def player_unstarted(self):
        return self.player_state == self._yt_player_state['UNSTARTED']

    @property
    def player_ended(self):
        return self.player_state == self._yt_player_state['ENDED']

    @property
    def player_playing(self):
        return self.player_state == self._yt_player_state['PLAYING']

    @property
    def player_paused(self):
        return self.player_state == self._yt_player_state['PAUSED']

    @property
    def player_buffering(self):
        return self.player_state == self._yt_player_state['BUFFERING']

    @property
    def player_cued(self):
        return self.player_state == self._yt_player_state['CUED']

    @property
    def ad_state(self):
        # Note: ad_state is sometimes not accurate, due to some sort of lag?
        with self.marionette.using_context('content'):
            state = self.execute_yt_script('return arguments[0].'
                                           'wrappedJSObject.getAdState();')
        return state

    @property
    def ad_format(self):
        """
        When ad is not playing, ad_format is False.

        :return: integer representing ad format, or False
        """
        state = self.get_ad_displaystate()
        if state:
            return self.marionette.execute_script('return arguments[0].'
                                                  'adFormat;',
                                                  script_args=[state])
        else:
            return False

    @property
    def ad_skippable(self):
        state = self.get_ad_displaystate()
        if state:
            return self.marionette.execute_script('return arguments[0].'
                                                  'skippable;',
                                                  script_args=[state])
        else:
            return False

    def get_ad_displaystate(self):
        # may return None
        with self.marionette.using_context('content'):
            return self.execute_yt_script('return arguments[0].'
                                          'wrappedJSObject.'
                                          'getOption("ad", "displaystate");')

    @property
    def breaks_count(self):
        """
        Number of upcoming ad breaks.
        """
        with self.marionette.using_context('content'):
            breaks = self.execute_yt_script('return arguments[0].'
                                            'wrappedJSObject.'
                                            'getOption("ad", "breakscount")')
        # if video is not associated with any ads, breaks will be null
        return breaks or 0

    @property
    def ad_inactive(self):
        # `current_time` stands still while ad is playing
        if self.player_current_time > 0 or self.player_playing:
            return (self.get_player_progress() > 0 or
                    self.ad_state == self._yt_player_state['ENDED'])
        else:
            return self.ad_state == self._yt_player_state['ENDED']

    def get_player_progress(self):
        initial = self.player_current_time
        sleep(1)
        return self.player_current_time - initial

    def execute_yt_script(self, script):
        return self.marionette.execute_script(script,
                                              script_args=[self.player,
                                                           self.video])

    def __str__(self):
        player_state = self._yt_player_state_name[self.player_state]
        ad_state = self._yt_player_state_name[self.ad_state]
        messages = ['YouTube player: {',
                    '\tcurrent_time: {0},'.format(self.player_current_time),
                    '\tduration: {0},'.format(self.player_duration),
                    '\tcurrent_state: {0},'.format(player_state),
                    '\tad_state: {0},'.format(ad_state),
                    '\tplayback_quality: {0},'.format(self.playback_quality),
                    '\tvideo_url: {0},'.format(self.video_url),
                    '\tvideo.src: {0}'.format(self.video_src),
                    '}']
        return '\n'.join(messages)

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from time import sleep
from re import compile
from json import loads

from marionette_driver import By, expected, Wait
from marionette_driver.errors import TimeoutException, NoSuchElementException
from video_puppeteer import VideoPuppeteer, VideoException
from firefox_media_tests.utils import verbose_until


class YouTubePuppeteer(VideoPuppeteer):
    """
    Wrapper around a YouTube #movie_player element

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
        super(YouTubePuppeteer,
              self).__init__(marionette, url,
                             video_selector='#movie_player video')
        wait = Wait(self.marionette, timeout=30)
        with self.marionette.using_context('content'):
            verbose_until(wait, self,
                          expected.element_present(By.ID, 'movie_player'))
            self.player = self.marionette.find_element(By.ID, 'movie_player')
            self.marionette.execute_script("log('#movie_player "
                                           "element obtained');")

    def player_play(self):
        """ Play via YouTube API. """
        self.execute_yt_script('arguments[1].wrappedJSObject.playVideo();')

    def player_pause(self):
        """ Pause via YouTube API. """
        self.execute_yt_script('arguments[1].wrappedJSObject.pauseVideo();')

    @property
    def player_duration(self):
        """ Duration in seconds via YouTube API.

        This always describes the target YouTube video. It does not necessarily
        describe the HTML video element, which may have ad playing in it.
        """
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.getDuration();')

    @property
    def player_current_time(self):
        """ Current time in seconds via YouTube API.

        This always describes the target YouTube video. It does not necessarily
        describe the HTML video element, which may have ad playing in it.
        """
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.getCurrentTime();')

    @property
    def player_remaining_time(self):
        """ Remaining time in seconds via YouTube API.

        This always describes the target YouTube video. It does not necessarily
        describe the HTML video element, which may have ad playing in it.
        """
        return self.player_duration - self.player_current_time

    def player_measure_progress(self):
        """ Playback progress in seconds via YouTube API.

        This always describes the target YouTube video. It does not necessarily
        describe the HTML video element, which may have ad playing in it.
        """
        initial = self.player_current_time
        sleep(1)
        return self.player_current_time - initial

    def _get_player_debug_dict(self):
        text = self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.getDebugText();')
        if text:
            try:
                return loads(text)
            except ValueError:
                self.marionette.log('Error loading json: DebugText',
                                    level='DEBUG')

    def execute_yt_script(self, script):
        """ Execute JS script in 'content' context with access to video element and
        YouTube #movie_player element.
        :param script: script to be executed.
        `arguments[0]` in script refers to video element, `arguments[1]` refers
        to #movie_player element (YouTube).
        :return: value returned by script
        """
        with self.marionette.using_context('content'):
            return self.marionette.execute_script(script,
                                                  script_args=[self.video,
                                                               self.player])

    @property
    def playback_quality(self):
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.getPlaybackQuality();')

    @property
    def movie_id(self):
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.'
                                      'getVideoData()["video_id"];')

    @property
    def movie_title(self):
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.'
                                      'getVideoData()["title"];')

    @property
    def player_url(self):
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.getVideoUrl();')

    @property
    def player_state(self):
        state = self.execute_yt_script('return arguments[1].'
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
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.getAdState();')

    @property
    def ad_format(self):
        """
        When ad is not playing, ad_format is False.

        :return: integer representing ad format, or False
        """
        state = self.get_ad_displaystate()
        ad_format = False
        if state:
            with self.marionette.using_context('content'):
                ad_format = self.marionette.execute_script("""
                    return arguments[0].adFormat;""",
                    script_args=[state])
        return ad_format

    @property
    def ad_skippable(self):
        state = self.get_ad_displaystate()
        skippable = False
        if state:
            with self.marionette.using_context('content'):
                skippable = self.marionette.execute_script("""
                    return arguments[0].skippable;""",
                    script_args=[state])
        return skippable

    def get_ad_displaystate(self):
        # may return None
        return self.execute_yt_script('return arguments[1].'
                                      'wrappedJSObject.'
                                      'getOption("ad", "displaystate");')

    @property
    def breaks_count(self):
        """
        Number of upcoming ad breaks.
        """
        breaks = self.execute_yt_script('return arguments[1].'
                                        'wrappedJSObject.'
                                        'getOption("ad", "breakscount")')
        # if video is not associated with any ads, breaks will be null
        return breaks or 0

    @property
    def ad_inactive(self):
        # TODO what about ad 'NOT_STARTED'
        # `player_current_time` stands still while ad is playing
        if self.player_current_time > 0 or self.player_playing:
            return (self.player_measure_progress() > 0 or
                    self.ad_state == self._yt_player_state['ENDED'])
        else:
            return self.ad_state == self._yt_player_state['ENDED']
    @property
    def ad_playing(self):
        return self.ad_state == self._yt_player_state['PLAYING']


    def attempt_ad_skip(self):
        """
        Attempt to skip ad by clicking on skip-add button.
        Return True if clicking of ad-skip button occurred.
        """
        # Wait for ad to load and become skippable
        if (self.ad_playing or self.player_measure_progress() == 0):
            sleep(10)
        else:
            # no ad playing
            return False
        if self.ad_skippable:
            selector = '#movie_player .videoAdUiSkipContainer'
            wait = Wait(self.marionette, timeout=30)
            with self.marionette.using_context('content'):
                wait.until(expected.element_displayed(By.CSS_SELECTOR,
                                                      selector))
                ad_button = self.marionette.find_element(By.CSS_SELECTOR,
                                                         selector)
                ad_button.click()
                self.marionette.log('Skipped ad.')
                return True
        else:
            return False

    def search_ad_duration(self):
        """
        :return: ad duration in seconds, if currently displayed in player
        """
        if not (self.ad_playing or self.player_measure_progress() == 0):
            return None
        # If the ad is not Flash...
        if (self.ad_playing and self.video_src.startswith('mediasource') and
                self.duration):
            return self.duration
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
    def player_stalled(self):
        """
        :return True if playback is not making progress for 4-9 seconds. This
        excludes ad breaks.

        Note that the player might just be busy with buffering due to a slow
        network.
        """
        # `current_time` stands still while ad is playing
        def condition():
            # no ad is playing and current_time stands still
            return (self.ad_state != self._yt_player_state['PLAYING'] and
                    self.measure_progress() < 0.1 and
                    self.player_measure_progress() < 0.1 and
                    (self.player_playing or self.player_buffering))

        if condition():
            sleep(2)
            if self.player_buffering:
                sleep(5)
            return condition()
        else:
            return False

    def deactivate_autoplay(self):
        """
        Attempt to turn off autoplay. Return True if successful.
        """
        element_id = 'autoplay-checkbox'
        mn = self.marionette
        wait = Wait(mn, timeout=10)

        def get_status(el):
            script = 'return arguments[0].wrappedJSObject.checked'
            return mn.execute_script(script, script_args=[el])

        try:
            with mn.using_context('content'):
                # the width, height of the element are 0, so it's not visible
                wait.until(expected.element_present(By.ID, element_id))
                checkbox = mn.find_element(By.ID, element_id)

                # Note: in some videos, due to late-loading of sidebar ads, the
                # button is rerendered after sidebar ads appear & the autoplay
                # pref resets to "on". In other words, if you click too early,
                # the pref might get reset moments later.
                sleep(1)
                if get_status(checkbox):
                    mn.execute_script('return arguments[0].'
                                      'wrappedJSObject.click()',
                                      script_args=[checkbox])
                    self.marionette.log('Toggled autoplay.')
                autoplay = get_status(checkbox)
                self.marionette.log('Autoplay is %s' % autoplay)
                return (autoplay is not None) and (not autoplay)
        except (NoSuchElementException, TimeoutException):
            return False

    def __str__(self):
        messages = [super(YouTubePuppeteer, self).__str__()]
        if self.player:
            player_state = self._yt_player_state_name[self.player_state]
            ad_state = self._yt_player_state_name[self.ad_state]
            messages += [
                '#movie_player: {',
                '\tvideo id: {0},'.format(self.movie_id),
                '\tvideo_title: {0}'.format(self.movie_title),
                '\tcurrent_state: {0},'.format(player_state),
                '\tad_state: {0},'.format(ad_state),
                '\tplayback_quality: {0},'.format(self.playback_quality),
                '\tcurrent_time: {0},'.format(self.player_current_time),
                '\tduration: {0},'.format(self.player_duration),
                '}'
            ]
        else:
            messages += ['\t#movie_player: None']
        return '\n'.join(messages)


def playback_started(yt):
    """
    Check whether playback has started.
    :param yt: YouTubePuppeteer
    """
    # usually, ad is playing during initial buffering
    return yt.player_state in [yt._yt_player_state['PLAYING'],
                               yt._yt_player_state['BUFFERING']]


def playback_done(yt):
    """
    Check whether playback is done, skipping ads if possible.
    :param yt: YouTubePuppeteer
    """
    diff = 1
    # in case ad plays at end of video, also check time remaining
    if yt.ad_state == yt._yt_player_state['PLAYING']:
        diff = yt.player_remaining_time
        yt.attempt_ad_skip()
    done = yt.player_ended or diff < 1
    return done


def wait_for_almost_done(yt, final_piece=120):
    """
    Allow the given video to play until only `final_piece` seconds remain,
    skipping ads mid-way as much as possible.
    `final_piece` should be short enough to not be interrupted by an ad.

    Depending on the length of the video, check the ad status every 10-30
    seconds, skip an active ad if possible.

    :param yt: YouTubePuppeteer
    """
    rest = 10
    retries = 5
    duration = remaining_time = 0
    # using yt.player_duration is crucial, since yt.duration might be the
    # duration of an ad (in the video element) rather than of target video
    # Nevertheless, it's still possible to get a duration of 0, depending on
    # ad behaviour, so try to skip over initial ad
    for attempt in range(retries):
        yt.attempt_ad_skip()
        duration = remaining_time = yt.player_duration
        if duration > 5 and not yt.ad_playing:
            break
        else:
            sleep(1)
    if duration < final_piece:
        # video is short so don't attempt to skip ads
        return duration
    elif duration > 600:
        # for videos that are longer than 10 minutes
        # wait longer between checks
        rest = duration/50

    def ad_done(youtube):
        return youtube.ad_state == yt._yt_player_state['ENDED']

    while remaining_time > final_piece:
        if yt.player_stalled:
            if yt.player_buffering:
                # fall back on timeout in 'wait' call that comes after this
                # in test function
                break
            else:
                message = '\n'.join(['Playback stalled', str(yt)])
                raise VideoException(message)
        if yt.breaks_count > 0:
            if not yt.attempt_ad_skip():
                # either ad is not playing or not skippable
                ad_duration = yt.search_ad_duration()
                if ad_duration:
                    wait = Wait(yt, timeout=ad_duration + 5)
                    try:
                        verbose_until(wait, yt, ad_done)
                    except TimeoutException as e:
                        yt.marionette.log('Waiting for ad to end '
                                          'timed out: %s' % e, level='WARNING')
        if remaining_time > 1.5 * rest:
            sleep(rest)
        else:
            sleep(rest/2)
        # using yt.player_duration is crucial, since yt.duration might be the
        # duration of an ad (in the video element) rather than of target video
        remaining_time = yt.player_remaining_time
    return remaining_time

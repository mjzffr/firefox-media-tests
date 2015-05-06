# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from sys import exc_info
from time import sleep

from marionette_driver import Wait
from marionette_driver.errors import TimeoutException


def verbose_until(wait, target, condition):
    """
    Performs a `wait`.until(condition)` and adds information about the state of
    `target` to any resulting `TimeoutException`.

    :param wait: a `marionette.Wait` instance
    :param target: the object you want verbose output about if a
        `TimeoutException` is raised
        This is usually the input value provided to the `condition` used by
        `wait`. Ideally, `target` should implement `__str__`
    :param condition: callable function used by `wait.until()`

    :return: the result of `wait.until(condition)`
    :raises: marionette.errors.TimeoutException
    """
    try:
        return wait.until(condition)
    except TimeoutException as e:
        message = '\n'.join([e.msg, str(target)])
        raise TimeoutException(message=message, cause=exc_info())


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
    duration = remaining_time = yt.player_duration
    if duration < final_piece:
        # video is short so don't attempt to skip ads
        return
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
                raise TimeoutException(message=message)
        if yt.breaks_count > 0:
            if not yt.attempt_ad_skip():
                # either ad is not playing or not skippable
                duration = yt.search_ad_duration()
                if duration:
                    wait = Wait(yt, timeout=duration + 5)
                    verbose_until(wait, yt, ad_done)
        if remaining_time > 1.5 * rest:
            sleep(rest)
        else:
            sleep(rest/2)
        remaining_time = yt.player_remaining_time

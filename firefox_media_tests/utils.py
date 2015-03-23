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
        diff = yt.player_duration - yt.player_current_time
        yt.attempt_ad_skip()
    done = yt.player_ended or diff < 1
    return done


def wait_for_ads(yt):
    def ad_done(youtube):
        return youtube.ad_state == yt._yt_player_state['ENDED']

    while yt.breaks_count > 0:
        if yt.breaks_count == 1:
            diff = yt.player_duration - yt.player_current_time
            if diff < 30:
                # Remaining ad break is probably at the very end of the video
                break
        if not yt.attempt_ad_skip():
            duration = yt.search_ad_duration()
            if duration:
                wait = Wait(yt, timeout=duration + 5)
                verbose_until(wait, yt, ad_done)
        if yt.breaks_count > 1:
            sleep(5)
        else:
            sleep(1)

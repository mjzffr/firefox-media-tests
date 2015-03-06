# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from sys import exc_info

from marionette import errors


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
    except errors.TimeoutException as e:
        message = '\n'.join([e.msg, str(target)])
        raise errors.TimeoutException(message=message, cause=exc_info())

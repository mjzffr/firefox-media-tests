# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from sys import exc_info
import datetime
import time

from marionette_driver.errors import TimeoutException


def timestamp_now():
    return int(time.mktime(datetime.datetime.now().timetuple()))


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


def save_memory_report(marionette):
    """ Saves memory report (like about:memory) to current working directory."""
    with marionette.using_context('chrome'):
        marionette.execute_async_script("""
            Components.utils.import("resource://gre/modules/Services.jsm");
            let Cc = Components.classes;
            let Ci = Components.interfaces;
            let dumper = Cc["@mozilla.org/memory-info-dumper;1"].
                        getService(Ci.nsIMemoryInfoDumper);
            // Examples of dirs: "CurProcD" usually 'browser' dir in
            // current FF dir; "DfltDwnld" default download dir
            let file = Services.dirsvc.get("CurProcD", Ci.nsIFile);
            file.append("media-memory-report");
            file.createUnique(Ci.nsIFile.DIRECTORY_TYPE, 0777);
            file.append("media-memory-report.json.gz");
            dumper.dumpMemoryReportsToNamedFile(file.path, null, null, false);
            log('Saved memory report to ' + file.path);
            // for dmd-enabled build
            dumper.dumpMemoryInfoToTempDir("media", false, false);
            marionetteScriptFinished(true);
            return;
        """, script_timeout=30000)

firefox-media-tests (deprecated repo)
=====================================

All code is now on mozilla-central. Details here: https://wiki.mozilla.org/Auto-tools/Projects/Platform_Quality/External_Media_Tests
s;jklakdjalkjalakj
[Marionette Python tests][marionette-python-tests] for media playback in Mozilla Firefox. MediaTestCase uses [Firefox Puppeteer][ff-puppeteer-docs] library.

Setup
-----

The instructions below assume you have a copy of the project in `some/path/firefox-media-tests` and they refer to this path as `$PROJECT_HOME`.

* Create a virtualenv called `foo`. 

   ```sh
   $ virtualenv foo
   $ source foo/bin/activate #or `foo\Scripts\activate` on Windows
   ```

* Install `firefox-media-tests` in development mode. (To get an environment that is closer to what is actually used in Mozilla's automation jobs, run `pip install -r requirements.txt` first.)

   ```sh
   $ python setup.py develop
   ```

Now `firefox-media-tests` should be a recognized command. Try `firefox-media-tests --help` to see if it works.


Running the Tests
-----------------

_Note:_ see the section about [pf-jenkins](#the-pf-jenkins-branch) for more information about running the tests in an automation environment.

In the examples below, `$FF_PATH` is a path to a recent Firefox binary.

This runs all the tests listed in `$PROJECT_HOME/firefox_media_tests/manifest.ini`:

   ```sh
   $ firefox-media-tests --binary $FF_PATH
   ```

You can also run all the tests at a particular path:

   ```sh
   $ firefox-media-tests --binary $FF_PATH some/path/foo
   ```

Or you can run the tests that are listed in a manifest file of your choice.

   ```sh
   $ firefox-media-tests --binary $FF_PATH some/other/path/manifest.ini
   ```

By default, the urls listed in `firefox_media_tests/urls/default.ini` are used for the tests, but you can also supply your own ini file of urls:

   ```sh
   $ firefox-media-tests --binary $FF_PATH --urls some/other/path/my_urls.ini
   ```

### Running EME tests

In order to run EME tests, you must use a Firefox profile that has logged into the EME provider and saved the credentials. You must also use a custom .ini file for urls to the provider's content and indicate which test to run, like above. Ex:

   ```sh
   $ firefox-media-tests --binary $FF_PATH some/path/tests.ini --profile custom_profile --urls some/path/provider-urls.ini
   ```


### Running tests in a way that provides information about a crash

What if Firefox crashes during a test run? You want to know why! To report useful crash data, the test runner needs access to a "minidump_stackwalk" binary and a "symbols.zip" file.

1. Download a `minidump_stackwalk` binary for your platform (save it whereever). Get it from http://hg.mozilla.org/build/tools/file/tip/breakpad/.
2. Make `minidump_stackwalk` executable

   ```sh
   $ chmod +x path/to/minidump_stackwalk
   ```

3. Create an environment variable called `MINIDUMP_STACKWALK` that points to that local path

   ```sh
   $ export MINIDUMP_STACKWALK=path/to/minidump_stackwalk
   ```

4. Download the `crashreporter-symbols.zip` file for the Firefox build you are testing and extract it. Example: ftp://ftp.mozilla.org/pub/firefox/tinderbox-builds/mozilla-aurora-win32/1427442016/firefox-38.0a2.en-US.win32.crashreporter-symbols.zip

5. Run the tests with a `--symbols-path` flag

  ```sh
   $ firefox-media-tests --binary $FF_PATH --symbols-path path/to/example/firefox-38.0a2.en-US.win32.crashreporter-symbols
  ```

To check whether the above setup is working for you, trigger a (silly) Firefox crash while the tests are running. One way to do this is with the [crashme add-on](https://github.com/luser/crashme) -- you can add it to Firefox even while the tests are running. Another way:

1. Find the process id (PID) of the Firefox process being used by the tests.

  ```sh
   $ ps x | grep 'Firefox'
  ```

2. Kill the Firefox process with SIGABRT.
  ```sh
  # 1234 is an example of a PID
   $ kill -6 1234
  ```

Somewhere in the output produced by `firefox-media-tests`, you should see something like:

```
0:12.68 CRASH: MainThread pid:1234. Test:test_basic_playback.py TestVideoPlayback.test_playback_starts.
Minidump anaylsed:False.
Signature:[@ XUL + 0x2a65900]
Crash dump filename:
/var/folders/5k/xmn_fndx0qs2jcpcwhzl86wm0000gn/T/tmpB4Bolj.mozrunner/minidumps/DA3BB025-8302-4F96-8DF3-A97E424C877A.dmp
Operating system: Mac OS X
                  10.10.2 14C1514
CPU: amd64
     family 6 model 69 stepping 1
     4 CPUs

Crash reason:  EXC_SOFTWARE / SIGABRT
Crash address: 0x104616900
...
```

### Setting up for network shaping tests (browsermobproxy)

1. Download the browsermob proxy zip file from http://bmp.lightbody.net/. The most current version as of this writing is browsermob-proxy-2.1.0-beta-2-bin.zip.
2. Unpack the .zip file.
3. Verify that you can launch browsermobproxy on your machine by running \<browsermob\>/bin/browsermob-proxy on your machine. I had to do a lot of work to install and use a java that browsermobproxy would like.
4. Import the certificate into your Firefox profile. Select Preferences->Advanced->Certificates->View Certificates->Import... Navigate to <browsermob>/ssl-support and select cybervilliansCA.cer. Select all of the checkboxes.
5. Tell marionette where browsermobproxy is and what port to start it on. Add the following command-line parameters to your firefox-media-tests command line:

<pre><code>
--browsermob-script <browsermob>/bin/browsermob-proxy --browsermob-port 999 --profile <your saved profile>
</code></pre>

On Windows, use browsermob-proxy.bat.

You can then call browsermob to shape the network. You can find an example in firefox_media_tests/playback/test_playback_limiting_bandwidth.py. Another example can be found at https://dxr.mozilla.org/mozilla-central/source/testing/marionette/client/marionette/tests/unit/test_browsermobproxy.py.

### A warning about video URLs
The ini files in `firefox_media_tests/urls` may contain URLs pulled from Firefox crash or bug data. Automated tests don't care about video content, but you might: visit these at your own risk and be aware that they may be NSFW. We do not intend to ever moderate or filter these URLs.

Writing a test
--------------
Write your test in a new or existing `test_*.py` file under `$PROJECT_HOME/firefox_media_tests`. Add it to the appropriate `manifest.ini` file(s) as well. Look in `media_utils` for useful video-playback functions.

* [Marionette docs][marionette-docs]
  - [Marionette Command Line Options](https://developer.mozilla.org/en-US/docs/Mozilla/Command_Line_Options)
* [Firefox Puppeteer docs][ff-puppeteer-docs]

The `pf-jenkins` Branch - soon-to-be deprecated
-----------------------------------------------

_Note that firefox-media-tests is being moved into mozilla-central some time in December 2015 or January 2016, after which the pf-jenkins branch will be deprecated._

This branch contains additional code to automate test runs in a Jenkins instance maintained as part of the [Platform Quality](https://wiki.mozilla.org/Auto-tools/Projects/Platform_Quality) project at Mozilla.

The main point of interest is `run_media_tests.py`, which is a [mozharness](https://wiki.mozilla.org/ReleaseEngineering/Mozharness) script that runs the specified tests and reports results to [Treeherder](https://wiki.mozilla.org/Auto-tools/Projects/Treeherder). The script also sets up a virtual environment for the tests, controls logging, sets up a Firefox binary to test, sets up crash-reporter symbols, etc. Look for `all_actions` in the source for a full summary.

To run `run_media_tests.py`, you must at least [download mozharness](https://hg.mozilla.org/build/mozharness/branches) and set the following environment variable:

  ```sh
  export MOZHARNESS_HOME=path/to/mozharness/directory
  ```

There's more documentation in `run_media_tests.py` itself and you can display the usage as follows:

  ```sh
  python run_media_tests.py --help
  ```

Keep in mind that, by default, `run_media_tests.py` will create and activate a virtual environment for you, so make sure to __deactivate any current virtual environment__ before you run the script.

_(Optional!)_ Reporting results to Treeherder requires credentials for the project/repo you want to submit to (e.g. mozilla-central) as well as credentials for whereever you will upload logs (an S3 bucket). Look at `config/treeherder_submission.py` to learn more.

The easiest way to turn off all the Treeherder stuff is to just add the `--no-treeherding` option.

### Examples
* This runs just the tests in `test_example.py` using a Firefox installer that you've previously downloaded, printing debug-level logs and not submitting anything to Treeherder.

  ```sh
python run_media_tests.py --installer-path=temp/firefox-41.0a1.en-US.mac64.dmg --tests=firefox_media_tests/playback/test_example.py --no-download-and-extract --no-treeherding --log-level=debug
  ```

* This does the same as above, except it runs all default tests and it _does_ submit to Treeherder. Custom job name/symbol to display on Treeherder are also specified.
  ```sh
  python run_media_tests.py --installer-path=temp/firefox-41.0a1.en-US.mac64.dmg --no-download-and-extract -c config/treeherder_submission.py --log-level=debug --job-symbol=t --job-name='Testing 123'
  ```

* This runs all the default tests but using custom media urls (medium1-60.ini). It downloads and sets up the Firefox installer and crash-reporter symbols at the specified urls. It submits the results to Treeherder. If the tests have no output for more than 4000 seconds, the firefox-media-test subprocess will be interrupted and the script will continue from there.
  ```sh
  python run_media_tests.py --installer-url <some_url> --symbols-url <some_url> --test-timeout 4000 --media-urls ./firefox_media_tests/urls/youtube/medium1-60.ini -c config/treeherder_submission.py
  ```

License
-------
This software is licensed under the [Mozilla Public License v. 2.0](http://mozilla.org/MPL/2.0/).

[marionette-python-tests]: https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette/Marionette_Python_Tests
[firefox_ui_tests]: https://github.com/mozilla/firefox-ui-tests
[ff-puppeteer-docs]: http://firefox-puppeteer.readthedocs.org/en/latest/
[marionette-docs]: http://marionette-client.readthedocs.org/en/latest/reference.html
[ff-nightly]:https://nightly.mozilla.org/

firefox-media-tests
===================

[Marionette Python tests][marionette-python-tests] for media playback in Mozilla Firefox. Uses [Firefox Puppeteer][ff-puppeteer-docs] library and parts of the test harness from [firefox-ui-tests][firefox_ui_tests].

Branches
--------
The `pf-jenkins` branch contains additional code to automate test runs in a Jenkins instance maintained as part of the [Platform Quality](https://wiki.mozilla.org/Auto-tools/Projects/Platform_Quality) project at Mozilla. It implements supporting tasks like obtaining a Firefox binary and crash-symbols for the target platform, setting up a virtual environment, and so on.

Setup
-----

* Get the source. This includes a submodule: `firefox-ui-tests`.

   ```sh
   $ git clone --recursive https://github.com/mjzffr/firefox-media-tests.git
   $ cd firefox-media-tests
   ```

   The above step clones the project into `some/path/firefox-media-tests` and the instructions below refer to this path as `$PROJECT_HOME`.

* Create a virtualenv called `foo`. (Optional, but highly recommended.)

   ```sh
   $ virtualenv foo
   $ source foo/bin/activate #or `foo\Scripts\activate` on Windows
   ```

There are two `setup.py` files: one in `$PROJECT_HOME`, another 
in `$PROJECT_HOME/firefox-ui-tests`

* First, install the `firefox-ui-tests` dependency. 

   ```sh
   $ cd firefox-ui-tests
   $ python setup.py develop
   ```

* Install `firefox-media-tests`. 

   ```sh
   $ cd ..
   $ python setup.py develop
   ```

Now `firefox-media-tests` should be a recognized command. Try `firefox-media-tests --help` to see if it works.


Running the Tests
-----------------
In the examples below, `$FF_PATH` with a path to a Firefox binary. _(Note - Mar 1, 2015: currently, these instructions only work for [Firefox Nightly][ff-nightly] 39 and Aurora 38. This depends on gecko-marionette version compatibility.)_

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

`firefox-media-tests` works very much like `firefox-ui-tests`, so see [usage for firefox-ui-tests](https://github.com/mjzffr/firefox-ui-tests#usage)

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

### A warning about video URLs
The ini files in `firefox_media_tests/urls` may contain URLs pulled from Firefox crash or bug data. Automated tests don't care about video content, but you might: visit these at your own risk and be aware that they may be NSFW. I do not intend to ever verify or filter these URLs.

Writing a test
--------------
Write your test in a new or existing `test_*.py` file under `$PROJECT_HOME/firefox_media_tests`. Add it to the appropriate `manifest.ini` file as well. Look at `media_player.py` for useful video-playback functions.

* [Marionette docs][marionette-docs]
* [Firefox Puppeteer docs][ff-puppeteer-docs]


License
-------
This software is licensed under the [Mozilla Public License v. 2.0](http://mozilla.org/MPL/2.0/).

[marionette-python-tests]: https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette/Marionette_Python_Tests
[firefox_ui_tests]: https://github.com/mozilla/firefox-ui-tests
[ff-puppeteer-docs]: http://firefox-puppeteer.readthedocs.org/en/latest/
[marionette-docs]: http://marionette-client.readthedocs.org/en/latest/reference.html 
[ff-nightly]:https://nightly.mozilla.org/

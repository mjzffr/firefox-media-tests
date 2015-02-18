firefox-media-tests
===================

[Marionette Python tests][marionette-python-tests] for media playback in Firefox. Uses [Firefox Puppeteer][ff-puppeteer] library and test harness from [firefox-ui-tests][firefox_ui_tests]

Setup
-----

1. Get the source. This includes a submodule: `firefox-ui-tests`.

   ```sh
   $ git clone --recursive git@github.com:mjzffr/firefox-media-tests.git
   $ cd firefox-media-tests
   ```
  
2. Create a virtualenv called `foo`

   ```sh
   $ virtualenv foo
   $ source foo/bin/activate
   ```

3. Install `firefox-ui-tests`

   ```sh
   $ cd firefox-ui-tests
   $ python setup.py develop
   ```

Now `firefox-ui-tests` should be a recognized command. Try `firefox-ui-tests --help` to see if it works.


Running the Tests
-----------------
See [usage for firefox-ui-tests](https://github.com/mjzffr/firefox-ui-tests#usage)

In our case, the tests are in `media-tests`. Replace `$FF_PATH` with a path to a Firefox binary.

   ```sh
   $ firefox-ui-tests --binary $FF_PATH media-tests
   ```

Or you can run the tests that are listed in a manifest file.

   ```sh
   $ firefox-ui-tests --binary $FF_PATH media-tests/manifest.ini
   ```


Writing a test
--------------
Write your test in a new `test_*.py` file. Add it to `manifest.ini` as well.


License
-------
This software is licensed under the [Mozilla Public License v. 2.0](http://mozilla.org/MPL/2.0/).

[marionette-python-tests]: https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette/Marionette_Python_Tests
[firefox_ui_tests]: https://github.com/mozilla/firefox-ui-tests
[ff-puppeteer]: http://firefox-puppeteer.readthedocs.org/en/latest/

firefox-media-tests
===================

[Marionette Python tests][marionette-python-tests] for media playback in Mozilla Firefox. Uses [Firefox Puppeteer][ff-puppeteer-docs] library and parts of the test harness from [firefox-ui-tests][firefox_ui_tests].

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
   $ source foo/bin/activate
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
   $ firefox-ui-tests --binary $FF_PATH some/path/foo
   ```

Or you can run the tests that are listed in a manifest file of your choice.

   ```sh
   $ firefox-ui-tests --binary $FF_PATH some/other/path/manifest.ini
   ```

`firefox-media-tests` works very much like `firefox-ui-tests`, so see [usage for firefox-ui-tests](https://github.com/mjzffr/firefox-ui-tests#usage)

Writing a test
--------------
Write your test in a new or existing `test_*.py` file under `$PROJECT_HOME/firefox_media_tests`. Add it to the appropriate `manifest.ini` file as well.

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

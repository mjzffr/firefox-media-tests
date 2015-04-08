from firefox_ui_harness.testcase import FirefoxTestCase


class TestSomethingElse(FirefoxTestCase):
    def setUp(self):
        FirefoxTestCase.setUp(self)
        self.test_urls = [
            'mozilla.html',
            ]
        self.test_urls = [self.marionette.absolute_url(t)
                          for t in self.test_urls]

    def tearDown(self):
        FirefoxTestCase.tearDown(self)

    def test_foo(self):
        print 'foo!'
        with self.marionette.using_context('content'):
            self.marionette.navigate(self.test_urls[0])

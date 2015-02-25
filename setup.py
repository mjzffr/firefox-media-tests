# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages

PACKAGE_VERSION = '0.1'

setup(name='firefox-media-tests',
      version=PACKAGE_VERSION,
      description=('A collection of Mozilla Firefox media playback tests run '
                   'with Marionette'),
      keywords='mozilla',
      author='Mozilla Automation and Tools Team',
      author_email='tools@lists.mozilla.org',
      license='MPL 2.0',
      packages=find_packages(),
      include_package_data=True,
      entry_points="""
        [console_scripts]
        firefox-media-tests = media_test_harness:run
    """)

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from manifestparser import read_ini


def get_videos(video_manifest):
    with open(video_manifest, 'r'):
        return [line[0] for line in read_ini(video_manifest)]

root = os.path.abspath(os.path.dirname(__file__))
manifest = os.path.join(root, 'manifest.ini')
resources = os.path.join(root, 'resources')
urls = os.path.join(root, 'urls')


# default set of videos
# (overwritten if --urls option is used)
videos = get_videos(os.path.join(urls, 'default.ini'))

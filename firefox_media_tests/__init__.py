# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from manifestparser import read_ini

root = os.path.abspath(os.path.dirname(__file__))
manifest = os.path.join(root, 'manifest.ini')
resources = os.path.join(root, 'resources')

# Sets of videos
video_manifest = os.path.join(root, 'video_data.ini')
with open(video_manifest, 'r'):
    videos = [line[0] for line in read_ini(video_manifest)]

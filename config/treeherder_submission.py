import os

TREEHERDER_CONFIG = os.environ.get('TREEHERDER_CONFIG') or 'credentials.ignore'

config = {
    #"treeherder_url": "http://local.treeherder.mozilla.org",
     "treeherder_url": "https://treeherder.allizom.org",

    # Paths are relative to 'base_work_dir'
    #"treeherder_credentials_path": "credentials.ignore/treeherder-local-credentials.json",
     "treeherder_credentials_path": os.path.join(TREEHERDER_CONFIG, "treeherder-staging-credentials.json"),
    "s3_credentials_path": os.path.join(TREEHERDER_CONFIG, "s3-credentials.json"),
    "group_name": "VideoPuppeteer",
    "group_symbol": "VP",
    # Can overwrite these via command-line options
    "job_name": "MSE Video Playback",
    "job_symbol": "m",

    "job_description": "firefox-media-tests (video playback)",
    "job_reason": "pf-jenkins scheduler",
    "job_who": "Platform Quality"
}

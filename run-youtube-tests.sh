#!/bin/bash

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Based on: https://github.com/sydvicious/mozplatformqa-jenkins/blob/master/run-media-source-web-platform.sh

# This must be called from an environment where python is setup correctly.
# The firefox binary must have been downloaded and expanded.
# The first argument is a url to the firefox binary. The second is the platform. The valid values are "mac", "win32",
# "win64", and "linux".
# On Windows, this requires the mozilla-build system, installed at c:\mozilla-build.
# This also requires pip and virtualenv to have been installed into the python
# distribution. Not ideal.

FIREFOX_ARCHIVE=$1
SYMBOLS_ARCHIVE=$2
PLATFORM=$3
URLS=$4

WORKSPACE=`pwd`
SYMBOLS_DIR_NAME='symbols'

function set_virtualenv {
    # Try to use the virtual env that may have been activated
    # before this script was called from cmd.exe; otherwise create a new one.
    if [ -d "$VIRTUAL_ENV" ]; then
        unset _OLD_VIRTUAL_PATH
        unset _OLD_VIRTUAL_PYTHONHOME
        unset _OLD_VIRTUAL_PS1
        source $VIRTUAL_ENV/Scripts/activate
    else
        VENV_NAME=venv
        cd $WORKSPACE
        if [ -d "./$VENV_NAME" ]; then
            rm -rf ./$VENV_NAME
        fi
        virtualenv $VENV_NAME
        source $VENV_NAME/Scripts/activate
    fi

    echo python is $(which python)
    echo PATH is $PATH
    echo VIRTUAL_ENV is $VIRTUAL_ENV
}

# On Windows, we expect this script to be called via
# "c:\mozilla-build\msys\bin\bash -xe $script" from cmd.exe
# in which case the bash PATH is not set up properly and must be repopulated
if [ "$PLATFORM" = "win32" ]; then
    export PATH=/bin:/c/mozilla-build/wget:/c/mozilla-build/info-zip:/c/mozilla-build/python:/c/mozilla-build/python/Scripts
    set_virtualenv
elif [ "$PLATFORM" = "win64" ]; then
    export PATH=/bin:/c/mozilla-build/wget:/c/mozilla-build/info-zip:/c/mozilla-build/python:/c/mozilla-build/python/Scripts
    set_virtualenv
fi

function usage {
    echo "Usage: run-youtube-tests.sh <firefox_archive> <platform>"
    exit 1
}

function unimplemented {
    echo "UNIMPLEMENTED"
    exit 20
}

if [ "x$PLATFORM" = "x" ]; then
    usage
fi

function unpack_mac_archive {
  archive_name=`basename $FIREFOX_ARCHIVE`
  hdiutil attach -quiet -mountpoint /Volumes/MSE $WORKSPACE/$archive_name
  rm -rf $WORKSPACE/firefox.app
  cp -r /Volumes/MSE/*.app $WORKSPACE/firefox.app
  hdiutil detach /Volumes/MSE
}

function unpack_win_archive {
  cd $WORKSPACE
  rm -rf firefox
  firefox_archive_name=`basename $FIREFOX_ARCHIVE`
  unzip -q $firefox_archive_name
}

function unpack_linux_archive {
  unimplemented
}

function download_archive {
  archive_name=`basename $1`
  rm -f $archive_name
  wget $1
}

function unpack_symbols_archive {
  cd $WORKSPACE
  rm -rf $SYMBOLS_DIR_NAME
  mkdir -p $SYMBOLS_DIR_NAME
  symbols_archive_name=`basename $SYMBOLS_ARCHIVE`
  cd $SYMBOLS_DIR_NAME
  unzip -q $WORKSPACE/$symbols_archive_name
  cd ..
}

download_archive $FIREFOX_ARCHIVE
if [ "$PLATFORM" = "mac" ] ; then
  unpack_mac_archive
elif [ "$PLATFORM" = "win32" ] ; then
  unpack_win_archive
elif [ "$PLATFORM" = "win64" ] ; then
  unpack_win_archive
else
  unpack_linux_archive
fi

download_archive $SYMBOLS_ARCHIVE
unpack_symbols_archive

# Install dependencies
cd $WORKSPACE/firefox-ui-tests
python setup.py develop
cd $WORKSPACE
python setup.py develop

if [ "$PLATFORM" = "mac" ]; then
  BINARY="$WORKSPACE/firefox.app/Contents/MacOS/firefox"
elif [ "$PLATFORM" = "win32" ]; then
  BINARY="$WORKSPACE/firefox/firefox.exe"
elif [ "$PLATFORM" = "win64" ]; then
  BINARY="$WORKSPACE/firefox/firefox.exe"
else
  BINARY="$WORKSPACE/firefox/firefox"
fi

cd $WORKSPACE

OPTIONS="--binary $BINARY"
if [ -n "$SYMBOLS_ARCHIVE" ]; then
  OPTIONS=$OPTIONS" --symbols-path $WORKSPACE/$SYMBOLS_DIR_NAME"
fi
if [ -n "$URLS" ]; then
  OPTIONS=$OPTIONS" --urls $URLS"
fi

firefox-media-tests $OPTIONS | tee $WORKSPACE/tests.log

NO_UNEXPECTED_RESULTS=`grep --count "Unexpected results: 0" $WORKSPACE/tests.log`
if [ $NO_UNEXPECTED_RESULTS -ne "0" ]; then
  exit 0
fi
exit 1

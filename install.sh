#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

DESKTOP_DIR=~/.local/share/applications/

sed 's|_EXEC_|'"$SCRIPTPATH"'/wacom-area.py|' wacom-area.desktop > $DESKTOP_DIR/wacom-area.desktop



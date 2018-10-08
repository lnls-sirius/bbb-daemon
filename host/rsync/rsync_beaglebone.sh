#!/bin/sh
# --------------------------------------------------
# Sirius Control System - Beaglebone Black
# Remote Sync Files and Libraries
# --------------------------------------------------
# October, 2018
# Patricia H Nallin
# --------------------------------------------------

RSYNC_SERVER="10.0.6.49"
RSYNC_LOCAL="/root"
RSYNC_PORT="873"
PROJECT=$1


# Check whether Rsync Server is available - First item in rsync.conf must be "online"
SYNC_AVAILABLE=`rsync -n $RSYNC_SERVER::`;
if [ "${SYNC_AVAILABLE%% *}" = "online" ]; then
    echo "Rsync Server is available!";
    echo "Checking for updates...";
    UPDATES=`rsync -ainO $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT`;

    # No updates available
    if [ -z "$UPDATES" ]; then
        echo "No updates found.";

    # There are updates for the project, sync files and build libraries
    else
        echo "Updates available!";
        echo -n "Updating... ";
        rsync -a --delete-after $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT > /tmp/rsync.log;
        if [ $? -eq 0 ]; then
            if [ "$PROJECT" = "pru-serial485" ] || [ "$PROJECT" = "counting-pru" ]; then
                echo "Updated!";
                echo "Building library...";
                cd $RSYNC_LOCAL/$PROJECT/src;
                ./library_build.sh;
            else
                echo "Done!";
            fi
        else
            echo "Updating failed.";
        fi
    fi
else
    echo "Rsync Server is not available.";
fi

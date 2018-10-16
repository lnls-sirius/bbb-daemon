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

# Proceed if a project was requested
if [ ! -z ${PROJECT} ]; then
    # Check whether Rsync Server is available - First item in rsync.conf must be "online"
    SYNC_AVAILABLE=`rsync -n $RSYNC_SERVER::`;
    if [ "${SYNC_AVAILABLE%% *}" = "online" ]; then
        # Server is available. Check if there are updates
        UPDATES=`rsync -ainO $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT`;

        # No updates available
        if [ -z "$UPDATES" ]; then
            echo "No updates found.";

        # There are updates for the project, sync files and build libraries
        else
            rsync -a --delete-after $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT > /tmp/rsync.log;
            if [ $? -eq 0 ]; then
                # If project is listed below, build libraries as well
                if [ "$PROJECT" = "pru-serial485" ] || [ "$PROJECT" = "counting-pru" ]; then
                    cd $RSYNC_LOCAL/$PROJECT/src;
                    ./library_build.sh;
                fi
            else
                echo "Updating failed.";
            fi
        fi
    else
        echo "Rsync Server is not available.";
    fi
else
    echo "No project selected for updating.";
fi

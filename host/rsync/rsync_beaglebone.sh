#!/bin/sh
# --------------------------------------------------
# Sirius Control System - Beaglebone Black
# Remote Sync Files and Libraries
# --------------------------------------------------
# October, 2018
# Patricia H Nallin
# --------------------------------------------------

PROJECT=$1

# Proceed if a project was requested
if [ ! -z ${PROJECT} ]; then
    # Check whether Rsync Server is available - First item in rsync.conf must be "online"
    SYNC_AVAILABLE=`rsync -n $RSYNC_SERVER::`;
    if [ "${SYNC_AVAILABLE%% *}" = "online" ]; then
        # Server is available. Check if there are updates
        if [ "${PROJECT}" = "etc-folder" ]; then
            UPDATES=`rsync -ainO $RSYNC_SERVER::$PROJECT /etc`;
        else
            UPDATES=`rsync -ainO $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT`;
        fi

        # No updates available
        if [ -z "$UPDATES" ]; then
            echo "No updates found.";
            exit 1

        # There are updates for the project, sync files and build libraries
        else
            if [ "${PROJECT}" = "etc-folder" ]; then
                rsync -a $RSYNC_SERVER::$PROJECT /etc > /tmp/rsync.log;
            else
                rsync -a --delete-after $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT > /tmp/rsync.log;
            fi
            if [ $? -eq 0 ]; then
                # If project is listed below, build libraries as well
                if [ "$PROJECT" = "pru-serial485" ] || [ "$PROJECT" = "counting-pru" ]; then
                    pushd $RSYNC_LOCAL/$PROJECT/src
                        ./library_build.sh;
                    popd
                fi
                exit 0
            else
                echo "Updating failed.";
                exit 1
            fi
        fi
    else
        echo "Rsync Server is not available.";
        exit 1
    fi
else
    echo "No project selected for updating.";
    exit 1
fi

# rsync -av 10.0.6.51::bbb-daemon/.gitignore /root/temp.ignore
# --exclude
# echo \' >> /root/temp.ignore | << echo \' | cat /root/temp.ignore | sed '/^#/ d' | tr '\n' ' '
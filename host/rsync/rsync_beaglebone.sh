#!/bin/bash
# -----------------------------------------------------------------------------
# Sirius Control System - Beaglebone Black
# Remote Sync Files and Libraries
# -----------------------------------------------------------------------------
# October, 2018
# Patricia H Nallin
# -----------------------------------------------------------------------------
set -x
PROJECT=$1


echo

# Proceed if a project was requested
if [ ! -z ${PROJECT} ]; then
    # ---------------------------------------------------------------------
    # FAC files
    if [ "${PROJECT}" = "dev-packages" ] || [ "${PROJECT}" = "ps-ioc-config-files" ] || [ "$PROJECT" = "mathphys" ] || [ "$PROJECT" = "machine-applications" ]; then
        SYNC_AVAILABLE=`rsync -n --contimeout=10 $RSYNC_FAC_SERVER::`;
        if [ "${SYNC_AVAILABLE%% *}" = "online" ]; then
            UPDATES=`rsync -ainO $RSYNC_FAC_SERVER::$PROJECT $FAC_PATH/$PROJECT`;

            # ---------------------------------------------------------------------
            # No updates available
            if [ -z "$UPDATES" ]; then
                echo "No updates found.";
                exit 1
            # ---------------------------------------------------------------------
            #  Synchronizing files. There are updates for the project.
            else
                if [ ! -d "$DIRECTORY" ]; then
                    mkdir -p $FAC_PATH
                fi
                rsync -a --delete-after $RSYNC_FAC_SERVER::$PROJECT $FAC_PATH/$PROJECT > /tmp/rsync.log;
                # ---------------------------------------------------------------------
                # Success on sync. Build libraries
                if [ $? -eq 0 ]; then
                    pushd $FAC_PATH/$PROJECT;
                        if [ "${PROJECT}" = "dev-packages" ]; then
                            pushd siriuspy
                                python-sirius setup.py install
                                rm -rf dist build */*.egg-info *.egg-info
                            popd
                        elif [ "${PROJECT}" = "mathphys" ]; then
                            python-sirius setup.py install
                            rm -rf dist build */*.egg-info *.egg-info
                        elif [ "${PROJECT}" = "machine-applications" ]; then
                            pushd as-ps
                                python-sirius setup.py install
                                rm -rf dist build */*.egg-info *.egg-info
                                # instal AS-PS IOC as service
                                cp -rf ./systemd/sirius-bbb-ioc-ps.service /etc/systemd/system/
                                mkdir -p /root/sirius-iocs
                                systemctl daemon-reload
                            popd
                        fi
                    popd
                fi
            fi
        fi
    # ---------------------------------------------------------------------



    # ---------------------------------------------------------------------
    # CON files
    else
        echo "CON files"
        # -------------------------------------------------------------------------
        # Check whether Rsync Server is available - First item in rsync.conf must be "online"
        SYNC_AVAILABLE=`rsync -n --contimeout=10 $RSYNC_SERVER::`;
        if [ "${SYNC_AVAILABLE%% *}" = "online" ]; then
            # ---------------------------------------------------------------------
            # etc-folder files
            if [ "${PROJECT}" = "etc-folder" ]; then
                UPDATES=`rsync -ainO $RSYNC_SERVER::$PROJECT /etc`;
            # ---------------------------------------------------------------------
            # Project files
            else
                UPDATES=`rsync -ainO $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT`;
            fi

            # No updates available
            if [ -z "$UPDATES" ]; then
                echo "No updates found.";
                exit 1
            # ---------------------------------------------------------------------
            #  Synchronizing files. There are updates for the project.
            else
                # -----------------------------------------------------------------
                # etc-folder files
                if [ "${PROJECT}" = "etc-folder" ]; then
                    rsync -a $RSYNC_SERVER::$PROJECT /etc > /tmp/rsync.log;
                # -----------------------------------------------------------------
                # Project files - Also build libraries
                else
                    rsync -a --delete-after $RSYNC_SERVER::$PROJECT $RSYNC_LOCAL/$PROJECT > /tmp/rsync.log;
                fi
                if [ $? -eq 0 ]; then
                    # If project is listed below, build libraries as well
                    if [ "$PROJECT" = "pru-serial485" ] || [ "$PROJECT" = "counting-pru" ]; then
                        pushd $RSYNC_LOCAL/$PROJECT/src
                            ./library_build.sh
                        popd
                    fi
                    if [ "$PROJECT" = "eth-bridge-pru-serial485" ]; then
                        pushd $RSYNC_LOCAL/$PROJECT/server
                            make install
                        popd
                    fi
                    exit 0
                fi
            fi
        fi
    fi
else
    echo "No project selected for updating.";
    exit 1
fi

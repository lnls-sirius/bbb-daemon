#!/bin/bash
# -*- coding: utf-8 -*-

pushd /root/bbb-daemon/host/rsync
    ./rsync_beaglebone.sh mathphys
    ./rsync_beaglebone.sh dev-packages
    ./rsync_beaglebone.sh machine-applications
    hn=$(hostname)
    # Removing old entries
    sed -i -e '/sirius/d' /etc/hosts
    sed -i -e '/127.0.0.1/d' -e '/127.0.1.1/d' /etc/hosts
    # Writing new values, described below
    sed -i -e '1i\127.0.0.1    localhost' -e '1i\127.0.1.1    '"$hn" /etc/hosts
    sed -i -e '$a\'"#"' sirius-consts server alias' -e '$a\10.128.255.5 sirius-consts.lnls.br servweb' /etc/hosts
popd

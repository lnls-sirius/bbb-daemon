#!/bin/bash
# -*- coding: utf-8 -*-

pushd /root/bbb-daemon/host/rsync
    ./rsync_beaglebone.sh mathphys
    ./rsync_beaglebone.sh dev-packages
    ./rsync_beaglebone.sh machine-applications
    sed -i -e '/sirius/d' /etc/hosts
    sed -i -e '$a\'"#"' sirius-consts server alias' -e '$a\10.128.254.203 sirius-consts.lnls.br' /etc/hosts
popd


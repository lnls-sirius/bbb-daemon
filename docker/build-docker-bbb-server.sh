#!/bin/sh


DOCKER_MANTAINER_NAME=lnlscon
DOCKER_NAME=bbb-daemon-container
DOCKER_TAG=bbb-server

docker build --no-cache -t ${DOCKER_MANTAINER_NAME}/${DOCKER_NAME}:${DOCKER_TAG} .

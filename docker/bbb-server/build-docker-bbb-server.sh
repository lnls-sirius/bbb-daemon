#!/bin/sh
DOCKER_MANTAINER_NAME=lnlscon
DOCKER_NAME=bbb-daemon-container
DOCKER_TAG=latest

docker build -t ${DOCKER_MANTAINER_NAME}/${DOCKER_NAME}:${DOCKER_TAG} .

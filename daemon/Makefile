PREFIX ?= /usr/local

# Docker files
SERVICE_NAME = bbb-daemon
SRC_SERVICE_FILE = ${SERVICE_NAME}.service
SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install uninstall

all:

install:
    #pip3 install --no-cache-dir -r ../docker/bbb-server/requirements.txt
	cp --preserve=mode ${SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	systemctl daemon-reload
	systemctl stop ${SERVICE_NAME}
	systemctl start ${SERVICE_NAME}

uninstall:
	systemctl stop ${SERVICE_NAME}
	rm -f ${SERVICE_FILE_DEST}/${SRC_SERVICE_FILE}
	systemctl daemon-reload

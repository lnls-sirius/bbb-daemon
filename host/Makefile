PREFIX ?= /usr/local

SERVICE_NAME = bbb-daemon
SRC_SERVICE_FILE = ${SERVICE_NAME}.service
SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install uninstall

all:

install:
	apt-get install python3
	apt-get install python3-pip
	pip3 install --no-cache-dir -r requirements.txt
	cp --preserve=mode services/${SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	systemctl daemon-reload
	systemctl stop ${SERVICE_NAME}
	systemctl start ${SERVICE_NAME}
	systemctl enable ${SERVICE_NAME}

uninstall:
	systemctl stop ${SERVICE_NAME}
	rm -f ${SERVICE_FILE_DEST}/${SRC_SERVICE_FILE}
	systemctl daemon-reload

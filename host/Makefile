PREFIX ?= /usr/local

DAEMON_SERVICE_NAME = bbb-daemon
DAEMON_SRC_SERVICE_FILE = ${DAEMON_SERVICE_NAME}.service

FUNCTION_SERVICE_NAME = bbb-function
FUNCTION_SRC_SERVICE_FILE = ${FUNCTION_SERVICE_NAME}.service

SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install uninstall

all:

install:
	# Dependencies
	apt-get install python3
	apt-get install python3-pip
	pip3 install --no-cache-dir -r requirements.txt

	# Services
	cp --preserve=mode services/${DAEMON_SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	cp --preserve=mode services/${FUNCTION_SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}

	systemctl daemon-reload

	systemctl stop ${DAEMON_SERVICE_NAME}
	systemctl start ${DAEMON_SERVICE_NAME}
	systemctl enable ${DAEMON_SERVICE_NAME}

	systemctl stop ${FUNCTION_SERVICE_NAME}
	systemctl start ${FUNCTION_SERVICE_NAME}
	systemctl enable ${FUNCTION_SERVICE_NAME}

uninstall:
	systemctl stop ${DAEMON_SERVICE_NAME}
	systemctl stop ${FUNCTION_SERVICE_NAME}

	rm -f ${SERVICE_FILE_DEST}/${DAEMON_SRC_SERVICE_FILE}
	rm -f ${SERVICE_FILE_DEST}/${FUNCTION_SRC_SERVICE_FILE}

	systemctl daemon-reload

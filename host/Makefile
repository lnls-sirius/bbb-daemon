PREFIX ?= /usr/local

DAEMON_SERVICE_NAME = bbb-daemon
DAEMON_SRC_SERVICE_FILE = ${DAEMON_SERVICE_NAME}.service

FUNCTION_SERVICE_NAME = bbb-function
FUNCTION_SRC_SERVICE_FILE = ${FUNCTION_SERVICE_NAME}.service

SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install uninstall daemon dependencies clean function

all:

daemon:
	cp --preserve=mode services/${DAEMON_SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	
	apt-get install python3-pip
	pip3 install --no-cache-dir -r requirements.txt
	pip3 install Adafruit_BBIO

	systemctl daemon-reload
	
        # Do not enable this service anymore.
	#systemctl enable ${DAEMON_SERVICE_NAME}
	#systemctl restart ${DAEMON_SERVICE_NAME}

function:
	# Services
	cp --preserve=mode services/${FUNCTION_SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}

	apt-get install python3-pip
	pip3 install --no-cache-dir -r requirements.txt
	pip3 install Adafruit_BBIO

	systemctl daemon-reload

	systemctl enable ${FUNCTION_SERVICE_NAME}
	systemctl restart ${FUNCTION_SERVICE_NAME}

install:
	# Services
	cp --preserve=mode services/${DAEMON_SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	cp --preserve=mode services/${FUNCTION_SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}

	apt-get install python3-pip
	pip3 install --no-cache-dir -r requirements.txt
	pip3 install Adafruit_BBIO

	systemctl daemon-reload

        # Do not enable this service anymore.
	#systemctl enable ${DAEMON_SERVICE_NAME}
	#systemctl restart ${DAEMON_SERVICE_NAME}

	systemctl enable ${FUNCTION_SERVICE_NAME}
	systemctl restart ${FUNCTION_SERVICE_NAME}

uninstall:
	systemctl stop ${DAEMON_SERVICE_NAME}
	systemctl stop ${FUNCTION_SERVICE_NAME}

	rm -f ${SERVICE_FILE_DEST}/${DAEMON_SRC_SERVICE_FILE}
	rm -f ${SERVICE_FILE_DEST}/${FUNCTION_SRC_SERVICE_FILE}

	systemctl daemon-reload

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~'    -exec rm --force {} +
	find . -name '__pycache__'  -exec rm -rd --force {} +


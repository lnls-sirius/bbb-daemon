PREFIX ?= /usr/local

SERVICE_NAME = serial-bind
SRC_SERVICE_FILE = ${SERVICE_NAME}.service
SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install uninstall

all:
clean:

install:
	pip3 install Adafruit_BBIO
	apt-get install socat
	cp --preserve=mode ${SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	systemctl daemon-reload
	systemctl stop ${SERVICE_NAME}
	systemctl start ${SERVICE_NAME}
	systemctl enable ${SERVICE_NAME}

uninstall:
	systemctl stop ${SERVICE_NAME}
	systemctl disable ${SERVICE_NAME}
	rm -f ${SERVICE_FILE_DEST}/${SRC_SERVICE_FILE}
	systemctl daemon-reload

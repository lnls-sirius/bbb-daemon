PREFIX ?= /usr/local

SERVICE_NAME = rsync

.PHONY: all install 

all:
install:
	cp rsyncd.conf /etc/rsyncd.conf 
	systemctl daemon-reload
	systemctl start ${SERVICE_NAME}
	systemctl enable ${SERVICE_NAME}

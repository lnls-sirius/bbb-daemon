.PHONY: install cert

install:
	apt-get -y install python3-pip python3-dev nginx
	pip3 install virtualenv==16.0.0
	virtualenv bbb-daemon-virtualenv
	cd install && ./setup-env.sh

install-docker:
	mkdir -p /opt/redis-data
	docker run --network host -v /opt/redis-data:/data --name bbb-redis -d redis redis-server --appendonly yes

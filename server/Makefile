.PHONY: install cert

install:
	sudo apt-get update
	sudo apt-get -y install python3-pip python3-dev nginx
	echo "Using Python 3 ..."
	echo "Installing requirements ..."
	pip3 install --no-cache-dir -r ../docker/bbb-server/requirements.txt

cert:
	sudo apt-get install openssl
	openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

install-docker:
	sudo mkdir -p /opt/redis-data
	sudo docker run --network host -v /opt/redis-data:/data --name bbb-redis -d redis redis-server --appendonly yes 
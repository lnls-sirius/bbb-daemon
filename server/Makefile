.PHONY: install

install:
	sudo apt-get update
	sudo apt-get -y install python3-pip python3-dev nginx
	echo "Using Python 3 ..."
	echo "Installing requirements ..."
	pip3 install --no-cache-dir -r ../docker/bbb-server/requirements.txt


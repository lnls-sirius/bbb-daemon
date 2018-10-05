# BeagleBone Black Monitoring Services

Given the fact that the Controls Group will have more than 600 BeagleBone hosts acting as IOC controllers in Sirius, a way of monitoring the ones that will eventually show some fault is vey important. We propose therefore a client-server archicteture in which each host pings a server every 1 second to signalize it is alive. The server holds all the information about all hosts that are currently pinging it and provides a TCP socket interface to manage and monitor them. Additionally, a Qt5 GUI is made available to manage the hosts.


## Host 

Every service that is meant to be use inside the BBB is located inside the <b>host</b> directory. <br>
Currently it consists in a program that will ping the server every 1 second sending usefull information and allowing us to know which boards are alive and what kind of device is connected to it.

The host app also is capable of receiving commands from the server side. The goal is to have a simple fron-end allowing us to send commands such as:
<ul>
    <li>Change your ip</li>
    <li>Change your hostname</li>
    <li>Update project .... (Rsync Client)</li>
</ul>

A simple make inside the host foler should me enought to set everything going.
```
make install 
```

## Server

The server keeps a list of all hosts connected to the Controls Group's network. Move to the `server/` directory and execute `./run.sh`.


An `SFTF server is running on PORT 1026`, this service is used to provide the projects defined on the types fields. Clients are only able to retrive data from 
the FTP. The server application is responsable to to keep the data up-to-date and fetch is to its clients.

A `web interface is present on PORT 4850`. Flask is the framework of choice for development and Waitress as the WSGI server.

Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions. 

Waitress is meant to be a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones which live in the Python standard library. It runs on CPython on Unix and Windows under Python 2.7+ and Python 3.3+. It is also known to run on PyPy 1.6.0+ on UNIX. It supports HTTP/1.0 and HTTP/1.1.

## Qt5 Graphical Interface

A Qt5 interface to manage types and nodes. It connects to the server through a TCP socket and sends requests according to the user actions. Move to `client/qt` and run `run.sh`.
 
## Docker

To launch the server application on swarm enter the directory `docker/swarm/ ` and run `sudo docker stack deploy -c docker-swarm.yml bbb-daemon`. To remove the containers `sudo docker stack rm bbb-daemon`.

### Configuration files

Each BBB uses basically two kinds of information during boot:

- Its pin configuration, which is defined in a `*.dtbo`.
- The scripts that should be executed. They are launched from a systemd service, called `rc-local.service` . This service uses the command defined in another file, `rc.local`. Therefore, `rc.local` must be updated depending on the function that the host will perform.

Furthermore, we added two more parameters:

- The PV prefix that the IOC running in the BBB will use to create the variables.
- A type parameter to identify the board that the BBB is connected to and the project that should be synchronized with.

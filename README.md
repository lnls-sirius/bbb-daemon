# BeagleBone Black Monitoring Services

Given the fact that the Controls Group will have more than 600 BeagleBone hosts acting as IOC controllers in Sirius, a way of monitoring the ones that will eventually show some fault is vey important. We propose therefore a client-server archicteture in which each host pings a server every 1 second to signalize it is alive. The server holds all the information about all hosts that are currently pinging it and provides a TCP socket interface to manage and monitor them. Additionally, a Qt5 GUI is made available to manage the hosts.

## Server

The server keeps a list of all hosts connected to the Controls Group's network. Move to the `server/` directory and execute `./run.sh`.

## Qt5 Graphical Interface

A Qt5 interface to manage types and nodes. It connects to the server through a TCP socket and sends requests according to the user actions. Move to `client/qt` and run `run.sh`.

## Daemon client

This program should be executed in the host that needs to be monitored. It pings the server every 1 second. It can also receive commands that should run in the host. Execute `run.sh` in `daemon/` folder.


### Configuration files

Each BBB uses basically two kinds of information during boot:

- Its pin configuration, which is defined in a `*.dtbo`.
- The scripts that should be executed. They are launched from a systemd service, called `rc-local.service` . This service uses the command defined in another file, `rc.local`. Therefore, `rc.local` must be updated depending on the function that the host will perform.

Furthermore, we added two more parameters:

- The PV prefix that the IOC running in the BBB will use to create the variables.
- A type parameter to identify the board that the BBB is connected to and the project that should be synchronized with.

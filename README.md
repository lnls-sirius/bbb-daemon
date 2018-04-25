# BeagleBone Black Monitoring Services

Given the fact that the Controls Group will have more than 600 BeagleBone hosts acting as IOC controllers in Sirius, a way of monitoring the ones that will eventually show some fault is vey important. We propose therefore a client-server archicteture in which each host pings a server every 1 second to signalize it is alive. The server holds all the information about all hosts that are currently pinging it and provides a TCP socket interface to manage and monitor them. Additionally, a Qt4 GUI is made available to manage the hosts.

## Server

The server keeps a list of all hosts connected to the Controls Group's network. Move to the `server/` directory and execute `./run.sh`.

## Qt4 Graphical Interface

A Qt4 interface to manage types and nodes. It connects to the server through a TCP socket and sends requests according to the user actions. Move to `client/qt` and run `run.sh`.

## Daemon client

This program should be executed in the host that needs to be monitored. It pings the server every 1 second. It can also receive commands that should run in the host. Execute `run.sh` in `daemon/` folder.




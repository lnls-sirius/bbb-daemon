# BeagleBone Black Monitoring Services

Given the fact that the Controls Group will have more than 600 BeagleBone hosts acting as IOC controllers in Sirius, a way of monitoring the ones that will eventually show some fault is vey important. We propose therefore a client-server archicteture in which each host pings a server every 1 second to signalize it is alive. The server holds all the information about all hosts that are currently pinging it and provides a TCP socket interface to manage and monitor them. Additionally, a Qt5 GUI is made available to manage the hosts.

## Host 

Every service that is meant to be use inside the BBB is located inside the <b>host</b> directory. <br>
Currently it consists in a program that will ping the server every x seconds sending usefull information and allowing us to know which boards are alive and what kind of device is connected to it.

The host app also is capable of receiving commands from the server side. The goal is to have a simple fron-end allowing us to send commands such as:
<ul>
    <li>Change your ip</li>
    <li>Change your hostname</li>
    <li>Update project .... (Rsync Client)</li>
    <li>etc...</li>
</ul>

## Server
Flask is the framework of choice for development.
Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions. 

## Rest API
In order to reboot a bbb send a POST according to this pattern:
```
curl --header "Content-Type: application/json" -k --request POST --data "{\"ip\":\"${1}\"}" https://${2}/bbb-daemon/api/node/reboot

```
where: 

`https://${2}/bbb-daemon/api/` is the api address and may change in the future.

`${1}` is the target ip address.

`${2}` is the CONS server ip address.


# Docker
To launch the server application on swarm enter the directory `docker/swarm/ ` and run `sudo docker stack deploy -c docker-swarm.yml bbb-daemon`. To remove the containers `sudo docker stack rm bbb-daemon`.

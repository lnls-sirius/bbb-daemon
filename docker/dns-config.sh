#!/usr/bin/env bash

ping 10.0.6.70

if [ "$DNS_USE_DNS_PVS" == "YES" ]; then
	echo "nameserver $DNS_SERVER_1" > /etc/resolv.conf
	echo "nameserver $DNS_SERVER_2" >> /etc/resolv.conf

	echo "search abtlus.org.br" >> /etc/resolv.conf

	cat /etc/resolv.conf
	echo "DNS configured !"
else
	echo "/etc/resolv.conf:"
	cat /etc/resolv.conf
	echo "DNS Default !"
fi

echo "Ping www.google.com"
ping www.google.com

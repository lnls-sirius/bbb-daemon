#echo "nameserver $SERVER_IP_ADDR" > /etc/resolv.conf

echo "nameserver $DNS_SERVER_1" > /etc/resolv.conf
echo "nameserver $DNS_SERVER_2" >> /etc/resolv.conf

echo "search abtlus.org.br" >> /etc/resolv.conf


cat /etc/resolv.conf
echo "Ping www.google.com"
ping www.google.com

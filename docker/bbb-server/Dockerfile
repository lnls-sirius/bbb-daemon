FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

WORKDIR /root/

RUN git clone https://github.com/lnls-sirius/bbb-daemon.git 
RUN apt-get -y update 

RUN cd /root/bbb-daemon/server && make -C /root/bbb-daemon/server install

WORKDIR /root/bbb-daemon
RUN cd /root/bbb-daemon/server
CMD ["sh", "-c", "/root/bbb-daemon/server/run.sh"]

EXPOSE 9877 9876 4850 

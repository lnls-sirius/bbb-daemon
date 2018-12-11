FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

WORKDIR /root/

RUN git clone https://github.com/lnls-sirius/bbb-daemon.git 

WORKDIR /root/bbb-daemon/server
RUN make -C /root/bbb-daemon/server install

WORKDIR /root/bbb-daemon
CMD ["sh", "-c", "/root/bbb-daemon/docker/bbb-server/run.sh"]

EXPOSE 9877 9876 4850 
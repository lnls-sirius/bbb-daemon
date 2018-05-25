FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

ENV REDIS_SERVER_IP 10.0.6.70
ENV REDIS_SERVER_PORT 6379
ENV COM_PORT 6789

EXPOSE $REDIS_SERVER_PORT
EXPOSE $COM_PORT
EXPOSE 9876
EXPOSE 9877

WORKDIR /root/

COPY requirements.txt ./

RUN apt-get update && pip3 install --no-cache-dir -r requirements.txt

RUN cd /root/
RUN git clone https://github.com/vishnubob/wait-for-it.git
RUN git clone https://github.com/lnls-sirius/bbb-daemon.git

RUN cd /root/bbb-daemon/docker

CMD ["sh", "-c", "/root/bbb-daemon/docker/wait.sh"]

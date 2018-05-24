FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

ENV REDIS_SERVER_IP 10.0.6.70
ENV REDIS_SERVER_PORT 6379

ENV DNS_SERVER_1 8.8.8.8
ENV DNS_SERVER_2 8.8.4.4

EXPOSE $REDIS_SERVER_PORT

WORKDIR /root/

COPY requirements.txt ./
COPY dns-config.sh ./

RUN sh -c /root/dns-config.sh
RUN pip install --no-cache-dir -r requirements.txt

RUN cd /root/
RUN git pull https://github.com/vishnubob/wait-for-it.git
RUN git pull https://github.com/lnls-sirius/bbb-daemon.git

RUN cd /root/bbb-daemon/docker

CMD ["sh", "-c", "/root/bbb-daemon/docker/wait.sh"]

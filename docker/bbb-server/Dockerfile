FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

WORKDIR /root/

COPY requirements.txt ./

RUN apt-get update && pip3 install --no-cache-dir -r requirements.txt

RUN cd /root/

RUN git clone https://github.com/vishnubob/wait-for-it.git
RUN git clone https://github.com/lnls-sirius/bbb-daemon.git

RUN cd /root/bbb-daemon/docker/bbb-server/

CMD ["sh", "-c", "/root/bbb-daemon/docker/bbb-server/wait.sh"]

EXPOSE \
    20 \
    21 \
    6789 \
    9876 \
    1026 \
    4850 \
    3000-3010 \
    9877 \
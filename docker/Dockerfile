FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

ENV SERVER_IP_ADDR 10.0.6.70

EXPOSE 6379

WORKDIR /root/

RUN ping www.google.com

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


#RUN pip install redis
#RUN pip install gitdb
#RUN pip install gitpython

RUN cd /root/
RUN git pull https://github.com/vishnubob/wait-for-it.git
RUN git pull https://github.com/lnls-sirius/bbb-daemon.git

RUN cd /root/bbb-daemon/docker

CMD ["sh", "-c", "/root/bbb-daemon/docker/wait.sh"]

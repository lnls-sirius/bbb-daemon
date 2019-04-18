FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

USER root

RUN useradd            \
    -s /bin/bash       \
    -U wsgi

RUN usermod            \
    -aG sudo wsgi

RUN mkdir /wsgi && chmod -R 777 /wsgi
WORKDIR /wsgi

RUN apt-get -y update
RUN apt-get -y install \
    less               \
    vim                \
    tree               \
    apache2            \
    apache2-dev

RUN pip install                         \
    mod_wsgi==4.6.5                     \
    Flask==1.0.2                        \
    Flask-RESTful==0.3.6                \
    Flask-Cors==3.0.7                   \
    redis==2.10.6                       \
    sip==4.19.8                         \
    msgpack==0.5.6

RUN mkdir -p /wsgi/bbb-daemon

COPY host         /wsgi/bbb-daemon/host
COPY common       /wsgi/bbb-daemon/common
COPY server       /wsgi/bbb-daemon/server
COPY wait-for-it  /wsgi/bbb-daemon/wait-for-it

RUN tree -d

WORKDIR /wsgi/bbb-daemon/server
CMD ["sh", "-c", "/wsgi/bbb-daemon/server/run.sh"]

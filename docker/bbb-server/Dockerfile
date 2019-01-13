FROM python:3-stretch

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

USER root

RUN useradd -s /bin/bash -g root -G sudo wsgi
RUN mkdir /wsgi && chmod -R 777 /wsgi
WORKDIR /wsgi

RUN apt-get -y update
RUN apt-get -y install less nano apache2 apache2-dev

RUN pip install virtualenv==16.0.0
RUN git clone https://github.com/lnls-sirius/bbb-daemon.git
RUN cd bbb-daemon && git clone https://github.com/vishnubob/wait-for-it.git && mkdir log && \
    cd server && \
    virtualenv bbb-daemon-virtualenv && \
    . bbb-daemon-virtualenv/bin/activate && \
    pip install -r install/requirements.txt && deactivate
RUN chown -R wsgi /wsgi

USER wsgi
WORKDIR /wsgi/bbb-daemon/server
CMD ["sh", "-c", "/wsgi/bbb-daemon/server/run.sh"]
FROM python:3-strech

EXPOSE 6379

WORKDIR /root/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

RUN cd /root/
RUN git pull https://github.com/lnls-sirius/bbb-daemon.git
RUN cd /root/bbb-daemon/server

CMD [./run.sh]


#You can then build and run the Docker image:

#$ docker build -t my-python-app .
#$ docker run -it --rm --name my-running-app my-python-app


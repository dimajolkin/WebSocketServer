FROM python:2.7

RUN pip install tornado==4.1
RUN pip install redis
RUN pip install daemonize
RUN apt install -y git

#RUN git clone https://github.com/dimajolkin/WebSocketServer.git /root/daemon
RUN mkdir /root/daemon
WORKDIR /root/daemon

ADD ./ /root/daemon

VOLUME /var/log:/var/log

EXPOSE 8888

RUN touch /var/log/pythonDaemon.log

#CMD cd /root/daemon &&\
#    echo "run service \n" &&\
#    python /root/daemon/run.py

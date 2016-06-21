FROM python:2.7

RUN pip install tornado==4.1
RUN pip install redis
RUN apt install -y git
RUN git clone https://github.com/dimajolkin/WebSocketServer.git /root/daemon

CMD cd /root/daemon && git pull -f origin master &&\
    echo "run service \n" &&\
    python /root/daemon/run.py >> /var/log/pythonDaemon.log

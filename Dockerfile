FROM python:2.7

RUN pip install tornado==4.1
RUN pip install redis
RUN apt install -y git
RUN git clone https://github.com/dimajolkin/WebSocketServer.git /root/daemon

CMD cd /root/daemon && git pull origin master
CMD python /root/daemon/wsServer.py >> /var/log/pythonDaemon.log

import json
import logging
import os
import socket

import redis
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

# from server import Storage, User
import tornado

from server.UserCollection import UserCollection
from server.Storage import Storage
from server.handlers.UserHandler import UserHandler
from server.listener.TaskListener import TaskListener
from server.listener.NoticeListener import NoticeListener


class Server:
    def __init__(self):

        config_file_path = "{0}/config.json".format(os.getcwd())
        self.config = json.loads(file(config_file_path).read())

        if not self.config:
            print "Config not fount"
            exit()

        if 'log' in self.config:
            logging.basicConfig(filename=self.config['log']['file'], level=logging.DEBUG)

        if 'redis' not in self.config:
            print "Redis config not found!!"
            exit()

        if 'log' in self.config:
            logging.basicConfig(filename=self.config['log']['file'], level=logging.DEBUG)

        self.redis_config = self.config['redis']

        self.redis = redis.Redis(
            host=self.redis_config['host'],
            port=self.redis_config['port'],
            db=self.redis_config['db']
        )

        self.users = UserCollection()

    def app(self):
        UserHandler.storage = Storage(self.redis)
        UserHandler.users_collection = self.users
        NoticeListener.users = self.users

        application = tornado.web.Application([
            (r"{0}".format(self.config['url']), UserHandler),
            # (r'/', WebHandler)
        ])

        NoticeListener(self.redis, ["notice:NOTIF:*"]).start()

        TaskListener(self.redis, ["__key*__:expired"]).start()

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(self.config['port'])
        myIP = socket.gethostbyname(socket.gethostname())
        print '*** Websocket Server Started at {0}'.format(myIP)
        print self.config
        tornado.ioloop.IOLoop.instance().start()
        pass

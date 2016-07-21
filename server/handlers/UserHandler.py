import logging

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

import json

from server import Storage


class UserHandler(tornado.websocket.WebSocketHandler):
    storage = None
    user_key = None

    users_collection = None

    def __init__(self, application, request, **kwargs):
        super(UserHandler, self).__init__(application, request, **kwargs)
        self.user_key = None
        self.token = None
        if not self.storage:
            raise Exception("WebSocketHandler empty storage")

    def open(self):
        self.users_collection.append(self)
        self.log("--> connection countHandlers:{0}".format(self.users_collection.length()))

    def on_message(self, message):
        data = json.loads(message)
        if 'token' in data:
            self.token = data['token']

            self.user_key = self.storage.pop('notice:AUTH:{0}'.format(self.token))
            if self.user_key:
                self.log("user auth {0}", [self.user_key])

                self.storage.set('notice:STATUS:{0}'.format(self.user_key), 1)
                self.write_message({"type": "ok", "content": "User authorization"})
            else:
                self.write_message({"type": "error", "code": 401, "content": "User not authorization!"})

        if 'type' in data and data['type'] == 'life':
            if self.user_key:
                self.write_message({"type": "ok"})
            else:
                self.write_message({"type": "error"})

    def on_close(self):
        self.users_collection.remove(self)
        self.log(" --> close countHandlers:{0}", [self.users_collection.length()])

    def check_origin(self, origin):
        return True

    def get_storage(self):
        if not isinstance(self.storage, Storage):
            raise Exception("Storage not instance of Storage")
        return self.storage

    def log(self, log, params=None):
        if params is None:
            params = []

        print logging.debug(log.format(params))

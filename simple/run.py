import json
import os
import logging
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import redis
import threading

from redis.exceptions import ConnectionError


class NoticeListener(threading.Thread):
    handlers = []
    redis = None

    def attach_handler(self, handler):
        self.handlers.append(handler)

    def detach_handler(self, handler):
        self.handlers.remove(handler)

    def send_by_user(self, user_id, message):
        for handler in self.handlers:
            if isinstance(handler, WebSocketHandler):
                if handler.user_profile_id == user_id:
                    handler.write_message({'id': json.loads(message)})

    def get(self, key):
        return self.redis.get(key)

    def pop(self, key):
        value = self.redis.get(key)
        if value:
            self.redis.delete(key)
        return value

    def set(self, key, value):
        self.redis.set(key, value)

    def __init__(self, redis, channels):
        """

        :type redis: redis.client.Redis
        :type handler: WebSocketHandler
        """
        self.redis = redis
        threading.Thread.__init__(self)

        self.pubsub = redis.pubsub()
        self.pubsub.psubscribe(channels)

    def work(self, item):
        logging.debug("begin message:")
        logging.debug(item['channel'])
        logging.debug(item['data'])
        logging.debug("end message")

    def close(self):
        self.pubsub.unsubscribe()

    def run(self):
        for item in self.pubsub.listen():
            self.work(item)
            try:
                user_id = item['channel'].split(':')[1]
                self.send_by_user(user_id, item['data'])

            except Exception:
                pass


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    storage = None

    def __init__(self, application, request, **kwargs):
        super(WebSocketHandler, self).__init__(application, request, **kwargs)
        self.user_profile_id = None
        self.token = None
        if not self.storage:
            raise Exception("WebSocketHandler empty storage")

    def open(self):
        self.storage.attach_handler(self)
        logging.debug("--> connection countHandlers:{0}".format(len(self.storage.handlers)))

    def on_message(self, message):
        data = json.loads(message)
        if 'token' in data:
            self.token = data['token']
            self.user_profile_id = storage.pop('notice:AUTH:{0}'.format(self.token))
            if self.user_profile_id:
                logging.debug("user auth {0}".format(self.user_profile_id))
                self.storage.set('notice:STATUS:{0}'.format(self.user_profile_id), 1)
                self.write_message({"type": "ok", "content": "User authorization"})
            else:
                self.write_message({"type": "error", "code": 401, "content": "User not authorization!"})

        if 'type' in data and data['type'] == 'life':
            if self.user_profile_id:
                self.write_message({"type": "ok"})
            else:
                self.write_message({"type": "error"})

    def on_close(self):
        self.storage.detach_handler(self)
        logging.debug(" --> close countHandlers:{0}".format(len(self.storage.handlers)))

    def check_origin(self, origin):
        return True


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("web/index.html", title="My title", items=items)


if __name__ == "__main__":

    config_file_path = "{0}/config.json".format(os.getcwd())
    config = json.loads(file(config_file_path).read())

    if not config:
        logging.debug("Config not fount")
        exit()

    if 'redis' not in config:
        logging.debug("Redis config not found!!")
        exit()

    if 'log' in config:
        logging.basicConfig(filename=config['log']['file'], level=logging.DEBUG)

    redisConfig = config['redis']

    try:
        redis = redis.Redis(
            host=redisConfig['host'],
            port=redisConfig['port'],
            db=redisConfig['db'])

        storage = NoticeListener(redis, ["notice:NOTIF:*"])
        storage.start()

        # init static variable
        WebSocketHandler.storage = storage

    except ConnectionError:
        logging.debug("Redis error connect: checked config.json")
        exit()

    try:
        application = tornado.web.Application([
            (r"{0}".format(config['url']), WebSocketHandler),
            (r'/', IndexHandler)
        ])

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(config['port'])
        myIP = socket.gethostbyname(socket.gethostname())
        logging.debug('*** Websocket Server Started at {0}'.format(myIP))
        tornado.ioloop.IOLoop.instance().start()
    except Exception as ex:
        tornado.ioloop.IOLoop.instance().stop()
        logging.error(ex)
        logging.error("Stop WebSocketServer")

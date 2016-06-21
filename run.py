import json
import os

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import redis
import threading

from redis.exceptions import ConnectionError


class RedisListener(threading.Thread):
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
        print(item['channel'], ":", item['data'])

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
    user_profile_id = None
    token = None

    def open(self):
        storage.attach_handler(self)
        print("new connection {0}".format(len(storage.handlers)))

    def on_message(self, message):
        data = json.loads(message)
        if 'token' in data:
            self.token = data['token']
            self.user_profile_id = storage.get('AUTH:{0}'.format(self.token))
            if self.user_profile_id:
                storage.set('STATUS:{0}'.format(self.user_profile_id), 1)

            else:
                self.write_message({"type": "error", "code": 401, "content": "User not authorization!"})
                return

    def on_close(self):
        storage.detach_handler(self)
        print('connection closed')

    def check_origin(self, origin):
        return True


storage = None

if __name__ == "__main__":

    config_file_path = "{0}/config.json".format(os.getcwd())
    config = json.loads(file(config_file_path).read())

    if not config:
        print "Config not fount"
        exit()

    if 'redis' not in config:
        print ("Redis config not found!!")
        exit()

    redisConfig = config['redis']

    try:
        redis = redis.Redis(
            host=redisConfig['host'],
            port=redisConfig['port'],
            db=redisConfig['db'])
        storage = RedisListener(redis, ["NOTIF:*"])
        storage.start()
    except ConnectionError:
        print "Redis error connect: checked config.json"

    application = tornado.web.Application([
        (r"{0}".format(config['url']), WebSocketHandler),
    ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.instance().start()

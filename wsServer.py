import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import redis
import threading


class RedisListener(threading.Thread):
    def __init__(self, r, handler, channels):
        """

        :type handler: WebSocketHandler
        """
        threading.Thread.__init__(self)
        self.redis = r
        self.handler = handler
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)

    def work(self, item):
        print item['channel'], ":", item['data']

    def close(self):
        self.pubsub.unsubscribe()

    def run(self):
        for item in self.pubsub.listen():
            self.handler.write_message(item['data'])
            self.work(item)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    app = None

    def open(self):
        self.app = RedisListener(redis.Redis(), self, ["564"])
        self.app.start()
        print "new connection"

    def on_message(self, message):
        self.write_message(message)

    def on_close(self):
        if self.app is not None:
            self.app.close()

        print 'connection closed'

    def check_origin(self, origin):
        return True


application = tornado.web.Application([
    (r'/ws', WebSocketHandler),
])

if __name__ == "__main__":
    r = redis.Redis()

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print  '*** Websocket Server Started at %s***' % myIP
    tornado.ioloop.IOLoop.instance().start()

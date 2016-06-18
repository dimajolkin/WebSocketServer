import redis
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import redis
import threading

class Listener(threading.Thread):

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
            message = item['data']
            if item['data'] == "KILL":
                self.close()
                print self, "unsubscribed and finished"
                break
            else:
                self.handler.write_message(item)
                self.work(item)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.client = Listener(redis.Redis(), self, ["564"])
        self.client.start()
        print "new connection"

    def on_message(self, message):
        print 'message received:  %s' % message
        # Reverse Message and send it back
        print 'sending back message: %s' % message[::-1]
        self.write_message('Hello Word')

    def on_close(self):
        self.client.close()
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

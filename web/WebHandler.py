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

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("views/index.html", title="My title", items=items)

import json
from multiprocessing import synchronize

from server.handlers.UserHandler import UserHandler
import logging

class UserCollection:
    def __init__(self):
        self.users = []
        pass

    def status(self):
        print "users count {0}".format(self.users.__len__())

    def append(self, user):
        if isinstance(user, UserHandler):
            self.users.append(user)
        self.status()

    def remove(self, user):
        self.users.remove(user)
        self.status()

    def send(self, user_key, message):
        """
        - send msg for all users handlers
        :param user_key:
        :param message:
        :return:
        """
        logging.debug("send:")
        for handler in self.users:
            logging.debug("send: --> {0}".format(handler.user_key))
            if isinstance(handler, UserHandler):
                if handler.user_key == user_key:
                    logging.debug("---> send for {0}".format(user_key))
                    handler.write_message({'id': json.loads(message)})

    def length(self):
        return self.users.__len__()

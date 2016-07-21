import threading
import logging

from server.UserCollection import UserCollection


class NoticeListener(threading.Thread):
    users = None

    def get_users(self):
        """"
        :return UserCollection
        """
        if not isinstance(self.users, UserCollection):
            raise Exception("NoticeListener link in UserCollection not found")

        return self.users

    def __init__(self, redis, channels):
        """

        :type redis: redis.client.Redis
        :type channels: WebSocketHandler
        """
        self.redis = redis
        threading.Thread.__init__(self)

        self.pubsub = redis.pubsub()
        self.pubsub.psubscribe(channels)

    def run(self):
        for item in self.pubsub.listen():
            try:
                logging.debug("content: " + str(item))

                user_key = item['channel'].split(':')[2]
                logging.debug("---> {0}".format(user_key))
                self.get_users().send(user_key, item['data'])

            except Exception as ex:
                logging.debug("Error: " + ex.message)

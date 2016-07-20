import logging
import threading


class TaskListener(threading.Thread):
    users = None

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
        print "event message:"
        print item['data']
        print "end message"

    def run(self):
        for item in self.pubsub.listen():
            try:
                task = Task(item)
                logging.debug("event" + str(item))

                if task.is_task():
                    pattern = 'notice:reminder:tasks:job:{0}:*'.format(task.get_key())
                    keys = self.redis.keys(pattern)
                    logging.debug("send msg: " + str(keys))
                    for key in keys:
                        user_key = key.split(':')[-1]
                        logging.debug(key)
                        notice = self.redis.get(key)
                        self.redis.publish('notice:NOTIF:{0}'.format(user_key), notice)

                    # self.redis.delete(keys)
                else:
                    print "not task:"
                    print item

            except Exception as ex:
                print ex.message


class Task:
    KEY = 'notice:reminder:tasks:list:'

    def __init__(self, data):
        self.data = data

    def is_task(self):
        """
        is task
        :return:
        """
        return str(self.data['data']).find(self.KEY) == 0

    def get_key(self):
        """
        get key <name>:<time>
        :return:
        """
        return str(self.data['data']).replace(self.KEY, '')

    def get_name(self):
        """
        get name task
        :return:
        """
        return self.get_key().split(':')[-2]


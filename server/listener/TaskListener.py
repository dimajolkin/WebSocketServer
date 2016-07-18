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
                #notice:tasks:list:<number>
                if item['channel'] == '__keyevent@2__:expired':
                    number_task = item['data'].split(':')[-1]
                    print "number task: {0}".format(number_task)
                    for key in self.redis.keys('notice:tasks:job:{0}:*'.format(number_task)):
                        user_key = key.split(':')[-1]
                        print user_key
                        print self.redis.get(key)
                        pass

                    print number_task

            except Exception as ex:
                print ex.message
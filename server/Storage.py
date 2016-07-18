class Storage:
    def __init__(self, redis):
        """

        :param redis.client.Redis redis :
        """
        self.redis = redis

    def pop(self, key):
        """
        - get and delete key
        :param str key:
        :return:
        """
        value = self.redis.get(key)
        if value:
            self.redis.delete(key)
        return value

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

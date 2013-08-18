import redis
from openrunlog import constants

if __name__ == '__main__':
    r = redis.StrictRedis(host='localhost', port=6379)
    r.rpush(constants.calculate_streaks, 'all')

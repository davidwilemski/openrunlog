
import tornadoredis
from openrunlog import models, cache

if __name__ == '__main__':
    r = tornadoredis.Client()
    r.connect()

    for user in models.User.objects():
        cache.invalidate(r, user)

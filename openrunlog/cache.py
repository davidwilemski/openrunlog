
import pickle
from tornado import gen


def key(k):
    return 'orl.cache.{}'.format(k)


@gen.coroutine
def get(r, uid):
    u = yield gen.Task(r.get, key(uid))
    if u:
        u = pickle.loads(u)
    raise gen.Return(u)


@gen.coroutine
def send(r, user):
    p = pickle.dumps(user)
    yield gen.Task(r.set, key(user.id), p)
    yield gen.Task(r.set, key(user.email), p)
    yield gen.Task(r.set, key(user.url), p)


@gen.coroutine
def invalidate(r, user):
    yield gen.Task(r.delete, key(user.id))
    yield gen.Task(r.delete, key(user.email))
    yield gen.Task(r.delete, key(user.url))

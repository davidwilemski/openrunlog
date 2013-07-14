import env
import mongoengine

from openrunlog import models


def rebuild_indexes():
    collection_user = models.User._get_collection()
    collection_run = models.Run._get_collection()

    collection_user.update({}, {"$unset": {"_types": 1}}, multi=True)
    collection_run.update({}, {"$unset": {"_types": 1}}, multi=True)

    # Confirm extra data is removed
    count = collection_user.find({'_types': {"$exists": True}}).count()
    assert count == 0
    count = collection_run.find({'_types': {"$exists": True}}).count()
    assert count == 0

    # Remove indexes
    info = collection_user.index_information()
    indexes_to_drop = [key for key, value in info.iteritems()
                       if '_types' in dict(value['key'])]
    for index in indexes_to_drop:
        collection_user.drop_index(index)

    info = collection_run.index_information()
    indexes_to_drop = [key for key, value in info.iteritems()
                       if '_types' in dict(value['key'])]
    for index in indexes_to_drop:
        collection_run.drop_index(index)

    # Recreate indexes
    models.User.ensure_indexes()
    models.Run.ensure_indexes()


def fix_reference_fields():
    for r in models.Run.objects:
        r._mark_as_changed('user')
        r.save()

    for w in models.Week.objects:
        w._mark_as_changed('user')
        w.save()

    for g in models.Group.objects:
        g._mark_as_changed('admins')
        g._mark_as_changed('members')
        g.save()


def flush_redis_keys():
    import redis
    r = redis.StrictRedis(host='localhost', port=6379)
    r.flushdb()

if __name__ == '__main__':
    config = env.prefix('ORL_')
    if config['debug'] == 'True':
        config['debug'] = True
    else:
        config['debug'] = False

    mongoengine.connect(
        config['db_name'],
        host=config['db_uri'])

    models.User.ensure_indexes()
    models.Run.ensure_indexes()
    rebuild_indexes()

    fix_reference_fields()

    flush_redis_keys()

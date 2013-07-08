
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from concurrent import futures
import env
import logging
import tarfile
import setproctitle
from tornado import ioloop, gen, process
import tornadoredis
import time

pool = futures.ProcessPoolExecutor(max_workers=5)
daily_key = 'orl.backups.daily'
onchange_key = 'orl.backups.onchange'

redis = tornadoredis.Client()
redis.connect()


def compress_file(filename):
    newfile = '{}.tar.bz2'.format(filename)
    with tarfile.open(newfile, "w:gz") as tar:
        tar.add(filename)
    return newfile


def get_config():
    config = env.prefix('ORL_')
    if config['debug'] == 'True':
        config['debug'] = True
    else:
        config['debug'] = False
    return config


def get_s3_bucket(config):
    bucketname = config['backup_bucket']
    s3key = config['s3_key']
    s3secret = config['s3_secret']
    conn = S3Connection(s3key, s3secret)
    b = conn.get_bucket(bucketname)
    return b


def gen_key(keyname, bucket):
    k = Key(bucket)
    k.key = keyname
    return k


def upload_file(config, filename):
    print 'uploading', filename
    b = get_s3_bucket(config)
    k = gen_key(filename, b)
    k.set_contents_from_filename(filename)
    return k.key


def delete_file(config, filename):
    print 'deleting', filename
    b = get_s3_bucket(config)
    k = gen_key(filename, b)
    k.delete()


@gen.coroutine
def cleanup(filename):
    args = ['rm', '-rf', filename]
    print ' '.join(args)
    delprocess = process.Subprocess(args)
    yield gen.Task(delprocess.set_exit_callback)


@gen.coroutine
def dump_mongodb_to_s3(config):
    logging.debug('starting dumping')
    filename = "/tmp/orl_mongo_backup_{}".format(time.time())
    args = ['mongoctl', 'dump', config['db_uri'], '-o', filename]
    mongoctl = process.Subprocess(args)
    yield gen.Task(mongoctl.set_exit_callback)
    logging.debug('finished dumping')
    print 'finished dumping print'
    compressed_filename = yield pool.submit(compress_file, filename)
    logging.debug('compressed file')

    logging.debug('uploading file')
    backupkey = yield pool.submit(upload_file, config, compressed_filename)
    logging.debug('uploaded file')

    yield cleanup(filename)
    yield cleanup(compressed_filename)
    logging.debug('deleted local file')

    raise gen.Return(backupkey)


@gen.coroutine
def daily():
    config = get_config()
    backupkey = yield dump_mongodb_to_s3(config)
    logging.debug('backed up to {}'.format(backupkey))
    print('backed up to {}'.format(backupkey))
    yield gen.Task(redis.rpush, daily_key, backupkey)

    numbackups = yield gen.Task(redis.llen, daily_key)
    print 'number backups: ', numbackups
    while numbackups > 5:
        logging.debug('cleaning up old backups')
        oldbackupkey = yield gen.Task(redis.lpop, daily_key)
        yield pool.submit(delete_file, config, oldbackupkey)
        numbackups -= 1

    raise gen.Return()


def main():
    logging.info('starting workers.backup')
    ioloop.PeriodicCallback(daily, 1000*60*60*24).start()


if __name__ == '__main__':
    config = get_config()

    logging.basicConfig(level=logging.INFO)
    setproctitle.setproctitle('orl.workers.backup')
    main()
    ioloop.IOLoop.instance().start()

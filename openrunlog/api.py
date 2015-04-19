import collections
import functools

import dateutil
from tornado import gen

import base
import models

REQUIRED = object()  # sentinel for a required field

Field = collections.namedtuple('Field', 'name default transform')


class APIException(Exception):
    def __str__(self):
        return self.message


def one_of(a, b, value):
    return a == value or b == value


def exclusive(a, b, value):
    return (a != value) != (b != value)


@gen.coroutine
def get_api_user(request, redis):
    api_key = request.headers.get('api_key', None)
    if api_key is None:
        raise APIException('missing header "api_key"')

    user = yield models.get_user_by_api_key(api_key)
    if user is None:
        raise APIException('Invalid API Key')
    raise gen.Return(user)


def api_method(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        user = yield get_api_user(self.request, self.redis)
        params = {'user': user}

        # first param of api methods should be the user's url
        user_url = args[0]
        if params['user'].url != user_url:
            raise APIException(
                'you do not have permission to add a run for /{}'.format(
                    user_url))

        for field in self.fields:
            if field.default is REQUIRED:
                value = self.get_argument(field.name)
            else:
                value = self.get_argument(field.name, field.default)

            try:
                params[field.name] = field.transform(value)
            except ValueError:
                raise APIException(
                    'Field "{}" was incorrectly formatted'.format(field.name))
        kwargs['params'] = params
        fn(self, *args, **kwargs)
    return wrapper


class AddRunHandler(base.API):
    fields = [Field(name='date',
                    default=REQUIRED,
                    transform=dateutil.parser.parse),
              Field(name='distance',
                    default=REQUIRED,
                    transform=float),
              Field(name='time',
                    default='0:00',
                    transform=models.time_to_seconds),
              Field(name='pace',
                    default='0:00',
                    transform=models.time_to_seconds),
              Field(name='notes',
                    default='',
                    transform=str), ]

    @gen.coroutine
    @api_method
    def post(self, user_url, params=None):
        if params is None:
            raise APIException('no params found')

        time, pace = params['time'], params['pace']
        if not one_of(time, pace, 0) or not exclusive(time, pace, 0):
            raise APIException('One of "time" or "pace" is required: {}'.format(params))

        run = models.Run(**params)
        run.save()
        self.finish(run.public_dict())

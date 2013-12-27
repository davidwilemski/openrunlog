
import json
import logging

import requests
from tinyfeedback.helper import send_once as tf


def format_body(run):
    body = {
            'message': run.notes,
            'workout': {
                'duration': run.time,
                'distance': {
                    'value': run.distance ,
                    'units': 'miles',
                },
                'activity_type': 'running',
                'completed_at': run.date.isoformat(),
            }
    }
    return json.dumps(body)


def export_run(run):
    url = 'https://api.dailymile.com/entries.json?oauth_token={}'.format(run.user.dailymile_token)

    body = format_body(run)

    headers = {
            'Content-Type': 'application/json'
    }

    if run.exported_to_dailymile:
        return

    # TODO check that run is not in the future

    response = requests.post(url, data=body, headers=headers)

    if response.status_code == 201:
        run.exported_to_dailymile = True
        run.save()
        tf('openrunlog', {'users.dailymile.run.sent': 1})
    else:
        logging.error(response)
        logging.error(response.json())
        raise Exception

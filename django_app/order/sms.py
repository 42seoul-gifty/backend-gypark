import requests
import time
import base64
import hmac
import hashlib
import json

from django.conf import settings


def send_sms(send_from, **kwargs):
    timestamp = str(int(time.time() * 1000))

    url_path = f'/sms/v2/services/{settings.NCLOUD_SERVICE_ID}/messages'
    url = 'https://sens.apigw.ntruss.com' + url_path

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': settings.NCLOUD_ACCESS_KEY,
    }
    headers['x-ncp-apigw-signature-v2'] = make_signature('POST', url_path, timestamp)

    kwargs['from'] = send_from
    kwargs['type'] = 'SMS'

    return requests.post(url, data=json.dumps(kwargs), headers=headers)


def	make_signature(method, url, timestamp):
    access_key = settings.NCLOUD_ACCESS_KEY
    secret_key = bytes(settings.NCLOUD_SECRET, 'UTF-8')

    message = '\n'.join([
        f'{method} {url}',
        timestamp,
        access_key
    ])
    message = bytes(message, 'UTF-8')
    signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signing_key

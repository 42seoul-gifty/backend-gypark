import requests
import time
import base64
import hmac
import hashlib
import json
from urllib.parse import urlparse

from django.conf import settings


class NCloudRequest:
    def __init__(self, url, method, **kwargs):
        self.url = url
        self.parsed = urlparse(self.url)
        self.method = method
        self.kwargs = kwargs
        self.headers = kwargs.pop('headers', {})

    def excute(self):
        timestamp = str(int(time.time() * 1000))
        self.headers.update({
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': settings.NCLOUD_ACCESS_KEY,
        })
        self.headers['x-ncp-apigw-signature-v2'] = self._make_signature(timestamp)

        method = getattr(requests, self.method.lower())
        return method(self.url, headers=self.headers, **self.kwargs)

    def _make_signature(self, timestamp):
        access_key = settings.NCLOUD_ACCESS_KEY
        secret_key = bytes(settings.NCLOUD_SECRET, 'UTF-8')

        path_with_params = self.url[self.url.index(self.parsed.path):]
        message = '\n'.join([
            f'{self.method} {path_with_params}',
            timestamp,
            access_key
        ])
        message = bytes(message, 'UTF-8')
        signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        return signing_key


def send_sms(**kwargs):
    url = ('https://sens.apigw.ntruss.com'
          f'/sms/v2/services/{settings.NCLOUD_SERVICE_ID}/messages')
    kwargs['type'] = 'SMS'

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    return NCloudRequest(url, 'POST', data=json.dumps(kwargs), headers=headers).excute()


def search_sms_request(request_id):
    url = ('https://sens.apigw.ntruss.com'
          f'/sms/v2/services/{settings.NCLOUD_SERVICE_ID}/messages?requestId={request_id}')
    return NCloudRequest(url, 'GET').excute()


import os
import json
import logging
import requests

from .SyncthingError import SyncthingError
from .Utilities import string_types

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 10.0

class BaseAPI(object):
    """ Placeholder for HTTP REST API URL prefix. """

    prefix = ''

    def __init__(
            self,
            api_key,
            host='localhost',
            port=8384,
            timeout=DEFAULT_TIMEOUT,
            is_https=False,
            ssl_cert_file=None
    ):
        if ssl_cert_file:
            if not os.path.exists(ssl_cert_file):
                raise SyncthingError('ssl_cert_file does not exist at location, %s' % ssl_cert_file)

        self.api_key = api_key
        self.host = host
        self.is_https = is_https
        self.port = port
        self.ssl_cert_file = ssl_cert_file
        self.timeout = timeout
        self.verify = True if ssl_cert_file or is_https else False
        self._headers = {
            'X-API-Key': api_key
        }
        self.url = '{proto}://{host}:{port}'.format(proto='https' if is_https else 'http', host=host, port=port)
        self._base_url = self.url + '{endpoint}'

    def get(
            self,
            endpoint,
            data=None,
            headers=None,
            params=None,
            return_response=False,
            raw_exceptions=False
    ) -> requests.Response | str | dict:
        endpoint = self.prefix + endpoint
        return self._request('GET', endpoint, data, headers, params, return_response, raw_exceptions)

    def post(
            self,
            endpoint,
            data=None,
            headers=None,
            params=None,
            return_response=False,
            raw_exceptions=False
    ) -> requests.Response | str | dict:
        endpoint = self.prefix + endpoint
        return self._request('POST', endpoint, data, headers, params, return_response, raw_exceptions)

    def _request(
            self,
            method,
            endpoint,
            data=None,
            headers=None,
            params=None,
            return_response=False,
            raw_exceptions=False
    ) -> requests.Response | str | dict:
        method = method.upper()

        endpoint = self._base_url.format(endpoint=endpoint)

        if method not in ('GET', 'POST', 'PUT', 'DELETE'):
            raise SyncthingError('unsupported http verb requested, %s' % method)

        if data is None:
            data = {}
        assert isinstance(data, string_types) or isinstance(data, dict)

        if headers is None:
            headers = {}
        assert isinstance(headers, dict)

        headers.update(self._headers)

        try:
            response = requests.request(
                method,
                endpoint,
                data=json.dumps(data),
                params=params,
                timeout=self.timeout,
                cert=self.ssl_cert_file,
                headers=headers
            )

            if not return_response:
                response.raise_for_status()

        except requests.RequestException as e:
            if raw_exceptions:
                raise e
            raise SyncthingError('http request error', e)

        else:
            if return_response:
                return response

            if response.status_code != requests.codes.ok:
                logger.error('%d %s (%s): %s', response.status_code, response.reason, response.url, response.text)
                return response

            if 'json' in response.headers.get('Content-Type', 'text/plain').lower():
                json_data = response.json()
            else:
                content = response.content.decode('utf-8')
                if content and content[0] == '{' and content[-1] == '}':
                    json_data = json.loads(content)
                else:
                    return content

            if isinstance(json_data, dict) and json_data.get('error'):
                api_err = json_data.get('error')
                raise SyncthingError(api_err)
            return json_data

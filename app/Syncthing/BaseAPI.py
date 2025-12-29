import os
import json
import logging
import requests

from requests import Response

from .SyncthingException import SyncthingException

DEFAULT_TIMEOUT = 10

class BaseAPI(object):
    """ Placeholder for HTTP REST API URL prefix. """

    prefix = ''

    def __init__(
        self,
        api_key: str,
        host: str = 'localhost',
        port: int = 8384,
        timeout: int = DEFAULT_TIMEOUT,
        is_https: bool = False,
        ssl_cert_file: str | None = None
    ):
        if ssl_cert_file:
            if not os.path.exists(ssl_cert_file):
                raise SyncthingException('ssl_cert_file does not exist at location, %s' % ssl_cert_file)

        self.api_key = api_key
        self.host = host
        self.port = port
        self.timeout = timeout
        self.is_https = is_https
        self.ssl_cert_file = ssl_cert_file
        self.verify = True if ssl_cert_file or is_https else False
        self._headers = {
            'X-API-Key': api_key
        }
        self.url = '{proto}://{host}:{port}'.format(proto='https' if is_https else 'http', host=host, port=port)
        self._base_url = self.url + '{endpoint}'
        self.logger = logging.getLogger(__name__)

    def get(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        return_response: bool = False,
        raw_exceptions: bool = False
    ) -> Response | int | str | dict | list:
        return self._request('GET', self.prefix + endpoint, data, headers, params, return_response, raw_exceptions)

    def post(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        return_response: bool = False,
        raw_exceptions: bool = False
    ) -> Response | int | str | dict | list:
        return self._request('POST', self.prefix + endpoint, data, headers, params, return_response, raw_exceptions)

    def put(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        return_response: bool = False,
        raw_exceptions: bool = False
    ) -> Response | int | str | dict | list:
        return self._request('PUT', self.prefix + endpoint, data, headers, params, return_response, raw_exceptions)

    def delete(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        return_response: bool = False,
        raw_exceptions: bool = False
    ) -> Response | int | str | dict | list:
        return self._request('DELETE', self.prefix + endpoint, data, headers, params, return_response, raw_exceptions)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        return_response: bool = False,
        raw_exceptions: bool = False
    ) -> Response | int | str | dict | list:
        method = method.upper()

        endpoint = self._base_url.format(endpoint=endpoint)

        if method not in ('GET', 'POST', 'PUT', 'DELETE'):
            raise SyncthingException('unsupported http verb requested, %s' % method)

        if data is None:
            data = {}
        assert isinstance(data, str) or isinstance(data, dict)

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
            raise SyncthingException('http request error', e)

        else:
            if return_response:
                return response

            if response.status_code != requests.codes.ok:
                self.logger.error('%d %s (%s): %s', response.status_code, response.reason, response.url, response.text)
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
                raise SyncthingException(api_err)
            return json_data

__all__ = [
    'DEFAULT_TIMEOUT',
    'BaseAPI'
]
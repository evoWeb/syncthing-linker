import os
import json
import logging
import requests
from urllib.parse import urljoin

from requests import Response

from .service_config import ServiceConfig
from .syncthing_exception import SyncthingException


class BaseAPI:
    """ Placeholder for HTTP REST API URL prefix. """

    prefix = ''

    def __init__(self, config: ServiceConfig):
        if config.ssl_cert_file:
            if not os.path.exists(config.ssl_cert_file):
                raise SyncthingException(f'ssl_cert_file does not exist at location, {config.ssl_cert_file}')

        self.api_key = config.api_key
        self.host = config.host
        self.port = config.port
        self.timeout = config.timeout
        self.is_https = config.is_https
        self.ssl_cert_file = config.ssl_cert_file
        self.verify = bool(config.ssl_cert_file or config.is_https)
        self._headers = {
            'X-API-Key': config.api_key
        }
        self.proto: str = 'https' if config.is_https else 'http'
        self.url = f'{self.proto}://{self.host}:{self.port}'
        self.logger = logging.getLogger(__name__)

    def get(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None
    ) -> Response | int | str | dict | list:
        return self._request('GET', self.prefix + endpoint, data, headers, params)

    def post(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None
    ) -> Response | int | str | dict | list:
        return self._request('POST', self.prefix + endpoint, data, headers, params)

    def put(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None
    ) -> Response | int | str | dict | list:
        return self._request('PUT', self.prefix + endpoint, data, headers, params)

    def delete(
        self,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None
    ) -> Response | int | str | dict | list:
        return self._request('DELETE', self.prefix + endpoint, data, headers, params)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None
    ) -> Response | int | str | dict | list:
        try:
            response = self.raw_request(method, endpoint, data, headers, params)
            response.raise_for_status()

        except requests.RequestException as e:
            raise SyncthingException('HTTP request error') from e

        else:
            if response.status_code != requests.codes.ok:
                self.logger.error(f'{response.status_code} {response.reason} ({response.url}): {response.text}')
                return response

            try:
                json_data = response.json()
            except json.JSONDecodeError:
                return response.content.decode('utf-8')

            if isinstance(json_data, dict) and json_data.get('error'):
                api_err = json_data.get('error')
                raise SyncthingException(f'Response contains the error {api_err}')
            return json_data

    def raw_request(
        self,
        method: str,
        endpoint: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        params: dict | None = None
    ) -> Response:
        method = method.upper()
        endpoint = urljoin(self.url, endpoint)

        if method not in ('GET', 'POST', 'PUT', 'DELETE'):
            raise SyncthingException(f'unsupported http verb requested, {method}')

        if data is None:
            data = {}

        if headers is None:
            headers = {}

        try:
            if not isinstance(data, dict):
                raise AssertionError()
            if not isinstance(headers, dict):
                raise AssertionError()

            headers.update(self._headers)

            return requests.request(
                method,
                endpoint,
                data=json.dumps(data),
                params=params,
                timeout=self.timeout,
                cert=self.ssl_cert_file,
                headers=headers
            )

        except requests.RequestException as e:
            raise SyncthingException('HTTP request error') from e

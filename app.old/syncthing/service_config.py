from dataclasses import dataclass

DEFAULT_TIMEOUT = 10

@dataclass
class ServiceConfig:
    api_key: str = ''
    host: str = 'localhost'
    port: int = 8384
    timeout: int = DEFAULT_TIMEOUT
    is_https: bool = False
    ssl_cert_file: str | None = None
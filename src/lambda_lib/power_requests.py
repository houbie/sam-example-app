import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 5  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    """HTTPAdapter that ensures that a default timeout of 5 seconds is set on every request when
    no explicit timeout is specified.
    """

    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


http = requests.Session()

# retry 1 after 1 second, retry 2 after 2 seconds
retries = Retry(total=2, backoff_factor=2, status_forcelist=[
    429,  # Too Many Requests (retries will backoff)
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
    520,  # Cloudflare: Server Returned an Unknown Error
    521,  # Cloudflare: Web Server Is Down
    522,  # Cloudflare: Connection Timed Out
    525,  # Cloudflare: SSL Handshake Failed
])
adapter = TimeoutHTTPAdapter(max_retries=retries)
http.mount("https://", adapter)
http.mount("http://", adapter)

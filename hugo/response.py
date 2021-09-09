import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from multidict import CIMultiDict

from hugo.config import SERVER_NAME, SERVER_STARTED
from hugo.cookie import Cookie
from hugo.utils import format_http_date


@dataclass
class Response:
    status: int
    body: Optional[bytes]
    content_type: str
    content_length: int
    headers: CIMultiDict = field(default_factory=CIMultiDict)
    cookies: dict = field(default_factory=dict)

    def add_cookie(
        self, key, value, expires=None, max_age=None, secure=False, httponly=False
    ):
        cookie = Cookie(key, value, expires, max_age, secure, httponly)
        self.cookies[key] = cookie

    def delete_cookie(self, key):
        self.add_cookie(key, "", max_age=0)

    @property
    def _final_status(self) -> str:
        status_line = {200: "OK", 404: "Not Found"}.get(self.status)
        return f"{self.status} {status_line}"

    @property
    def _final_headers(self):
        headers = CIMultiDict(
            {
                "Date": format_http_date(datetime.utcnow()),
                "Server": SERVER_NAME,
                "Last-Modified": format_http_date(SERVER_STARTED),
                "Accept-Ranges": "bytes",
                "Content-Length": self.content_length,
                "Connection": "close",
                "Content-Type": self.content_type,
            }
        )
        for cookie in self.cookies.values():
            headers.add("Set-Cookie", cookie.get_header_value())
        headers.extend(self.headers)
        return "\r\n".join(f"{k}: {v}" for k, v in headers.items())

    @property
    def final_response(self) -> bytes:
        resp = (
            f"HTTP/1.1 {self._final_status}\r\n"
            f"{self._final_headers}\r\n\r\n".encode()
        )
        if self.body is not None:
            resp += self.body
        return resp

    @classmethod
    def from_data(
        cls,
        data=None,
        include_body=True,
        content_type="text/html",
        status=200,
    ) -> "Response":
        if isinstance(data, (dict, list)):
            data = json.dumps(data).encode()
            content_type = "application/json"
        elif isinstance(data, str):
            data = data.encode()

        content_length = len(data)
        if not include_body:
            data = None

        return cls(status, data, content_type, content_length)

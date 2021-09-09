import json
from dataclasses import dataclass

from multidict import MultiDict, CIMultiDict

from hugo.config import SESSION_COOKIE_NAME
from hugo.exceptions import HttpError
from hugo.session import Session


@dataclass
class Request:
    method: str
    path: str
    headers: CIMultiDict
    cookies: dict
    body: str
    params: MultiDict
    session: Session
    form: MultiDict
    content_type: str
    content_length: int

    @staticmethod
    def parse_qs(qs: str) -> MultiDict:
        resp = MultiDict()
        for raw_param in qs.split("&"):
            k, v = raw_param.split("=", 1)
            resp.add(k.strip(), v.strip())
        return resp

    @classmethod
    def from_data(cls, data: bytes) -> "Request":
        data = data.decode()

        splitted = data.split("\r\n\r\n", 1)
        if len(splitted) == 2:
            top, body = splitted
        else:
            top, body = splitted[0], ""

        top_lines = top.splitlines()
        method, path, *_ = top_lines[0].split()

        # Parse params
        params = MultiDict()
        if len(path_with_params := path.split("?", 1)) == 2:
            path, raw_params = path_with_params
            params = cls.parse_qs(raw_params)

        # Parse headers
        headers = CIMultiDict()
        for raw_header in top_lines[1:]:
            k, v = raw_header.split(":", 1)
            headers.add(k.strip(), v.strip())

        content_type = headers.get("Content-Type")
        content_length = headers.get("Content-Length")

        # Parse cookies
        cookies = {}
        cookie_header = headers.get("Cookie")
        if cookie_header:
            raw_cookies = [c.strip() for c in cookie_header.split(";")]
            for raw_cookie in raw_cookies:
                k, v = raw_cookie.split("=", 1)
                cookies[k.strip()] = v.strip()

        # Parse session
        if session_cookie := cookies.get(SESSION_COOKIE_NAME):
            session = Session.from_data(session_cookie)
        else:
            session = Session()

        # Parse form data
        if content_type == "application/x-www-form-urlencoded":
            form = cls.parse_qs(body)
        else:
            form = MultiDict()

        return cls(
            method.upper(),
            path,
            headers,
            cookies,
            body,
            params,
            session,
            form,
            content_type,
            content_length,
        )

    def is_json(self) -> bool:
        return self.content_type == "application/json"

    @property
    def json(self):
        if self.is_json():
            return json.loads(self.body)

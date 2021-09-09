from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from hugo.utils import format_http_date


@dataclass
class Cookie:
    name: str
    value: str
    expires: Optional[datetime] = None
    max_age: Optional[int] = None
    secure: bool = False
    httponly: bool = False

    def get_header_value(self):
        values = [f"{self.name}={self.value}"]

        if self.expires is not None:
            values.append(f"Expires={format_http_date(self.expires)}")

        if self.max_age is not None:
            values.append(f"Max-Age={self.max_age}")

        if self.secure:
            values.append("Secure")

        if self.httponly:
            values.append("HttpOnly")

        return "; ".join(values) + ";"

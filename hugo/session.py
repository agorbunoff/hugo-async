import base64
import json
from typing import Optional


class Session(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modified = False

    def __setitem__(self, key, value):
        self.modified = True
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        self.modified = True
        return super().__delitem__(key)

    def serialize(self):
        b = base64.b64encode(json.dumps(self).encode())
        return b.decode()

    @classmethod
    def from_data(cls, data: str) -> Optional["Session"]:
        # try:
        b = base64.b64decode(data.encode())
        return cls(json.loads(b))
        # except:
        #     return None

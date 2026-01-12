import hashlib
import json
from typing import Optional, Iterable, Union, Tuple
from w3lib.url import canonicalize_url

from bald_spider import Request


def to_bytes(text, encoding: str = "utf-8") -> bytes:
    if isinstance(text, bytes):
        return text
    if isinstance(text, str):
        return text.encode(encoding)
    if isinstance(text, dict):
        return json.dumps(text, sort_keys=True).encode(encoding)
    raise TypeError(f" `text` must be bytes, str or dict, but received {type(text)}")

def request_fingerprint(
        request: Request,
        include_headers: Optional[Iterable[Union[str, bytes]]] = None,
) -> str:
    headers: Optional[Tuple[str, ...]] = None
    if include_headers:
        headers = tuple(header.lower() for header in sorted(include_headers))
    fp = hashlib.md5()
    fp.update(request.method.encode())
    fp.update(to_bytes(canonicalize_url(request.url)))
    fp.update(to_bytes(request.body or b""))
    if headers:
        for h in headers:
            if h in request.headers:
                fp.update(to_bytes(h))
                fp.update(to_bytes(request.headers[h]))
    fingerprint = fp.hexdigest()
    return fingerprint


def set_request(request: Request, priority: int):
    request.meta['depth'] = request.meta.setdefault('depth', 0) + 1
    if priority:
        request.priority -= request.meta['depth'] * priority


if __name__ == '__main__':
    request1 = Request(url='www.baidu.com?a=11&b=2', )
    request2 = Request(url='www.baidu.com?b=2&a=1', headers={'a': 1, 'b': 2}, )
    print(request_fingerprint(request1) == request_fingerprint(request2))

import re
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit


def set_query_parameter(url, new_param_values: dict):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    # print(query_params)

    for param_name, param_value in new_param_values.items():
        if param_value is None:
            query_params.pop(param_name, None)
        else:
            query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def parse_bible_ref(references: str):
    pattern = r"(?P<book>\d{0,1}\s?\w+)(\s|.)?((?P<chapter>\d+((–|-)\d+)?)(:(?P<verse>(,?\d+((–|-)\d+)?)+))?)?"
    res = []
    parts = references.split(";")

    last_book = None
    for part in parts:
        match = None
        if not re.search(r"[a-zA-Z]", part) and last_book is not None:
            part = last_book + part

        for match in re.finditer(pattern, part):
            book = match["book"].strip() if match["book"] else None
            last_book = book
            chapter = match["chapter"].strip() if match["chapter"] else None
            verses = match["verse"].split(",") if match["verse"] else None
            res.append(
                {
                    "ref": part.strip(),
                    "book": book,
                    "chapter": chapter,
                    "verses": verses,
                }
            )

    return res

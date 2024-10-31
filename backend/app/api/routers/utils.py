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

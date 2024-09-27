from typing import List

import pytest

class DictObj:
    """
    Convert dict to obj
    """
    def __init__(self, in_dict: dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [DictObj(x) if isinstance(
                    x, dict) else x for x in val])
            else:
                setattr(self, key, DictObj(val)
                        if isinstance(val, dict) else val)


def build_url(uri):
    """Builds full api path

    Args:
        uri (str): api path

    Returns:
        str: full api url
    """
    return f"{pytest.MAIN_URL}/{pytest.BASE_URL}/{uri}"


def get_url(client, uri, check_empty=True, to_dict=True):
    url = build_url(uri)     
    response = client.get(url)
    return standard_check(response, check_empty, to_dict=to_dict)


def standard_check(response, check_empty=True, to_dict=True) -> dict[List]:
    assert response.status_code == 200
    data = response.json()
    if check_empty:
        assert len(data.get("results")) > 0
    if to_dict:
        data = DictObj(data)         
    return data

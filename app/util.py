# !/usr/bin/python
# coding=utf-8


def convert(data):
    """
    bytes convert to str
    """
    if isinstance(data, bytes):
        return data.decode('utf-8')
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return map(convert, data)
    return data

# -*- coding: utf-8 -*-
from collections import namedtuple
from zope.deprecation import deprecate
from decimal import Decimal

import six.moves.urllib.parse


UID_DELIMITER = "|"
COUNT_DELIMITER = ":"

RawCartItem = namedtuple("RawCartItem", ["uid", "count", "comment"])


def read(request):
    """Read, unescape and return the cart cookie.
    """
    return request.cookies.get("cart", "")


@deprecate("Use 'bda.plone.cart.cartitem.purge_cart' instead.")
def delete(request):
    """Delete the cart cookie.
    """
    request.response.expireCookie("cart", path="/")


def split_item(raw_item):
    item = raw_item.split(COUNT_DELIMITER)
    uid = item[0].split(UID_DELIMITER)[0]
    count = item[1]
    comment = six.moves.urllib.parse.unquote(item[0][len(uid) + 1 :])
    return uid, count, comment


def extract_items(items):
    """Cart items are stored in a cookie. The format is
    ``uid;comment:count,uid;comment:count,...``.

    Return a list of RawCartItem namedtuples (uid, count, comment).
    """
    if not items:
        return []
    ret = list()
    __traceback_info__ = str(items)
    items = items.split(",")
    for item in items:
        if not item:
            continue
        uid, count, comment = split_item(item)
        ret.append(RawCartItem(uid, Decimal(count), comment))
    return ret

# -*- coding: utf-8 -*-
from collections import namedtuple
from decimal import Decimal

import six.moves.urllib.parse

UID_DELIMITER = "|"
COUNT_DELIMITER = ":"

RawCartItem = namedtuple("RawCartItem", ["uid", "count", "comment"])


def read(request):
    """Read, unescape and return the cart cookie.
    """
    return request.cookies.get("cart", "")


def delete(request):
    """Delete the cart cookie.
    """
    request.response.expireCookie("cart", path="/")


def extract_items(items):
    """Cart items are stored in a cookie. The format is
    ``uid;comment:count,uid;comment:count,...``.

    Return a list of 3-tuples containing ``(uid, count, comment)``.
    """
    if not items:
        return []
    ret = list()
    items = items.split(",")
    for item in items:
        if not item:
            continue
        item = item.split(COUNT_DELIMITER)
        uid = item[0].split(UID_DELIMITER)[0]
        count = item[1]
        comment = six.moves.urllib.parse.unquote(item[0][len(uid) + 1 :])
        ret.append(RawCartItem(uid, Decimal(count), comment))
    return ret


def remove_item_from_cart(request, uid):
    """Remove single item from cart by uid.
    """
    items = extractitems(read(request))
    cookie_items = list()
    for item_uid, count, comment in items:
        if uid == item_uid:
            continue
        cookie_items.append(
            item_uid
            + UID_DELIMITER
            + six.moves.urllib.parse.quote(comment)
            + COUNT_DELIMITER
            + str(count)
        )
    cookie = ",".join(cookie_items)
    request.response.setCookie("cart", cookie, quoted=False, path="/")

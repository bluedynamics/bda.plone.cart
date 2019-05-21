# -*- coding: utf-8 -*-
from plone import api

import uuid


def ascur(val, comma=False):
    """Convert float value to currency string.

    comma:
         True for ```,``` instead of ```.```.
    """
    val = "%.2f" % val
    if comma:
        return val.replace(".", ",")
    return val


def safe_str_uuid(uid):
    """string of an UID as expected by Plone (i.e. catalog)
    """
    if isinstance(uid, uuid.UUID):
        return uid.hex
    # There is a chance that uids come in the form of str(uuid.UUID), like
    # '8de81513-4317-52d5-f32c-680db93dda0c'. But we need
    # '8de81513431752d5f32c680db93dda0c'. So convert to uuid and get the
    # hex value of it to be sure
    try:
        return uuid.UUID(uid).hex
    except ValueError:
        return None


def get_catalog_brain(context, uid):
    """get catalog brain by its UID or None if UID is invalid
    """
    query_uid = safe_str_uuid(uid)
    if query_uid is None:
        return None
    brains = api.content.find(UID=uid)
    if not brains:
        return None
    if len(brains) > 1:
        raise RuntimeError(u"FATAL: duplicate objects with same UID found.")
    return brains[0]


def get_object_by_uid(context, uid):
    """get object by its UID or None if UID is invalid
    """
    query_uid = safe_str_uuid(uid)
    if query_uid is None:
        return None
    try:
        return api.content.get(UID=uid)
    except ValueError:
        return None

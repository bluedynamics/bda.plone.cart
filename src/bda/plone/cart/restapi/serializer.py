# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import ICartDataProvider
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.cart.restapi.converter import json_compatible_dict
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces import IRequest


@implementer(ISerializeToJson)
@adapter(ICartDataProvider, IRequest)
class SerializeCartDataToJson(object):
    def __init__(self, provider, request):
        self.provider = provider
        self.request = request

    def __call__(self):
        return json_compatible_dict(self.provider.data)


@implementer(ISerializeToJson)
@adapter(ICartItemDataProvider, IRequest)
class SerializeCartItemDataToJson(object):
    def __init__(self, provider, request):
        self.provider = provider
        self.request = request

    def __call__(self):
        return json_compatible_dict(self.provider.data)

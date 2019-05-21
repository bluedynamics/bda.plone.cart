# -*- coding: utf-8 -2-
from bda.plone.cart.cart import get_data_provider
from bda.plone.cart.restapi.service import Service
from bda.plone.cart.restapi.service import TraversingService
from decimal import Decimal
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter


class CartDataService(Service):
    """Cartdata"""

    def reply(self):
        provider = get_data_provider(self.context, self.request)
        serializer = getMultiAdapter((provider, self.request), ISerializeToJson)
        return serializer()


class CartItemValidationService(Service):
    """Cartdata"""

    def reply(self):
        uid = self.request.form["uid"]
        count = Decimal(self.request.form["count"])
        content = api.content.get(UID=uid)
        item_provider = get_data_provider(content, self.request)
        result = item_provider.validate_set(uid)
        if result["success"]:
            result = item_provider.validate_count(uid, count)
        return result


class CartItemDataService(TraversingService):
    def reply(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (item uid)")
        uid = self.params[0]
        content = api.content.get(UID=uid)
        item_provider = get_data_provider(content, self.request)
        serializer = getMultiAdapter((item_provider, self.request), ISerializeToJson)
        return serializer()

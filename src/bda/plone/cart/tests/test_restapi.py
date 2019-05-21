# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import ICartDataProvider
from bda.plone.cart.interfaces import ICartExtensionLayer
from bda.plone.cart.interfaces import ICartItem
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.cart.interfaces import ICartItemState
from bda.plone.cart.tests import Cart_INTEGRATION_TESTING
from bda.plone.cart.tests import cartmocks
from bda.plone.shipping.tests.test_shipping import MockShipping
from decimal import Decimal
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import alsoProvides

import unittest


class TestRestAPI(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, ICartExtensionLayer)

        # create an object for testing
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Document", "doc")
        self.doc = self.portal["doc"]
        alsoProvides(self.doc, ICartItem)
        provideAdapter(MockShipping, name="mock_shipping")
        provideAdapter(cartmocks.MockCartDataProvider)
        provideAdapter(cartmocks.MockCartItemDataProvider)
        provideAdapter(cartmocks.MockCartItemState)
        self.cart_data_provider = getMultiAdapter(
            (self.portal, self.request), interface=ICartDataProvider
        )
        self.cart_item_state = getMultiAdapter(
            (self.doc, self.request), interface=ICartItemState
        )
        self.cart_item_data = getMultiAdapter(
            (self.doc, self.request), interface=ICartItemDataProvider
        )

    def _serializer(self, obj):
        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer

    def test_serializer_item(self):
        self.assertDictEqual(
            self._serializer(self.cart_item_data)(),
            {"net": Decimal("123.45"), "uid": "Unique-Id-0001", "yesno": False},
        )

# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import ICartDataProvider
from bda.plone.cart.interfaces import ICartExtensionLayer
from bda.plone.cart.interfaces import ICartItem
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.cart.interfaces import ICartItemState
from bda.plone.cart.tests import Cart_INTEGRATION_TESTING
from bda.plone.cart.tests import cartmocks
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import alsoProvides

import unittest


class TestRestAPI(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        alsoProvides(self.request, ICartExtensionLayer)

        # create an object for testing
        setRoles(self.layer["portal"], TEST_USER_ID, ["Manager"])
        login(self.layer["portal"], TEST_USER_NAME)
        self.layer["portal"].invokeFactory("Document", "doc")
        self.doc = self.layer["portal"]["doc"]
        alsoProvides(self.doc, ICartItem)

        # setup mocks
        provideAdapter(cartmocks.MockShipping, name="mock_shipping")
        provideAdapter(cartmocks.MockCartDataProvider)
        provideAdapter(cartmocks.MockCartItemDataProvider)
        provideAdapter(cartmocks.MockCartItemState)
        self.cart_data_provider = getMultiAdapter(
            (self.doc, self.request), interface=ICartDataProvider
        )
        self.cart_item_state = getMultiAdapter(
            (self.doc, self.request), interface=ICartItemState
        )
        self.cart_item_data = getAdapter(self.doc, interface=ICartItemDataProvider)

    def _serializer(self, obj):
        return getMultiAdapter((obj, self.request), ISerializeToJson)

    def test_serializer_item(self):
        self.assertDictEqual(
            {"otherkey": 1234.5678, "testkey": u"testvalue"},
            self._serializer(self.cart_item_data)(),
        )

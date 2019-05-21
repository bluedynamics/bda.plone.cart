# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import ICartExtensionLayer
from bda.plone.cart.interfaces import IShipping
from bda.plone.cart.tests import Cart_INTEGRATION_TESTING
from bda.plone.cart.tests import cartmocks
from decimal import Decimal
from zope.component import provideAdapter
from zope.interface import alsoProvides

import unittest


class TestShipping(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, ICartExtensionLayer)
        provideAdapter(cartmocks.MockShipping)
        self.shipping = IShipping(self.portal)

    def test_shipping(self):
        mock = self.shipping
        self.assertEquals(mock.sid, "mock_shipping")
        self.assertEquals(mock.label, "Mock Shipping")
        self.assertEquals(mock.description, "Mock Shipping Description")
        self.assertEquals(mock.available, True)
        self.assertEquals(mock.default, False)
        self.assertEquals(mock.net([]), Decimal(10))
        self.assertEquals(mock.vat([]), Decimal(2))

# -*- coding: utf-8 -*-
from bda.plone.cart.shipping import Shipping
from bda.plone.cart.interfaces import IShipping
from bda.plone.cart.tests import set_browserlayer
from bda.plone.cart.tests import Cart_INTEGRATION_TESTING
from decimal import Decimal
from zope.component import provideAdapter

import unittest


class MockShipping(Shipping):
    sid = "mock_shipping"
    label = "Mock Shipping"
    description = "Mock Shipping Description"
    available = True
    default = False

    def net(self, items):
        return Decimal(10)

    def vat(self, items):
        return Decimal(2)


class TestShipping(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        set_browserlayer(self.request)
        provideAdapter(MockShipping)
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

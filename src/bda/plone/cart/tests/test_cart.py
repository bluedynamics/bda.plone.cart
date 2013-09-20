import unittest2 as unittest
from bda.plone.cart.tests import (
    Cart_INTEGRATION_TESTING,
    set_browserlayer,
)


class TestCart(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)

    def test_foo(self):
        self.assertEquals(1, 1)

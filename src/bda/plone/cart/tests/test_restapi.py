# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import ICartDataProvider
from bda.plone.cart.interfaces import ICartExtensionLayer
from bda.plone.cart.interfaces import ICartItem
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.cart.interfaces import ICartItemState
from bda.plone.cart.tests import Cart_INTEGRATION_TESTING
from decimal import Decimal
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import alsoProvides

import mock
import unittest


class TestRestAPI(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, ICartExtensionLayer)
        # setup mocks
        alsoProvides(self.portal, ICartItem)
        from . import cartmocks
        provideAdapter(cartmocks.MockShipping, name="mock_shipping")
        provideAdapter(cartmocks.MockCartDataProvider)
        provideAdapter(cartmocks.MockCartItemDataProvider)
        provideAdapter(cartmocks.MockCartItemState)
        self.cart_data_provider = getMultiAdapter(
            (self.portal, self.request), interface=ICartDataProvider
        )
        self.cart_item_state = getMultiAdapter(
            (self.portal, self.request), interface=ICartItemState
        )

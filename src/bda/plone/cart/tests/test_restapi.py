# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import ICartExtensionLayer
from bda.plone.cart.tests import Cart_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
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

    def test_serializer(self):
        pass

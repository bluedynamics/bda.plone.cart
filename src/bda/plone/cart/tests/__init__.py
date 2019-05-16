# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import ICartExtensionLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.interface import alsoProvides


def set_browserlayer(request):
    """Set the BrowserLayer for the request.

    We have to set the browserlayer manually, since importing the profile alone
    doesn't do it in tests.
    """
    alsoProvides(request, ICartExtensionLayer)


class CartLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import bda.plone.cart

        self.loadZCML(package=bda.plone.cart, context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, "bda.plone.cart:default")

    def tearDownZope(self, app):
        pass


Cart_FIXTURE = CartLayer()
Cart_INTEGRATION_TESTING = IntegrationTesting(
    bases=(Cart_FIXTURE,), name="Cart:Integration"
)

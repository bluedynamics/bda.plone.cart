# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer


class CartLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi
        import bda.plone.cart

        self.loadZCML(package=plone.restapi, context=configurationContext)
        self.loadZCML(package=bda.plone.cart, context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, "bda.plone.cart:default")

    def tearDownZope(self, app):
        pass


Cart_FIXTURE = CartLayer()
Cart_INTEGRATION_TESTING = IntegrationTesting(
    bases=(Cart_FIXTURE,), name="Cart:Integration"
)
Cart_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(Cart_FIXTURE,), name="Cart:Functional"
)

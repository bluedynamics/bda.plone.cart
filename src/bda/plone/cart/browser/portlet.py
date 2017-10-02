# -*- coding: utf-8 -*-
from bda.plone.cart import extractitems
from bda.plone.cart import readcookie
from bda.plone.cart.browser import CartMixin
from decimal import Decimal
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

import pkg_resources


if pkg_resources.get_distribution("Products.CMFPlone").version > '4.99':
    PLONE5 = 1
else:
    PLONE5 = 0


_ = MessageFactory('bda.plone.cart')


class ICartPortlet(IPortletDataProvider):
    pass


@implementer(ICartPortlet)
class CartAssignment(base.Assignment):

    @property
    def title(self):
        return _(u'cart', u'Cart')


# Patterns to search for in actual browser URL whether to skip rendeing
# cart. Append to this list from addons if you have specific browser URL's
# where you want to skip rendering the cart.
# XXX: use regular expressions
SKIP_RENDER_CART_PATTERNS = [
    '@@checkout',
    '@@confirm_order',
    '/portal_factory/'
]


def render_cart(context):
    url = context.restrictedTraverse('@@plone').getCurrentUrl()
    if url.endswith('@@cart'):
        return False
    for pattern in SKIP_RENDER_CART_PATTERNS:
        if url.find(pattern) > -1:
            return False
    return True


class CartRenderer(base.Renderer, CartMixin):
    if PLONE5:
        template = ViewPageTemplateFile('portlet_p5.pt')
    else:
        template = ViewPageTemplateFile('portlet_p4.pt')

    @property
    def available(self):
        # XXX: is customer somewhere in portal
        return True

    def update(self):
        if render_cart(self.context):
            self.show = True
        else:
            self.show = False

    def render(self):
        if not self.show:
            return u''
        return self.template()


class CartAddForm(base.NullAddForm):
    label = _(u"Add Cart Portlet")
    description = _(u"This portlet displays the shopping cart.")

    def create(self):
        return CartAssignment()


class CartViewlet(ViewletBase, CartMixin):

    def render(self):
        context = self.context
        if not render_cart(context):
            return u''
        # check whether cart portlet is rendered and skip viewlet if so
        for name, manager in getUtilitiesFor(IPortletManager, context=context):
            retriever = getMultiAdapter((context, manager), IPortletRetriever)
            portlets = retriever.getPortlets()
            for portlet in portlets:
                if ICartPortlet.providedBy(portlet['assignment']):
                    return u''
        # XXX: is customer somewhere in portal
        return super(CartViewlet, self).render()

    @property
    def cart_total_count(self):
        # XXX: how to handle float?
        # XXX: count total items in cart or total unique items in cart?
        ret = Decimal('0')
        for uid, count, comment in extractitems(readcookie(self.request)):
            ret += count
        return ret

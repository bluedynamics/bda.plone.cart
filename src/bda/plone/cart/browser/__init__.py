# -*- coding: utf-8 -*-
import simplejson as json
from decimal import Decimal
from zope.interface import implementer
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize import instance
from .. import (
    readcookie,
    get_data_provider,
)


_ = MessageFactory('bda.plone.cart')


CURRENCY_LITERALS = {
    'EUR': u"€",
    'USD': u"$",
    'INR': u"₹",
    'CAD': u"$",
    'CHF': u"CHF",
    'GBP': u"£",
    'AUD': u"$",
    'NOK': u"kr.",
    'SEK': u"Kr.",
    'DKK': u"K.",
    'YEN': u"¥",
}


class DataProviderMixin(object):

    @property
    def data_provider(self):
        return get_data_provider(self.context)


class CartView(BrowserView, DataProviderMixin):

    @property
    def disable_max_article(self):
        return self.data_provider.disable_max_article

    @property
    def summary_total_only(self):
        return self.data_provider.summary_total_only

    @property
    def include_shipping_costs(self):
        return self.data_provider.include_shipping_costs

    @property
    def checkout_url(self):
        cookie = readcookie(self.request)
        if not cookie:
            return
        return self.data_provider.checkout_url

    @property
    def show_currency(self):
        return self.data_provider.show_currency

    @property
    def currency(self):
        return self.data_provider.currency

    @property
    def currency_symbol(self):
        return CURRENCY_LITERALS[self.currency]


class CartDataView(BrowserView, DataProviderMixin):

    def validate_cart_item(self):
        uid = self.request.form.get('uid')
        count = Decimal(self.request.form.get('count'))
        provider = self.data_provider
        ret = dict()
        ret = provider.validate_set(uid)
        if ret['success']:
            ret = provider.validate_count(uid, count)
        return json.dumps(ret)

    def cartData(self):
        return json.dumps(self.data_provider.data)


class ICartPortlet(IPortletDataProvider):
    pass


@implementer(ICartPortlet)
class CartAssignment(base.Assignment):

    @property
    def title(self):
        return _(u'cart', u'Cart')


class CartRenderer(base.Renderer, DataProviderMixin):
    template = ViewPageTemplateFile('portlet.pt')

    def update(self):
        url = self.context.restrictedTraverse('@@plone').getCurrentUrl()
        if url.endswith('@@cart') \
          or url.find('@@checkout') != -1 \
          or url.find('@@confirm_order') != -1 \
          or url.find('/portal_factory/') != -1:
            self.show = False
        else:
            self.show = True

    def render(self):
        if not self.show:
            return u''
        return self.template()

    @property
    def cart_url(self):
        return self.data_provider.cart_url

    @property
    def checkout_url(self):
        return self.data_provider.checkout_url

    @property
    def show_to_cart(self):
        return self.data_provider.show_to_cart

    @property
    def show_checkout(self):
        return self.data_provider.show_checkout


class CartAddForm(base.NullAddForm):
    label = _(u"Add Cart Portlet")
    description = _(u"This portlet displays the shopping cart.")

    def create(self):
        return CartAssignment()

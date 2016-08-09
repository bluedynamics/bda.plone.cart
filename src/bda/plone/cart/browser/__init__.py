# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from bda.plone.cart import CURRENCY_LITERALS
from bda.plone.cart import get_data_provider
from bda.plone.cart import readcookie
from decimal import Decimal
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
import simplejson as json
import zope.deferredimport


zope.deferredimport.deprecated(
    "Import from bda.plone.cart.browser.portlet instead",
    ICartPortlet='bda.plone.cart.browser.portlet:ICartPortlet',
    CartAssignment='bda.plone.cart.browser.portlet:CartAssignment',
    render_cart='bda.plone.cart.browser.portlet:render_cart',
    DummyCartRenderer='bda.plone.cart.browser.portlet:DummyCartRenderer',
    CartRenderer='bda.plone.cart.browser.portlet:CartRenderer',
    CartAddForm='bda.plone.cart.browser.portlet:CartAddForm',
    CartViewlet='bda.plone.cart.browser.portlet:CartViewlet',
)


_ = MessageFactory('bda.plone.cart')


CART_TRANSLATIONS_JS = u"""
(function($) {
    $(document).ready(function() {
        var messages = bda_plone_cart.messages;
        messages.total_limit_reached = "%(total_limit_reached)s";
        messages.not_a_number = "%(not_a_number)s";
        messages.max_unique_articles_reached = "%(max_unique_articles_reached)s";
        messages.comment_required = "%(comment_required)s";
        messages.integer_required = "%(integer_required)s";
        messages.no_longer_available = "%(no_longer_available)s";
        messages.cart_item_added = "%(item_added)s";
        messages.cart_item_updated = "%(item_updated)s";
        messages.cart_item_removed = "%(item_removed)s";
    });
})(jQuery);
"""


class CartJSTranslations(BrowserView):

    def __call__(self):
        msgs = dict()
        msgs['total_limit_reached'] = translate(_(
            'cart_total_limit_reached',
            default=u'Total limit reached'),
            context=self.request)
        msgs['not_a_number'] = translate(_(
            'cart_not_a_number',
            default=u'Input not a number'),
            context=self.request)
        msgs['max_unique_articles_reached'] = translate(_(
            'cart_max_unique_articles_reached',
            default=u'Unique article limit reached'),
            context=self.request)
        msgs['comment_required'] = translate(_(
            'cart_comment_required',
            default=u'Comment is required'),
            context=self.request)
        msgs['integer_required'] = translate(_(
            'cart_integer_required',
            default=u'Input not an integer'),
            context=self.request)
        msgs['no_longer_available'] = translate(_(
            'cart_no_longer_available',
            default=u'One or more items in cart are only partly or no longer '
                    u'available. Please update or remove related items'),
            context=self.request)
        msgs['item_added'] = translate(_(
            'cart_item_added',
            default=u'Item has been added to cart'),
            context=self.request)
        msgs['item_updated'] = translate(_(
            'cart_item_updated',
            default=u'Item has been updated in cart'),
            context=self.request)
        msgs['item_removed'] = translate(_(
            'cart_item_removed',
            default=u'Item has been removed from cart'),
            context=self.request)
        return CART_TRANSLATIONS_JS % msgs


class DataProviderMixin(object):

    @property
    def data_provider(self):
        return get_data_provider(self.context, self.request)


class CartMixin(DataProviderMixin):

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


class CartView(BrowserView, DataProviderMixin):
    # XXX: rename to CartSummary

    @property
    def context_url(self):
        return self.context.absolute_url()

    @property
    def disable_max_article(self):
        return self.data_provider.disable_max_article

    @property
    def summary_total_only(self):
        return self.data_provider.summary_total_only

    @property
    def checkout_url(self):
        cookie = readcookie(self.request)
        if not cookie:
            return
        return self.data_provider.checkout_url

    @property
    def currency(self):
        data_provider = self.data_provider
        currency = data_provider.currency
        show_currency = data_provider.show_currency
        if show_currency == 'yes':
            return currency
        if show_currency == 'symbol':
            return CURRENCY_LITERALS[currency]
        return ''


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

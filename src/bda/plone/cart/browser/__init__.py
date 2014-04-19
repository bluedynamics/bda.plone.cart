# -*- coding: utf-8 -*-
import simplejson as json
from decimal import Decimal
from zope.interface import implementer
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize import instance
from .. import readcookie
from .. import get_data_provider


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
    'NZD': u"$",
}


CART_TRANSLATIONS_JS = u"""
(function($) {
    $(document).ready(function() {
        var messages = bda_plone_cart.messages;
        messages.total_limit_reached = "%(total_limit_reached)s";
        messages.not_a_number = "%(not_a_number)s";
        messages.max_unique_articles_reached = "%(max_unique_articles_reached)s";
        messages.invalid_comment_character = "%(invalid_comment_character)s";
        messages.comment_required = "%(comment_required)s";
        messages.integer_required = "%(integer_required)s";
        messages.no_longer_available = "%(no_longer_available)s";
    });
})(jQuery);
"""


msg_total_limit_reached = _(
    'cart_total_limit_reached',
    default=u'Total limit reached')
msg_not_a_number = _(
    'cart_not_a_number',
    default=u'Input not a number')
msg_max_unique_articles_reached = _(
    'cart_max_unique_articles_reached',
    default=u'Unique article limit reached')
msg_invalid_comment_character = _(
    'cart_invalid_comment_character',
    default=u'Invalid comment characters')
msg_comment_required = _(
    'cart_comment_required',
    default=u'Comment is required')
msg_integer_required = _(
    'cart_integer_required',
    default=u'Input not an integer')
msg_no_longer_available = _(
    'cart_no_longer_available',
    default=u'One or more items in cart are only partly or no longer '
            u'available. Please update or remove related items')


class CartJSTranslations(BrowserView):

    def __call__(self):
        return CART_TRANSLATIONS_JS % {
            'total_limit_reached': translate(
                msg_total_limit_reached, context=self.request),
            'not_a_number': translate(
                msg_not_a_number, context=self.request),
            'max_unique_articles_reached': translate(
                msg_max_unique_articles_reached, context=self.request),
            'invalid_comment_character': translate(
                msg_invalid_comment_character, context=self.request),
            'comment_required': translate(
                msg_comment_required, context=self.request),
            'integer_required': translate(
                msg_integer_required, context=self.request),
            'no_longer_available': translate(
                msg_no_longer_available, context=self.request),
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

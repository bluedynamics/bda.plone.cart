# -*- coding: utf-8 -*-
from bda.plone.cart import _
from bda.plone.cart.interfaces import IItemDelivery
from bda.plone.cart.interfaces import IShipping
from bda.plone.cart.interfaces import IShippingSettings
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getAdapters
from zope.interface import implementer
from zope.interface import Interface


class Shippings(object):
    def __init__(self, context):
        self.context = context

    def get(self, name):
        return getAdapter(self.context, IShipping, name=name)

    @property
    def _adapters(self):
        return getAdapters((self.context,), IShipping)

    @property
    def shippings(self):
        # XXX translating the adapter name is pointless
        return [_[1] for _ in self._adapters]

    @property
    def vocab(self):
        # XXX translating the adapter name is pointless
        # the label should be delivered already as i18n messageid,
        # otherwise it is pointless
        return [(_[0], _[1].label) for _ in self._adapters if _[1].available]

    @property
    def default(self):
        adapters = self._adapters
        for name, shipping in adapters:
            if shipping.default:
                return name
        if adapters:
            return adapters[0][0]


@implementer(IShipping)
@adapter(Interface)
class Shipping(object):
    sid = None
    label = None
    description = None

    def __init__(self, context):
        self.context = context

    @property
    def _settings(self):
        return IShippingSettings(self.context)

    @property
    def available(self):
        return self.sid in self._settings.available

    @property
    def default(self):
        return self.sid == self._settings.default

    def net(self, items):
        raise NotImplementedError(
            u"Abstract ``Shipping`` does not implement " u"``net``"
        )

    def vat(self, items):
        raise NotImplementedError(
            u"Abstract ``Shipping`` does not implement " u"``vat``"
        )

    def calculate(self, items):
        # NOTE: This function is kept for B/C reasons and gets removed as of
        # ``bda.plone.shipping`` 1.0.
        raise NotImplementedError(
            u"Abstract ``Shipping`` does not implement " u"``calculate``"
        )


@implementer(IItemDelivery)
@adapter(Interface)
class NullItemDelivery(object):
    delivery_duration = None

    def __init__(self, context):
        self.context = context

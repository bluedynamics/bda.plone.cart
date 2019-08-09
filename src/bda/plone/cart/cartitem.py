# -*- coding: utf-8 -*-
from bda.plone.cart import cookie
from bda.plone.cart import utils
from bda.plone.cart.interfaces import ICartItem
from bda.plone.cart.interfaces import ICartItemAvailability
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.cart.interfaces import ICartItemDiscount
from bda.plone.cart.interfaces import ICartItemPreviewImage
from bda.plone.cart.interfaces import ICartItemState
from bda.plone.cart.interfaces import ICartItemStock
from bda.plone.cart.interfaces import IItemDelivery
from bda.plone.cart.interfaces import IShippingItem
from decimal import Decimal
from plone.uuid.interfaces import IUUID
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IRequest

import six.moves.urllib.parse


def remove_item_from_cart(request, uid):
    """Remove single item from cart by uid.
    """
    items = cookie.extract_items(cookie.read(request))
    cookie_items = list()
    for item_uid, count, comment in items:
        if uid == item_uid:
            continue
        cookie_items.append(
            item_uid
            + cookie.UID_DELIMITER
            + six.moves.urllib.parse.quote(comment)
            + cookie.COUNT_DELIMITER
            + str(count)
        )
    new_cookie = ",".join(cookie_items)
    request.response.setCookie("cart", new_cookie, quoted=False, path="/")


def purge_cart(request):
    """Purges the whole cart.
    """
    request.response.expireCookie("cart", path="/")


def cart_item_shippable(context, item):
    """Return boolean whether cart item is shippable.
    """
    obj = utils.get_object_by_uid(context, item[0])
    if not obj:
        return False
    shipping = get_item_shipping(obj)
    if shipping:
        return shipping.shippable
    return False


def cart_item_free_shipping(context, item):
    """Return boolean whether cart item shipping is free.
    """
    obj = utils.get_object_by_uid(context, item[0])
    if not obj:
        return False
    shipping = get_item_shipping(obj)
    if shipping:
        return shipping.free_shipping
    return False


def aggregate_cart_item_count(target_uid, items):
    """Aggregate count for items in cart with target uid.
    """
    aggregated_count = 0
    for uid, count, comment in items:
        if target_uid == uid:
            aggregated_count += count
    return aggregated_count


@implementer(ICartItemDataProvider)
class CartItemDataProviderBase(object):
    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return getattr(self.context, "title", "")

    @property
    def net(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``net``."
        )

    @property
    def vat(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``vat``."
        )

    @property
    def cart_count_limit(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``cart_count_limit``."
        )

    @property
    def display_gross(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``display_gross``."
        )

    @property
    def comment_enabled(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``comment_enabled``."
        )

    @property
    def comment_required(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``comment_required``."
        )

    @property
    def quantity_unit_float(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``quantity_unit_float``."
        )

    @property
    def quantity_unit(self):
        raise NotImplementedError(
            u"CartItemDataProviderBase does not implement ``quantity_unit``."
        )

    @property
    def discount_enabled(self):
        # XXX: flag on cart item
        # XXX: probably superfluous
        return True

    def discount_net(self, count):
        if self.discount_enabled:
            discount = queryAdapter(self.context, ICartItemDiscount)
            if discount:
                return discount.net(self.net, self.vat, count)
        return Decimal(0)


AVAILABILITY_CRITICAL_LIMIT = 5.0


@implementer(ICartItemAvailability)
@adapter(ICartItem, IRequest)
class CartItemAvailabilityBase(object):
    """Base cart item availability display behavior adapter.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def stock(self):
        return get_item_stock(self.context)

    @property
    def display(self):
        stock = self.stock
        # stock not applied
        if stock is None:
            return True
        return stock.display

    @property
    def available(self):
        stock = self.stock
        # stock not applied
        if stock is None:
            # unlimited
            return None
        available = stock.available
        # reduce available count if item already in cart
        if available is not None:
            cart_items = cookie.extract_items(cookie.read(self.request))
            item_uid = IUUID(self.context)
            for uid, count, comment in cart_items:
                if uid == item_uid:
                    available -= float(count)
        return available

    @property
    def overbook(self):
        stock = self.stock
        # stock not applied
        if stock is None:
            # unlimited
            return None
        return stock.overbook

    @property
    def critical_limit(self):
        return AVAILABILITY_CRITICAL_LIMIT

    @property
    def addable(self):
        """Default addable rules:

        * if available None, no availability defined, unlimited addable
        * if overbook is None, unlimited overbooking
        * if available > overbook * -1, addable
        * not addable atm
        """
        if self.available is None:
            return True
        if self.overbook is None:
            return True
        if self.available > self.overbook * -1:
            return True
        return False

    @property
    def signal(self):
        """Default signal rules:

        * if available is None, green
        * if available > limit, green
        * if available > 0, yellow
        * if self.overbook is None, orange
        * if available > self.overbook * -1, orange
        * else, red
        """
        available = self.available
        if available is None:
            return "green"
        if available > self.critical_limit:
            return "green"
        if available > 0:
            return "yellow"
        if self.overbook is None:
            return "orange"
        if available > self.overbook * -1:
            return "orange"
        return "red"

    @property
    def details(self):
        raise NotImplementedError(
            u"CartItemAvailabilityBase does not implement ``details``."
        )


@implementer(ICartItemState)
@adapter(ICartItem, IRequest)
class CartItemStateBase(object):
    """Base cart item state implementation.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def aggregated_count(self):
        items = cookie.extract_items(cookie.read(self.request))
        return aggregate_cart_item_count(IUUID(self.context), items)

    @property
    def reserved(self):
        """Return the number of reserved items in the cart from the buyable
        context.
        """
        aggregated_count = float(self.aggregated_count)
        stock = get_item_stock(self.context)
        available = stock.available
        reserved = 0.0
        if available <= 0:
            reserved = aggregated_count
        elif available - aggregated_count < 0:
            reserved = abs(available - aggregated_count)
        return reserved

    @property
    def exceed(self):
        stock = get_item_stock(self.context)
        overbook = stock.overbook
        reserved = self.reserved
        exceed = 0.0
        if overbook is not None:
            if reserved > overbook:
                exceed = reserved - overbook
        return exceed

    @property
    def remaining_available(self):
        stock = get_item_stock(self.context)
        available = stock.available
        overbook = stock.overbook
        if available >= 0:
            remaining_available = available + overbook
        else:
            remaining_available = overbook - available
        return remaining_available

    def validate_count(self, count):
        count = float(count)
        stock = get_item_stock(self.context)
        # stock not applied
        if stock is None:
            return True
        available = stock.available
        overbook = stock.overbook
        if available is None or overbook is None:
            return True
        available -= count
        if available >= overbook * -1:
            return True
        return False

    def alert(self, count):
        raise NotImplementedError(u"CartItemStateBase does not implement ``alert``.")


@implementer(ICartItemPreviewImage)
class CartItemPreviewAdapterBase(object):
    def __init__(self, context):
        self.context = context

    @property
    def url(self):
        raise NotImplementedError(
            u"CartItemPreviewAdapterBase does not implement ``url``."
        )


def get_item_data_provider(context):
    """Return ICartItemDataProvider implementation.
    """
    return getAdapter(context, ICartItemDataProvider)


def get_item_stock(context):
    """Return ICartItemStock implementation.
    """
    return queryAdapter(context, ICartItemStock)


def get_item_shipping(context):
    """Return IShippingItem implementation.
    """
    return queryAdapter(context, IShippingItem)


def get_item_availability(context, request=None):
    """Return ICartItemAvailability implementation.
    """
    if request is None:
        request = context.REQUEST
    return getMultiAdapter((context, request), ICartItemAvailability)


def get_item_delivery(context):
    """Return IItemDelivery implementation.
    """
    return getAdapter(context, IItemDelivery)


def get_item_state(context, request=None):
    """Return ICartItemState implementation.
    """
    if request is None:
        request = context.REQUEST
    return getMultiAdapter((context, request), ICartItemState)


def get_item_preview(context):
    """Return ICartItemPreviewImage implementation.
    """
    return getAdapter(context, ICartItemPreviewImage)

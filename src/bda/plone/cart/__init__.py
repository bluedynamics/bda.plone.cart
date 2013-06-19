import urllib2
from decimal import Decimal
from zope.interface import (
    implementer,
    Interface,
)
from zope.component import (
    adapter,
    getMultiAdapter,
)
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.Archetypes.interfaces.base import IBaseObject
from Products.CMFCore.utils import getToolByName
from bda.plone.cart.interfaces import ICartItemPreviewImage
from bda.plone.shipping import Shippings
from .interfaces import (
    ICartItem,
    ICartDataProvider,
    ICartItemDataProvider,
    ICartItemAvailability,
    ICartItemStock,
)


def ascur(val, comma=False):
    """Convert float value to currency string.

    comma:
         True for ```,``` instead of ```.```.
    """
    val = '%.2f' % val
    if comma:
        return val.replace('.', ',')
    return val


def readcookie(request):
    """Read, unescape and return the cart cookie.
    """
    return urllib2.unquote(request.cookies.get('cart', ''))


def deletecookie(request):
    """Delete the cart cookie.
    """
    request.response.expireCookie('cart', path='/')


def extractitems(items):
    """Cart items are stored in a cookie. The format is
    ``uid:count,uid:count,...``.

    Return a list of 3-tuples containing ``(uid, count, comment)``.
    """
    if not items:
        return []
    ret = list()
    items = urllib2.unquote(items).split(',')
    for item in items:
        if not item:
            continue
        item = item.split(':')
        uid = item[0].split(';')[0]
        count = item[1]
        comment = item[0][len(uid) + 1:]
        try:
            ret.append((uid, Decimal(count), comment))
        except ValueError, e:
            # item[1] may be a 'NaN' -> Should be ok with Decimal now.
            print e
            pass
    return ret


@implementer(ICartDataProvider)
@adapter(Interface, IBrowserRequest)
class CartDataProviderBase(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def disable_max_article(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``disable_max_article``.")

    @property
    def summary_total_only(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``summary_total_only``.")

    @property
    def checkout_url(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``checkout_url``.")

    def net(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``net``.")

    def vat(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``vat``.")

    def cart_items(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``cart_items``.")

    @property
    def include_shipping_costs(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``include_shipping_costs``.")

    @property
    def shipping_method(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``shipping_method``.")

    @property
    def currency(self):
        return 'EUR'

    @property
    def cart_url(self):
        return '%s/@@cart' % self.context.absolute_url()

    @property
    def show_to_cart(self):
        return True

    @property
    def show_checkout(self):
        return False

    @property
    def show_currency(self):
        return True

    def validate_set(self, uid):
        """By default, all items generally may be set.
        """
        return {
            'success': True,
            'error': '',
        }

    def validate_count(self, uid, count):
        obj = get_object_by_uid(self.context, uid)
        availability = get_item_availability(obj)
        count = float(count)
        # XXX
        return {
            'success': True,
            'error': '',
        }

    def shipping(self, items):
        shippings = Shippings(self.context)
        shipping = shippings.get(self.shipping_method)
        return shipping.calculate(items)

    def item(self, uid, title, count, price, url, comment='', description='',
             comment_required=False, quantity_unit_float=False,
             quantity_unit='', preview_image_url=''):
        return {
            # placeholders
            'cart_item_uid': uid,
            'cart_item_title': title,
            'cart_item_count': count,
            'cart_item_price': ascur(price),
            'cart_item_location:href': url,
            'cart_item_preview_image:src': preview_image_url,
            'cart_item_comment': comment,
            'cart_item_description': description,
            'cart_item_quantity_unit': quantity_unit,
            # control flags
            'comment_required': comment_required,
            'quantity_unit_float': quantity_unit_float,
        }

    @property
    def data(self):
        ret = {
            'cart_items': list(),
            'cart_summary': dict(),
        }
        items = extractitems(self.request.form.get('items'))
        if items:
            net = self.net(items)
            vat = self.vat(items)
            cart_items = self.cart_items(items)
            ret['cart_items'] = cart_items
            ret['cart_summary']['cart_net'] = ascur(net)
            ret['cart_summary']['cart_vat'] = ascur(vat)
            if self.include_shipping_costs:
                shipping = self.shipping(items)
                ret['cart_summary']['cart_shipping'] = ascur(shipping)
                ret['cart_summary']['cart_total'] = ascur(net + vat + shipping)
            else:
                ret['cart_summary']['cart_total'] = ascur(net + vat)
            ret['cart_summary']['cart_total_raw'] = net + vat
        return ret


AVAILABILITY_CRITICAL_LIMIT = 5.0


@implementer(ICartItemAvailability)
@adapter(ICartItem, IBrowserRequest)
class CartItemAvailabilityBase(object):
    """Base cart item availability display behavior adapter.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def _stock(self):
        return ICartItemStock(self.context)

    @property
    def available(self):
        available = self._stock.available
        # reduce available count if item already in cart
        if available is not None:
            cart_items = extractitems(readcookie(self.request))
            item_uid = self.context.UID()
            for uid, count, comment in cart_items:
                if uid == item_uid:
                    available -= float(count)
        return available

    @property
    def overbook(self):
        return self._stock.overbook

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
        * if available > CRITICAL_LIMIT, green
        * if available > 0, yellow
        * if available <= 0, red
        """
        if self.available is None:
            return 'green'
        if self.available > self.critical_limit:
            return 'green'
        if self.available > 0:
            return 'yellow'
        return 'red'

    @property
    def details(self):
        raise NotImplementedError(u"CartItemAvailabilityBase does not "
                                  u"implement ``details``.")


@implementer(ICartItemPreviewImage)
@adapter(IBaseObject)
class CartItemPreviewAdapterBase(object):

    def __init__(self, context):
        self.context = context

    @property
    def url(self):
        raise NotImplementedError(
            u"CartItemPreviewAdapterBase does not implement ``url``.")


def get_data_provider(context, request=None):
    """Return ICartDataProvider implementation.
    """
    if request is None:
        request = context.REQUEST
    return getMultiAdapter((context, request), ICartDataProvider)


def get_item_data_provider(context):
    """Return ICartItemDataProvider implementation.
    """
    return ICartItemDataProvider(context)


def get_item_availability(context, request=None):
    """Return ICartItemAvailability implementation.
    """
    if request is None:
        request = context.REQUEST
    return getMultiAdapter((context, request), ICartItemAvailability)


def get_catalog_brain(context, uid):
    cat = getToolByName(context, 'portal_catalog')
    brains = cat(UID=uid)
    if brains:
        if len(brains) > 1:
            raise RuntimeError(
                u"FATAL: duplicate objects with same UID found.")
        return brains[0]
    return None


def get_object_by_uid(context, uid):
    brain = get_catalog_brain(context, uid)
    if brain:
        return brain.getObject()
    return None

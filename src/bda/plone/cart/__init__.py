from .interfaces import ICartDataProvider, ICartItemDataProvider
from Products.Archetypes.interfaces.base import IBaseObject
from Products.CMFCore.utils import getToolByName
from bda.plone.cart.interfaces import ICartItemPreviewImage
from bda.plone.shipping import Shippings
from decimal import Decimal
from zope.component import adapts, getMultiAdapter
from zope.interface import implements, Interface
from zope.publisher.interfaces.browser import IBrowserRequest
import urllib2


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


class CartDataProviderBase(object):
    implements(ICartDataProvider)
    adapts(Interface, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def disable_max_article_count(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``disable_max_article_count``.")

    @property
    def summary_total_only(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``summary_total_only``.")

    @property
    def checkout_url(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``checkout_url``.")

    def validate_set(self, uid):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``validate_set``.")

    def validate_count(self, uid, count):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``validate_count``.")

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
    def cart_url(self):
        return '%s/@@cart' % self.context.absolute_url()

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


def get_data_provider(context):
    """Return ICartDataProvider implementation.
    """
    return getMultiAdapter((context, context.REQUEST), ICartDataProvider)


def get_item_data_provider(context):
    """Return ICartItemDataProvider implementation.
    """
    return ICartItemDataProvider(context)


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


class CartItemPreviewAdapterBase(object):
    implements(ICartItemPreviewImage)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context

    @property
    def url(self):
        raise NotImplementedError(
            u"CartItemPreviewAdapterBase does not implement ``url``.")

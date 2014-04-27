import urllib2
from decimal import Decimal
from zope.interface import implementer
from zope.interface import Interface
from zope.component import adapter
from zope.component import queryAdapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.CMFCore.utils import getToolByName
from bda.plone.shipping.interfaces import IItemDelivery
from bda.plone.shipping import Shippings
from bda.plone.cart.interfaces import ICartItem
from bda.plone.cart.interfaces import ICartDataProvider
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.cart.interfaces import ICartItemAvailability
from bda.plone.cart.interfaces import ICartItemPreviewImage
from bda.plone.cart.interfaces import ICartItemStock
from bda.plone.cart.interfaces import ICartItemState
from bda.plone.cart.interfaces import ICartDiscount
from bda.plone.cart.interfaces import ICartItemDiscount


_ = MessageFactory('bda.plone.cart')


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
    ``uid;comment:count,uid;comment:count,...``.

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
        ret.append((uid, Decimal(count), comment))
    return ret


def aggregate_cart_item_count(target_uid, items):
    """Aggregate count for items in cart with target uid.
    """
    aggregated_count = 0
    for uid, count, comment in items:
        if target_uid == uid:
            aggregated_count += count
    return aggregated_count


def remove_item_from_cart(request, uid):
    """Remove single item from cart by uid.
    """
    items = extractitems(readcookie(request))
    cookie_items = list()
    for item_uid, count, comment in items:
        if uid == item_uid:
            continue
        cookie_items.append(
            item_uid + ';' + comment + ':' + str(count))
    cookie = ','.join(cookie_items)
    request.response.setCookie('cart', cookie, quoted=False, path='/')


# XXX: from config
CART_MAX_ARTICLE_COUNT = 5


@implementer(ICartDataProvider)
@adapter(Interface, IBrowserRequest)
class CartDataProviderBase(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def data(self):
        ret = dict()
        ret['cart_settings'] = dict()
        ret['cart_settings']['hide_cart_if_empty'] = self.hide_cart_if_empty
        if self.disable_max_article:
            ret['cart_settings']['cart_max_article_count'] = 10000
        else:
            ret['cart_settings']['cart_max_article_count'] = \
                CART_MAX_ARTICLE_COUNT
        ret['cart_items'] = list()
        ret['cart_summary'] = dict()
        items = extractitems(self.request.form.get('items'))
        if items:
            net = self.net(items)
            vat = self.vat(items)
            ret['cart_items'] = self.cart_items(items)
            ret['cart_summary']['cart_net'] = ascur(net)
            ret['cart_summary']['cart_vat'] = ascur(vat)
            cart_discount = self.discount(items)
            discount_net = cart_discount['net']
            discount_vat = cart_discount['vat']
            discount_total = discount_net + discount_vat
            ret['cart_summary']['discount_net'] = '-' + ascur(discount_net)
            ret['cart_summary']['discount_vat'] = '-' + ascur(discount_vat)
            ret['cart_summary']['discount_total'] = '-' + ascur(discount_total)
            ret['cart_summary']['discount_total_raw'] = discount_total
            total = net + vat - discount_total
            if self.include_shipping_costs:
                shipping = self.shipping(items)
                total += shipping['net'] + shipping['vat']
                label = translate(shipping['label'], context=self.request)
                ret['cart_summary']['shipping_label'] = label
                if shipping['description']:
                    desc = translate(shipping['description'],
                                     context=self.request)
                    ret['cart_summary']['shipping_description'] = '(%s)' % desc
                else:
                    ret['cart_summary']['shipping_description'] = ''
                ret['cart_summary']['shipping_net'] = ascur(shipping['net'])
                ret['cart_summary']['shipping_vat'] = ascur(shipping['vat'])
                ret['cart_summary']['shipping_total'] = \
                    ascur(shipping['net'] + shipping['vat'])
                ret['cart_summary']['shipping_total_raw'] = \
                    shipping['net'] + shipping['vat']
                # B/C for bda.plone.cart < 0.6 custom templates
                ret['cart_summary']['cart_shipping'] = \
                    ascur(shipping['net'] + shipping['vat'])
            ret['cart_summary']['cart_total'] = ascur(total)
            ret['cart_summary']['cart_total_raw'] = total
        return ret

    @property
    def currency(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``currency``.")

    @property
    def hide_cart_if_empty(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``hide_cart_if_empty``.")

    @property
    def disable_max_article(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``disable_max_article``.")

    @property
    def summary_total_only(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``summary_total_only``.")

    @property
    def include_shipping_costs(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``include_shipping_costs``.")

    @property
    def shipping_method(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``shipping_method``.")

    @property
    def checkout_url(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``checkout_url``.")

    @property
    def cart_url(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``cart_url``.")

    @property
    def show_to_cart(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``show_to_cart``.")

    @property
    def show_checkout(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``show_checkout``.")

    @property
    def show_currency(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``show_currency``.")

    def validate_set(self, uid):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``validate_set``.")

    def validate_count(self, uid, count):
        """Validate setting cart item count for uid.

        uid - Is the cart item UID.
        count - If count is 0, it means that a cart item is going to be
        deleted, which is always allowed. If count is > 0, it's the aggregated
        item count in cart.
        """
        cart_item = get_object_by_uid(self.context, uid)
        item_data = get_item_data_provider(cart_item)
        cart_count_limit = item_data.cart_count_limit
        if cart_count_limit and float(count) > cart_count_limit:
            message = translate(
                _('article_limit_reached', default="Article limit reached"),
                context=self.request)
            return {
                'success': False,
                'error': message,
                'update': False,
            }
        item_state = get_item_state(cart_item, self.request)
        if item_state.validate_count(count):
            return {
                'success': True,
                'error': '',
            }
        message = translate(
            _('trying_to_add_more_items_than_available',
              default="Not enough items available, abort."),
            context=self.request)
        return {
            'success': False,
            'error': message,
            'update': False,
        }

    def net(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``net``.")

    def vat(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``vat``.")

    def shipping(self, items):
        shippings = Shippings(self.context)
        shipping = shippings.get(self.shipping_method)
        try:
            return {
                'label': shipping.label,
                'description': shipping.description,
                'net': shipping.net(items),
                'vat': shipping.vat(items),
            }
        # B/C for bda.plone.shipping < 0.4
        except NotImplementedError:
            return {
                'label': shipping.label,
                'description': shipping.description,
                'net': shipping.calculate(items),
                'vat': Decimal(0),
            }

    def discount(self, items):
        net = vat = Decimal(0)
        discount = queryAdapter(self.context, ICartDiscount)
        if discount:
            net = discount.net(items)
            vat = discount.vat(items)
        return {
            'net': net,
            'vat': vat,
        }

    def cart_items(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``cart_items``.")

    def item(self, uid, title, count, price, url, comment='', description='',
             comment_required=False, quantity_unit_float=False,
             quantity_unit='', preview_image_url='',
             no_longer_available=False, alert=''):
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
            'cart_item_alert': alert,
            # control flags
            'comment_required': comment_required,
            'quantity_unit_float': quantity_unit_float,
            'no_longer_available': no_longer_available,
        }


@implementer(ICartItemDataProvider)
class CartItemDataProviderBase(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return getattr(self.context, 'title', '')

    @property
    def net(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``net``.")

    @property
    def vat(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``vat``.")

    @property
    def cart_count_limit(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``cart_count_limit``.")

    @property
    def display_gross(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``display_gross``.")

    @property
    def comment_enabled(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``comment_enabled``.")

    @property
    def comment_required(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``comment_required``.")

    @property
    def quantity_unit_float(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``quantity_unit_float``.")

    @property
    def quantity_unit(self):
        raise NotImplementedError(u"CartItemDataProviderBase does not "
                                  u"implement ``quantity_unit``.")

    @property
    def discount_enabled(self):
        # XXX: flag on cart item
        return True

    def discount_net(self, count):
        if self.discount_enabled:
            discount = queryAdapter(self.context, ICartItemDiscount)
            if discount:
                return discount.net(self.net, self.vat, count)
        return Decimal(0)


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
    def stock(self):
        return get_item_stock(self.context)

    @property
    def display(self):
        return self.stock.display

    @property
    def available(self):
        available = self.stock.available
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
        return self.stock.overbook

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
            return 'green'
        if available > self.critical_limit:
            return 'green'
        if available > 0:
            return 'yellow'
        if self.overbook is None:
            return 'orange'
        if available > self.overbook * -1:
            return 'orange'
        return 'red'

    @property
    def details(self):
        raise NotImplementedError(u"CartItemAvailabilityBase does not "
                                  u"implement ``details``.")


@implementer(ICartItemState)
@adapter(ICartItem, IBrowserRequest)
class CartItemStateBase(object):
    """Base cart item state implementation.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def aggregated_count(self):
        items = extractitems(readcookie(self.request))
        return aggregate_cart_item_count(self.context.UID(), items)

    @property
    def reserved(self):
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
        available = stock.available
        overbook = stock.overbook
        if available is None or overbook is None:
            return True
        available -= count
        if available >= overbook * -1:
            return True
        return False

    def alert(self, count):
        raise NotImplementedError(u"CartItemStateBase does not "
                                  u"implement ``alert``.")


@implementer(ICartItemPreviewImage)
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


def get_item_stock(context):
    """Return ICartItemStock implementation.
    """
    return ICartItemStock(context)


def get_item_availability(context, request=None):
    """Return ICartItemAvailability implementation.
    """
    if request is None:
        request = context.REQUEST
    return getMultiAdapter((context, request), ICartItemAvailability)


def get_item_delivery(context):
    """Return IItemDelivery implementation.
    """
    return IItemDelivery(context)


def get_item_state(context, request=None):
    """Return ICartItemState implementation.
    """
    if request is None:
        request = context.REQUEST
    return getMultiAdapter((context, request), ICartItemState)


def get_item_preview(context):
    """Return ICartItemPreviewImage implementation.
    """
    return ICartItemPreviewImage(context)


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

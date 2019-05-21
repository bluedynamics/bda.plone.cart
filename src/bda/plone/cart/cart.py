# -*- coding: utf-8 -*-
from bda.plone.cart import _
from bda.plone.cart import cartitem
from bda.plone.cart import cookie
from bda.plone.cart import utils
from bda.plone.cart.interfaces import ICartDataProvider
from bda.plone.cart.interfaces import ICartDiscount
from bda.plone.shipping import Shippings
from decimal import Decimal
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IRequest


def get_data_provider(context, request=None):
    """Return ICartDataProvider implementation.
    """
    if request is None:
        request = context.REQUEST
    return getMultiAdapter((context, request), ICartDataProvider)


@implementer(ICartDataProvider)
@adapter(Interface, IRequest)
class CartDataProviderBase(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def data(self):
        ret = dict()
        ret["cart_settings"] = dict()
        ret["cart_settings"]["hide_cart_if_empty"] = self.hide_cart_if_empty
        if self.disable_max_article:
            ret["cart_settings"]["cart_max_article_count"] = 10000
        else:
            ret["cart_settings"]["cart_max_article_count"] = self.max_artice_count
        include_shipping_costs = self.include_shipping_costs
        ret["cart_settings"]["include_shipping_costs"] = include_shipping_costs
        ret["cart_items"] = list()
        ret["cart_summary"] = dict()
        items = cookie.extract_items(cookie.read(self.request))
        if items:
            net = self.net(items)
            vat = self.vat(items)
            ret["cart_items"] = self.cart_items(items)
            ret["cart_summary"]["cart_net"] = utils.utils.ascur(net)
            ret["cart_summary"]["cart_vat"] = utils.utils.ascur(vat)
            cart_discount = self.discount(items)
            discount_net = cart_discount["net"]
            discount_vat = cart_discount["vat"]
            discount_total = discount_net + discount_vat
            ret["cart_summary"]["discount_net"] = "-" + utils.ascur(discount_net)
            ret["cart_summary"]["discount_vat"] = "-" + utils.ascur(discount_vat)
            ret["cart_summary"]["discount_total"] = "-" + utils.ascur(discount_total)
            ret["cart_summary"]["discount_total_raw"] = discount_total
            total = net + vat - discount_total
            if include_shipping_costs:
                shipping = self.shipping(items)
                total += shipping["net"] + shipping["vat"]
                label = translate(shipping["label"], context=self.request)
                ret["cart_summary"]["shipping_label"] = label
                if shipping["description"]:
                    desc = translate(shipping["description"], context=self.request)
                    ret["cart_summary"]["shipping_description"] = "(%s)" % desc
                else:
                    ret["cart_summary"]["shipping_description"] = ""
                ret["cart_summary"]["shipping_net"] = utils.ascur(shipping["net"])
                ret["cart_summary"]["shipping_vat"] = utils.ascur(shipping["vat"])
                ret["cart_summary"]["shipping_total"] = utils.ascur(
                    shipping["net"] + shipping["vat"]
                )
                ret["cart_summary"]["shipping_total_raw"] = (
                    shipping["net"] + shipping["vat"]
                )
                # B/C for bda.plone.cart < 0.6 custom templates
                ret["cart_summary"]["cart_shipping"] = utils.ascur(
                    shipping["net"] + shipping["vat"]
                )
            ret["cart_summary"]["cart_total"] = utils.ascur(total)
            ret["cart_summary"]["cart_total_raw"] = total
        return ret

    @property
    def total(self):
        total = Decimal(0)
        items = cookie.extract_items(cookie.read(self.request))
        net = self.net(items)
        vat = self.vat(items)
        cart_discount = self.discount(items)
        discount_net = cart_discount["net"]
        discount_vat = cart_discount["vat"]
        discount_total = discount_net + discount_vat
        total = net + vat - discount_total
        if self.include_shipping_costs:
            shipping = self.shipping(items)
            total += shipping["net"] + shipping["vat"]
        return total.quantize(Decimal("1.000"))

    @property
    def currency(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``currency``."
        )

    @property
    def hide_cart_if_empty(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``hide_cart_if_empty``."
        )

    @property
    def max_artice_count(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``max_artice_count``."
        )

    @property
    def disable_max_article(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``disable_max_article``."
        )

    @property
    def summary_total_only(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``summary_total_only``."
        )

    @property
    def include_shipping_costs(self):
        items = cookie.extract_items(cookie.read(self.request))
        for item in items:
            if cartitem.cart_item_shippable(self.context, item):
                return True
        return False

    @property
    def shipping_method(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``shipping_method``."
        )

    @property
    def checkout_url(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``checkout_url``."
        )

    @property
    def cart_url(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``cart_url``."
        )

    @property
    def show_to_cart(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``show_to_cart``."
        )

    @property
    def show_checkout(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``show_checkout``."
        )

    @property
    def show_currency(self):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``show_currency``."
        )

    def validate_set(self, uid):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``validate_set``."
        )

    def validate_count(self, uid, count):
        """Validate setting cart item count for uid.

        uid - Is the cart item UID.
        count - If count is 0, it means that a cart item is going to be
        deleted, which is always allowed. If count is > 0, it's the aggregated
        item count in cart.
        """
        cart_item = utils.get_object_by_uid(self.context, uid)
        item_data = cartitem.get_item_data_provider(cart_item)
        cart_count_limit = item_data.cart_count_limit
        if cart_count_limit and float(count) > cart_count_limit:
            message = translate(
                _("article_limit_reached", default="Article limit reached"),
                context=self.request,
            )
            return {"success": False, "error": message, "update": False}
        item_state = cartitem.get_item_state(cart_item, self.request)
        if item_state.validate_count(count):
            return {"success": True, "error": ""}
        message = translate(
            _(
                "trying_to_add_more_items_than_available",
                default="Not enough items available, abort.",
            ),
            context=self.request,
        )
        return {"success": False, "error": message, "update": False}

    def net(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement ``net``.")

    def vat(self, items):
        raise NotImplementedError(u"CartDataProviderBase does not implement ``vat``.")

    def shipping(self, items):
        shippings = Shippings(self.context)
        shipping = shippings.get(self.shipping_method)
        try:
            return {
                "label": shipping.label,
                "description": shipping.description,
                "net": shipping.net(items),
                "vat": shipping.vat(items),
            }
        # B/C for bda.plone.shipping < 0.4
        except NotImplementedError:
            return {
                "label": shipping.label,
                "description": shipping.description,
                "net": shipping.calculate(items),
                "vat": Decimal(0),
            }

    def discount(self, items):
        net = vat = Decimal(0)
        discount = queryAdapter(self.context, ICartDiscount)
        if discount:
            net = discount.net(items)
            vat = discount.vat(items)
        return {"net": net, "vat": vat}

    def cart_items(self, items):
        raise NotImplementedError(
            u"CartDataProviderBase does not implement ``cart_items``."
        )

    def item(
        self,
        uid,
        title,
        count,
        price,
        url,
        comment="",
        description="",
        comment_required=False,
        quantity_unit_float=False,
        quantity_unit="",
        preview_image_url="",
        no_longer_available=False,
        alert="",
        discount=Decimal(0),
    ):
        return {
            # placeholders
            "cart_item_uid": uid,
            "cart_item_title": title,
            "cart_item_count": count,
            "cart_item_price": utils.ascur(price),
            "cart_item_location:href": url,
            "cart_item_preview_image:src": preview_image_url,
            "cart_item_comment": comment,
            "cart_item_description": description,
            "cart_item_quantity_unit": quantity_unit,
            "cart_item_alert": alert,
            "cart_item_discount": utils.ascur(discount)
            if discount != Decimal(0)
            else Decimal(0),
            # control flags
            "comment_required": comment_required,
            "quantity_unit_float": quantity_unit_float,
            "no_longer_available": no_longer_available,
        }

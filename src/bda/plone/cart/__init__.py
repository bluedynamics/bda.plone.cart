# -*- coding: utf-8 -*-
from zope.deferredimport import deprecated
from zope.i18nmessageid import MessageFactory


deprecated(
    "Import from new module instead",
    # utils
    ascur="bda.plone.cart.utils:ascur",
    safe_str_uuid="bda.plone.cart.utils:safe_str_uuid",
    get_catalog_brain="bda.plone.cart.utils:get_catalog_brain",
    get_object_by_uid="bda.plone.cart.utils:get_object_by_uid",
    # cookie
    readcookie="bda.plone.cart.cookie:read",
    deletecookie="bda.plone.cart.cookie:delete",
    extractitems="bda.plone.cart.cookie:extract_items",
    remove_item_from_cart="bda.plone.cart.cookie:remove_item_from_cart",
    # cartitem
    cart_item_shippable="bda.plone.cart.cartitem:cart_item_shippable",
    cart_item_free_shipping="bda.plone.cart.cartitem:cart_item_free_shipping",
    aggregate_cart_item_count="bda.plone.cart.cartitem:aggregate_cart_item_count",
    CartItemDataProviderBase="bda.plone.cart.cartitem:CartItemDataProviderBase",
    CartItemAvailabilityBase="bda.plone.cart.cartitem:CartItemAvailabilityBase",
    CartItemStateBase="bda.plone.cart.cartitem:CartItemStateBase",
    CartItemPreviewAdapterBase="bda.plone.cart.cartitem:CartItemPreviewAdapterBase",
    get_item_data_provider="bda.plone.cart.cartitem:get_item_data_provider",
    get_item_stock="bda.plone.cart.cartitem:get_item_stock",
    get_item_shipping="bda.plone.cart.cartitem:get_item_shipping",
    get_item_availability="bda.plone.cart.cartitem:get_item_availability",
    get_item_delivery="bda.plone.cart.cartitem:get_item_delivery",
    get_item_state="bda.plone.cart.cartitem:get_item_state",
    get_item_preview="bda.plone.cart.cartitem:get_item_preview",
    # cart
    get_data_provider="bda.plone.cart.cart:get_data_provider",
    CartDataProviderBase="bda.plone.cart.cart:CartDataProviderBase",
)

_ = MessageFactory("bda.plone.cart")


# XXX currency handling should be replaced by https://pypi.org/project/money/
CURRENCY_LITERALS = {
    "EUR": u"€",
    "USD": u"$",
    "INR": u"₹",
    "CAD": u"$",
    "CHF": u"CHF",
    "GBP": u"£",
    "AUD": u"$",
    "NOK": u"kr.",
    "SEK": u"Kr.",
    "DKK": u"K.",
    "YEN": u"¥",
    "NZD": u"$",
}

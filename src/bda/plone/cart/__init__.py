# -*- coding: utf-8 -*-
from zope.deferredimport import deprecated
from zope.i18nmessageid import MessageFactory


deprecated(
    "Import from new module 'bda.plone.cart.utils' instead",
    ascur="bda.plone.cart.utils:ascur",
    get_catalog_brain="bda.plone.cart.utils:get_catalog_brain",
    get_object_by_uid="bda.plone.cart.utils:get_object_by_uid",
    safe_str_uuid="bda.plone.cart.utils:safe_str_uuid",
)
deprecated(
    "Import from new module 'bda.plone.cart.cookie' instead",
    deletecookie="bda.plone.cart.cookie:delete",
    readcookie="bda.plone.cart.cookie:read",
    extractitems="bda.plone.cart.cookie:extract_items",
)
deprecated(
    "Import from new module 'bda.plone.cart.cartitem' instead",
    aggregate_cart_item_count="bda.plone.cart.cartitem:aggregate_cart_item_count",
    cart_item_free_shipping="bda.plone.cart.cartitem:cart_item_free_shipping",
    cart_item_shippable="bda.plone.cart.cartitem:cart_item_shippable",
    CartItemAvailabilityBase="bda.plone.cart.cartitem:CartItemAvailabilityBase",
    CartItemDataProviderBase="bda.plone.cart.cartitem:CartItemDataProviderBase",
    CartItemPreviewAdapterBase="bda.plone.cart.cartitem:CartItemPreviewAdapterBase",
    CartItemStateBase="bda.plone.cart.cartitem:CartItemStateBase",
    get_item_availability="bda.plone.cart.cartitem:get_item_availability",
    get_item_data_provider="bda.plone.cart.cartitem:get_item_data_provider",
    get_item_delivery="bda.plone.cart.cartitem:get_item_delivery",
    get_item_preview="bda.plone.cart.cartitem:get_item_preview",
    get_item_shipping="bda.plone.cart.cartitem:get_item_shipping",
    get_item_state="bda.plone.cart.cartitem:get_item_state",
    get_item_stock="bda.plone.cart.cartitem:get_item_stock",
    remove_item_from_cart="bda.plone.cart.cartitem:remove_item_from_cart",
)
deprecated(
    "Import from new module 'bda.plone.cart.cart' instead",
    CartDataProviderBase="bda.plone.cart.cart:CartDataProviderBase",
    get_data_provider="bda.plone.cart.cart:get_data_provider",
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

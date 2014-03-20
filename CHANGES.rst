
Changelog
=========

0.4dev
------

- Add ``bda.plone.cart.CartItemDataProviderBase`` class.
  [rnix]

- Extend ``bda.plone.cart.interfaces.ICartItemDataProvider`` by
  ``discount_enabled`` and ``discount_net`` properties.
  [rnix]

- Introduce ``bda.plone.cart.interfaces.ICartDiscount``.
  [rnix]

- Introduce ``bda.plone.cart.interfaces.ICartItemDiscount``.
  [rnix]

- Fix BrowserLayer order precedence.
  [thet]


0.3
---

- Add ``get_item_delivery`` helper function for looking up ``IItemDelivery``
  adapter.
  [rnix]


0.2
---

- Introduce ``bda.plone.cart.interfaces.ICartItemState``.
  [rnix]

- Introduce ``bda.plone.cart.interfaces.ICartItemAvailability``.
  [rnix]

- Introduce ``bda.plone.cart.interfaces.ICartItemStock``.
  [rnix]

- Allow the cart portlet in the left column too.
  [fRiSi]

- Add adapter for cart item preview images
  [petschki]


0.1
---

- initial work
  [rnix]

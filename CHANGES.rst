
Changelog
=========

2.0.dev0 (unreleased)
---------------------

- Use bs popover markup to display cart status message.
  [rnix]

- Remove decimal_converter and rely on plone.restapi>=6.13.7
  [agitator]

- Mark cart item in summary and portlet if comment is enabled or not.
  [jensens]

- Fix broken remove from cart in summary.
  [jensens]

- Handle count number localized.
  [jensens]

- No longer support for z3c.autoinclude.
  [jensens]

- More CSS classes on cart
  [jensens]

- Fix problem, when cart item value is removed while typing item was removed from cart.
  [jensens]

- Fix problem, when in listing the to be added number changes was immediately is added to the cart.
  [jensens]

- Moved shipping code over to here.
  [jensens]

- Refactored lots of code out of init into more semantic modules.
  [jensens]

- Added RESTAPI
  [jensens]

- Code style black.
  [jensens]

- Python 2/3 compatibility
  [agitator]

- Update version and classifiers - 2.x targets Plone 5.1/5.2 without Archetypes
  [agitator]

- Italian translations
  [ale-rt]


1.0a1 (unreleased)
------------------

- Keep cart item cound focus after auto update.
  [rnix]

- Auto update cart if item count changes.
  [rnix]

- Replace unittest2 with untittest.
  [llisa123]

- Introduce ``bda.plone.cart.browser.portlet.SKIP_RENDER_CART_PATTERNS`` which
  can be used to define patterns which are checked against actual browser URL
  defining whether to skip cart rendering.
  [rnix]

- In ``cart.js``, make code blocks dealing with add and update after click event available for third party code.
  A move of the two anonymous functions in its own named functions,
  named ``update_cart_item`` and ``add_cart_item`` taking the node as parameter there were called on.
  [jensens]

- In ``cart.js``, allow also a select for count.
  [jensens. agitator]

- Add support for displaying cart item discount in cart.
  [rnix]

- Add ``get_item_shipping`` and ``cart_item_free_shipping`` utilities.
  [rnix]

- Fix typo. Rename remaining ``card_item_tempate`` to ``cart_item_tempate``.
  This already has been changed for summary and overview
  (in ``bda.plone.checkout``) but was missing in ``cart.js`` and ``tile.pt``
  fixes ``#31``. Make sure to fix this in all your cart related custom
  templates!
  [rnix]

- More precise selectors for cart item template, cart summary discount and
  cart summary shipping in ``cart.js``.
  [rnix]

- Use code for safe uid also for get_object_by_uid and use ``plone.api``.
  [jensens]

- fixed selector typo #cart_viewlet_summery with #cart_viewlet_summary
  [agitator]

- Pass comment in JS from add/update cart to server side validation.
  [jensens]

- use MwSt. instead of Ust. in german
  [agitator]

- added data-context-url for sane cartData and validate_cart_item calls on Plone 5
  [agitator]

- Plone 5 update
  [agitator]

- ``extractitems`` now returns a namedtuple with attributes ``uid``, ``count`` and ``comment``
  [jensens]


0.10.dev2
---------

- Resolve JSHint errors and warnings.
  [thet]

- Fix cart item not removable, if comment is required. Fixes #17, fixes #12.
  [thet]

- Remove portlet's cartWrapper div node. It's not used at all and only
  introduces non-standard portlet HTML markup.
  [thet]

- By default, cart viewlet is hidden and gets displayed as soon as cart items
  are fetched.
  [rnix]

- Consider ``hide cart if empty`` setting on cart viewlet.
  [rnix]

- Hide unset preview images for cart item.
  [rnix]

- Cart can display status message if cart data gets modified.
  [rnix]

- Cart might be rendered as viewlet in portal header instead of as portlet.
  [rnix]

- Do not expect ``IShippingItem`` to be implemented. See also
  ``https://github.com/bluedynamics/bda.plone.shop/issues/31``
  [jensens]

- No caching/merging of cart.translations.js
  [agitator]



0.9
---

- Quote/Unqote special characters in cart cookie only for cart item comment.
  Thus we can have any characters in comment. "Invalid comment characters"
  validation and error message no longer necessary.
  [rnix]


0.8
---

- Use ``decodeURIComponent`` instead of deprectaed ``unescape`` in ``cart.js``.
  [rnix]

- Catch ``ValueError`` if given uid value is no valid ``uuid.UUID`` string in
  ``get_catalog_brain``.
  [rnix]

- Let ``get_catalog_brain`` and thus ``get_object_by_uid`` handle ``uuid.UUID``
  objects, hex strings like '8de81513431752d5f32c680db93dda0c' and UUID object
  representation strings like '8de81513-4317-52d5-f32c-680db93dda0c'.
  [thet]

- Encode umlaut characters in cart item comment.
  [rnix]


0.7
---

- Add comment label in cart summary template.
  [rnix]


0.6
---

- Hide discount and shipping info in cart via JS if data changed respective.
  [rnix]

- Remove ``include_shipping_costs`` property from ``CartView``.
  [rnix]

- Always deliver shipping markup for cart, control with JS whether shipping
  costs are displayed.
  [rnix]

- Move ``bda.plone.cart.browser.CURRENCY_LITERALS`` to
  ``bda.plone.cart.CURRENCY_LITERALS``.
  [rnix]

- Add ``ICartDataProvider.max_artice_count`` attribute and implement in
  ``CartDataProviderBase``.
  [rnix]

- Add ``bda.plone.cart.cart_item_shippable`` utility.
  [rnix]

- Implement ``ICartDataProvider.include_shipping_costs`` on
  ``CartDataProviderBase`` using
  ``bda.plone.shipping.interfaces.IShippingItem.shipping`` flag for
  calculation.
  [rnix]

- Add ``ICartDataProvider.total`` attribute and implement in
  ``CartDataProviderBase``.
  [rnix]

- Use ``readcookie`` instead of expecting ``items`` request parameter in
  ``CartDataProviderBase.data``.
  [rnix]

- Do not pass recent cart ``items`` parameter to ``@@cartData`` view, contained
  value is included as ``cart`` cookie anyways.
  [rnix]

- Adopt shipping handling to ``bda.plone.shipping`` >= 0.4.
  [rnix]

- ``CartDataProviderBase`` no longer provides default values for ``currency``,
  ``cart_url``, ``show_to_cart``, ``show_checkout`` and ``show_currency``.
  [rnix]

- Add browser view rendering a JS snippet for Cart JS translations. Cart
  translations are now handled via message catalogs.
  [rnix]

- Fix validation of comment characters in cart JS.
  [rnix]


0.5
---

- Add a title property to the ``ICartItemDataProvider`` accessor interface to
  allow customizations of the cart item title. This can be used to give more
  context on the cart item, e.g. for a buyable within another content item.
  [thet]


0.4
---

- Cart validation considers ``update`` flag on error.
  [rnix]

- Introduce ``remove_item_from_cart`` utility function.
  [rnix]

- ``validate_set`` of ``CartDataProviderBase`` raises ``NotImplementedError``.
  [rnix]

- Hanlde ``article_limit_reached`` message on server side.
  [rnix]

- Extend ``bda.plone.cart.interfaces.ICartItemDataProvider`` by
  ``cart_count_limit``.
  [rnix]

- Fix and refactor max article count for cart.
  [rnix]

- Add ``hide_cart_if_empty`` property to
  ``bda.plone.cart.interfaces.ICartDataProvider``, integrate in
  ``bda.plone.cart.CartDataProviderBase`` and consider in Cart JS.
  [rnix]

- Add ``display`` property to ``bda.plone.cart.interfaces.ICartItemStock`` and
  and expose it via ``bda.plone.cart.CartItemAvailabilityBase``
  [rnix]

- Add ``bda.plone.cart.CartItemDataProviderBase`` class.
  [rnix]

- Extend ``bda.plone.cart.interfaces.ICartItemDataProvider`` by
  ``discount_enabled`` and ``discount_net``.
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

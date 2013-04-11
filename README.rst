bda.plone.cart
##############

Shopping cart portlet for plone.

.. contents::

Installation
============

Depend your instance to ``bda.plone.cart`` and install it as addon
in plone control panel.


Provide data
============

This package provides components needed to render shopping cart. It does
not expect any contracts but ``bda.plone.cart.ICartDataProvider``.

Implement data provider inheriting from
``bda.plone.cart.CartDataProviderBase``,

::

    >>> from bda.plone.cart import CartDataProviderBase
    >>> class AppCartDataProvider(CartDataProviderBase):
    ...     """Also look at ``bda.plone.cart.example`` source code.
    ...     """
    ...
    ...     def net(self, items):
    ...         """Return net price for items as float.
    ...         """
    ...
    ...     def vat(self, items):
    ...         """Return VAT for items as float.
    ...         """
    ...
    ...     def cart_items(self, items):
    ...         """Return list of dicts with format returned by ``self.item``.
    ...         """
    ...
    ...     def validate_set(self, uid):
    ...         """Validate if setting item with UID is allowed.
    ...         """
    ...         return {
    ...             'success': True,
    ...             'error': '',
    ...         }
    ...
    ...     def validate_count(self, uid, count):
    ...         """Validate if setting n items with UID is allowed.
    ...         """
    ...         return {
    ...             'success': True,
    ...             'error': '',
    ...         }
    ...
    ...     @property
    ...     def currency(self):
    ...         return 'EUR'
    ...
    ...     @property
    ...     def disable_max_article(self):
    ...         """Flag whether to disable max article limit.
    ...         """
    ...         return True
    ...
    ...     @property
    ...     def summary_total_only(self):
    ...         """Flag whether to show total sum only in summary.
    ...         """
    ...         return False
    ...
    ...     @property
    ...     def include_shipping_costs(self):
    ...         return True
    ...
    ...     @property
    ...     def shipping_method(self):
    ...         return 'flat_rate'
    ...
    ...     @property
    ...     def checkout_url(self):
    ...         """URL to checkout view.
    ...         """
    ...         return '%s/@@checkout' % self.context.absolute_url()
    ...
    ...     @property
    ...     def cart_url(self):
    ...         """URL to cart view.
    ...         """
    ...         return '%s/@@cart' % self.context.absolute_url()

and register it as adapter with ZCML. The adapter is looked up for context
and request, these attributes are available on ``context`` respective
``request`` on data provider::

    <adapter
        for="some.package.IContext
             zope.publisher.interfaces.browser.IBrowserRequest"
        factory="some.package.AppCartDataProvider" />


Cart Item Preview Image
=======================

The Cart renders a preview image for the cart items for two cases

    1. the context has a field named "image"
    2. collective.contentleadimage is installed

You can easily change the preview image rendering by adapt your buyable items.
if you only want to change the scale of the image you can::

    from bda.plone.shop.cartdata import CartItemPreviewImage

    class MyCartItemPreviewImage(CartItemPreviewImage):
        preview_scale = "my_scale"

to do more complex preview image rendering you can override the *url*
property::

    from bda.plone.shop.cartdata import CartItemPreviewImage

    class MyCartItemPreviewImage(CartItemPreviewImage):

        @property
        def url(self):
            # do sophisticated stuff to get your preview image
            return preview_url

in both cases don't forget to define in configure.zcml::

    <adapter for="some.package.IContent"
        factory=".youradater.MyCartItemPreviewImage" />

Markup
======

Take a look at ``bda.plone.cart.browser:tile.pt`` how HTML markup
for adding items to cart might look like.

Basically a shop item consists of a container DOM element, containing an
element with CSS class ``cart_item_uid``, where the item UID is taken from::

    <span class="cart_item_uid" style="display: none;">12345678</span>

a text input field with CSS class ``cart_item_count`` which is read for
item count::

    <input type="text" size="2" value="1" class="cart_item_count" />

a quantity unit::

    <span class="cart_item_quantity_unit">Quantity</span>

If quantity unit can be be float, add ``quantity_unit_float`` CSS class::

    <input type="text" size="2" value="1"
           class="cart_item_count quantity_unit_float" />

the "add to Cart" action::

    <a href="" class="add_cart_item">add to cart</a>

and the "update cart" action::

    <a href="" class="update_cart_item">update cart</a>

and optionally an element defining a comment or an input for entering a
comment::

    <input type="text" size="20" value="" class="cart_item_comment" />

If comment should be required, add CSS class ``required`` to comment input.
If comment is empty, an error message gets shown to the user when trying to
add or update a cart item::

    <input type="text" size="20" value="" class="cart_item_comment required" />


Javascript
==========

The cart can be customizes on client side.

Flag whether to hide cart container if cart is empty::

    CART_HIDE_CONTAINER_IF_EMPTY = [true|false];

Maximum number of allowed articles in order::

    CART_MAX_ARTICLE_COUNT = 20;

Client side dialog messages::

    cart.messages['article_limit_reached'] = "Article limit reached";
    cart.messages['total_limit_reached'] = "Total limit reached";
    cart.messages['not_a_number'] = "Input not a number";
    cart.messages['max_unique_articles_reached'] = "Unique article limit reached";
    cart.messages['invalid_comment_character'] = "Invalid comment characters";
    cart.messages['comment_required'] = "Comment is required";
    cart.messages['integer_required'] = "Input not an integer";


Create translations
===================

::

    $ cd src/bda/plone/cart/
    $ ./i18n.sh


Contributors
============

- Robert Niederreiter

- Peter Holzer

- Sven Plage

- Harald Friessnegger, Webmeisterei GmbH

- Peter Mathis, Kombinat Media Gestalter GmbH

- Icons by famfamfam



==============
bda.plone.cart
==============

Shopping cart for plone.

.. contents::


Base package Installation
=========================

Depend your instance to ``bda.plone.cart`` and install it as addon
in plone control panel.


Provide contracts
=================

This package provides components needed to render a shopping cart. It expects
several contracts defined in:

- ``bda.plone.cart.interfaces.ICartDataProvider``
- ``bda.plone.cart.interfaces.ICartItemDataProvider``
- ``bda.plone.cart.interfaces.ICartItemStock``
- ``bda.plone.cart.interfaces.ICartItemPreviewImage``
- ``bda.plone.cart.interfaces.ICartItemAvailability``
- ``bda.plone.cart.interfaces.ICartItemState``
- ``bda.plone.cart.interfaces.ICartDiscount``
- ``bda.plone.cart.interfaces.ICartItemDiscount``

Please take a look at the corresponding interfaces for contract details.
Further some abstract base implementations are available in
``bda.plone.cart.__init__`` which can be used as base class for concrete
implementations.


Cart Visibility
===============

The cart can be rendered as a portlet or inside a viewlet in the portal
header. It's not possible to render the cart twice in one page. Thus, the
viewlet gets skipped automatically if a cart portlet assignment is found.
Also, if cart summary, checkout, order confirmation or portal factory is
rendered, regular cart rendering gets skipped.


A ready-to-use implementation
=============================

Concrete implementations of the expected contracts already exists in
``bda.plone.shop`` for Archetypes and Dexterity. Please refer to
``https://github.com/bluedynamics/bda.plone.shop`` for more details.


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

Optionally, If cart viewlet is used, a status message can be displayed when
adding or updating cart items. This is useful if user should get
clearly informed if cart data has changed. To display status messages,
add CSS class ``show_status_message`` to "add to cart" and "update cart"
actions::

    <a href="" class="update_cart_item show_status_message">update cart</a>

and optionally an element defining a comment or an input for entering a
comment::

    <input type="text" size="20" value="" class="cart_item_comment" />

If comment should be required, add CSS class ``required`` to comment input.
If comment is empty, an error message gets shown to the user when trying to
add or update a cart item::

    <input type="text" size="20" value="" class="cart_item_comment required" />


Create translations
===================

::
    $ cd src/bda/plone/cart/
    $ ./i18n.sh


Contributors
============

- Robert Niederreiter (Autor)
- Sven Plage
- Peter Holzer
- Harald Friessnegger
- Peter Mathis
- Espen Moe-Nilssen
- Johannes Raggam
- Jure Cerjak
- Icons by famfamfam

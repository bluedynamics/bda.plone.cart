# -*- coding: utf-8 -*-
from bda.plone.cart.cart import CartDataProviderBase
from bda.plone.cart.cartitem import CartItemDataProviderBase
from bda.plone.cart.cartitem import CartItemStateBase
from bda.plone.cart.interfaces import ICartItem
from zope.component import adapter


class MockCartItemState(CartItemStateBase):
    """Mock implementation of ICartItemState.
    """

    def alert(self, count):
        return "You have too many items in the cart: {0}".format(count)

    def validate_count(self, count):
        if count < 5:
            return True
        return False


class MockCartDataProvider(CartDataProviderBase):
    """Mock implementation of ICartDataProvider.
    """

    @property
    def disable_max_article(self):
        return True

    @property
    def summary_total_only(self):
        return True

    @property
    def checkout_url(self):
        return "%s/@@checkout" % self.context.absolute_url()

    @property
    def include_shipping_costs(self):
        return False

    @property
    def shipping_method(self):
        return "mock_shipping"

    def net(self, items):
        return 100

    def vat(self, items):
        return 50

    def validate_set(self, uid):
        return {"success": True, "error": ""}

    def cart_items(self, items):
        cart_items = []

        uid = "foo-uid"
        title = u"Le item"
        count = 5
        price = 150
        url = u"http://foo"

        item = self.item(uid, title, count, price, url)
        cart_items.append(item)

        return items


@adapter(ICartItem)
class MockCartItemDataProvider(CartItemDataProviderBase):
    """Mock implementation of ICartItemDataProvider.
    """

    @property
    def title(self):
        title = super(MockCartItemDataProvider, self).title
        return "Most awesome {}".format(title)

    @property
    def cart_count_limit(self):
        return 10

    @property
    def discount_enabled(self):
        return False

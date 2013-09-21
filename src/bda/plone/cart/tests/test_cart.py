import mock
import unittest2 as unittest
from bda.plone.cart.tests import (
    Cart_INTEGRATION_TESTING,
    set_browserlayer,
)
from bda.plone.cart import (
    CartDataProviderBase,
    CartItemStateBase,
)
from bda.plone.cart.interfaces import (
    ICartDataProvider,
    ICartItem,
    ICartItemState,
)
from bda.plone.shipping.tests.test_shipping import MockShipping
from zope.component import (
    provideAdapter,
    getMultiAdapter,
)
from zope.interface import alsoProvides


class MockCartItemState(CartItemStateBase):
    """Mock implementation of ICartItemState."""

    def alert(self, count):
        return "You have too many items in the cart: {0}".format(count)

    def validate_count(self, count):
        if count < 5:
            return True
        return False


class MockCartDataProvider(CartDataProviderBase):
    """Mock implementation of ICartDataProvider."""

    @property
    def disable_max_article(self):
        return True

    @property
    def summary_total_only(self):
        return True

    @property
    def checkout_url(self):
        return '%s/@@checkout' % self.context.absolute_url()

    @property
    def include_shipping_costs(self):
        return False

    @property
    def shipping_method(self):
        return 'mock_shipping'

    def net(self, items):
        return 100

    def vat(self, items):
        return 50

    def cart_items(self, items):
        cart_items = []

        uid = 'foo-uid'
        title = u'Le item'
        count = 5
        price = 150
        url = u'http://foo'

        item = self.item(uid, title, count, price, url)
        cart_items.append(item)

        return items


class TestCartDataProvider(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)

        # setup mocks
        alsoProvides(self.portal, ICartItem)
        provideAdapter(MockShipping, name='mock_shipping')
        provideAdapter(MockCartDataProvider)
        provideAdapter(MockCartItemState)
        self.cart_data_provider = getMultiAdapter(
            (self.portal, self.request), interface=ICartDataProvider)
        self.cart_item_state = getMultiAdapter(
            (self.portal, self.request), interface=ICartItemState)

    def test_validate_set(self):
        self.assertEquals(
            self.cart_data_provider.validate_set('foo_id'),
            {'success': True, 'error': ''}
        )

    @mock.patch('bda.plone.cart.get_object_by_uid')
    def test_validate_count(self, mock_get_object_by_uid):
        mock_get_object_by_uid.return_value = self.portal
        self.assertEquals(
            self.cart_data_provider.validate_count('foo_id', 4),
            {'success': True, 'error': ''}
        )
        self.assertEquals(
            self.cart_data_provider.validate_count('foo_id', 10),
            {
                'success': False,
                'error': 'Not enough items available, abort.'
            }
        )

    def test_shipping(self):
        items = []
        self.assertEquals(self.cart_data_provider.shipping(items), 10)

    def test_item(self):
        self.assertEquals(
            self.cart_data_provider.item(
                'foo-uid', u'Le item', 5, 70.0, 'http://foo'),
            {
                'cart_item_uid': 'foo-uid',
                'cart_item_title': u'Le item',
                'cart_item_count': 5,
                'cart_item_price': '70.00',
                'cart_item_location:href': 'http://foo',
                'cart_item_preview_image:src': '',
                'cart_item_comment': '',
                'cart_item_description': '',
                'cart_item_quantity_unit': '',
                'cart_item_alert': '',
                'comment_required': False,
                'quantity_unit_float': False,
                'no_longer_available': False,
            }
        )

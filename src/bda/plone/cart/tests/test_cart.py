import mock
import unittest2 as unittest
from bda.plone.cart.tests import Cart_INTEGRATION_TESTING
from bda.plone.cart.tests import set_browserlayer
from bda.plone.cart import CartDataProviderBase
from bda.plone.cart import CartItemDataProviderBase
from bda.plone.cart import CartItemStateBase
from bda.plone.cart.interfaces import ICartDataProvider
from bda.plone.cart.interfaces import ICartItem
from bda.plone.cart.interfaces import ICartItemState
from bda.plone.shipping.tests.test_shipping import MockShipping
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.uuid.interfaces import IUUID
from zope.component import adapter
from zope.component import provideAdapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


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

    def validate_set(self, uid):
        return {'success': True, 'error': ''}

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


@adapter(ICartItem)
class MockCartItemDataProvider(CartItemDataProviderBase):
    """Mock implementation of ICartItemDataProvider.
    """

    @property
    def cart_count_limit(self):
        return 10


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
        provideAdapter(MockCartItemDataProvider)
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
                'update': False,
                'success': False,
                'error': u'Not enough items available, abort.'
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


class TestHelpers(unittest.TestCase):
    """Test helper methods."""
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)

        # create an object for testing
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Document', 'doc')
        self.doc = self.portal['doc']

    def test_ascur(self):
        from bda.plone.cart import ascur

        self.assertEquals(ascur(5.0), '5.00')
        self.assertEquals(ascur(5.0, comma=True), '5,00')

    def test_extractitems_malformed_items(self):
        from bda.plone.cart import extractitems

        self.assertRaises(IndexError, extractitems, 'foo')

    def test_extractitems_has_items(self):
        from bda.plone.cart import extractitems

        items = 'uid-1:5,uid-2:100,uid-3:7'
        self.assertEquals(
            extractitems(items),
            [('uid-1', 5, '', ), ('uid-2', 100, '', ), ('uid-3', 7, '', )]
        )

    def test_aggregate_cart_item_count_non_existing_uid(self):
        from bda.plone.cart import aggregate_cart_item_count

        items = [
            ('uid-1', 5, 'no comment', ),
            ('uid-2', 100, 'no comment', ),
            ('uid-1', 7, 'no comment', )
        ]

        self.assertEquals(aggregate_cart_item_count('uid-foo', items), 0)

    def test_aggregate_cart_item_count_matching_uid(self):
        from bda.plone.cart import aggregate_cart_item_count

        items = [
            ('uid-1', 5, 'no comment', ),
            ('uid-2', 100, 'no comment', ),
            ('uid-1', 7, 'no comment', )
        ]

        self.assertEquals(aggregate_cart_item_count('uid-1', items), 12)

    def test_get_catalog_brain(self):
        from bda.plone.cart import get_catalog_brain

        self.assertEquals(get_catalog_brain(self.portal, 'foo'), None)
        brain = get_catalog_brain(self.portal, IUUID(self.doc))
        self.assertEquals(brain.getObject(), self.doc)

    def test_get_object_by_uid(self):
        from bda.plone.cart import get_object_by_uid

        self.assertEquals(get_object_by_uid(self.portal, 'foo'), None)
        obj = get_object_by_uid(self.portal, IUUID(self.doc))
        self.assertEquals(obj, self.doc)


class TestCookie(unittest.TestCase):
    layer = Cart_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)

    def _set_cookie(self, value):
        # set cookie on the request
        self.request.cookies['cart'] = value

    def test_readcookie_no_cookie(self):
        from bda.plone.cart import readcookie

        self.assertEquals(readcookie(self.request), '')

    def test_readcookie_has_cookie(self):
        from bda.plone.cart import readcookie

        self._set_cookie('uid-1:5,uid-2:100,uid-3:7')
        self.assertEquals(
            readcookie(self.request), 'uid-1:5,uid-2:100,uid-3:7')

    def test_deletecookie(self):
        from bda.plone.cart import deletecookie

        self.assertEquals(self.request.response.cookies, {})
        deletecookie(self.request)
        cookie = self.request.response.cookies['cart']
        self.assertEquals(cookie['value'], 'deleted')

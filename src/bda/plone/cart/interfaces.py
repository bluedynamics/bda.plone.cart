from zope.interface import (
    Interface,
    Attribute,
)


class ICartDataProvider(Interface):

    data = Attribute(u"Cart data as list of dicts.")

    disable_max_article = Attribute(u"Flag whether to disable max article "
                                    u"limit.")

    summary_total_only = Attribute(u"Flag whether to show total sum only in "
                                   u"summary.")

    include_shipping_costs = Attribute(u"Flag whether to display shipping "
                                       u"costs.")

    shipping_method = Attribute(u"Current shipping method identifyer.")

    checkout_url = Attribute(u"URL to checkout view.")

    cart_url = Attribute(u"URL to cart view.")

    currency = Attribute(u"Currency.")

    def validate_set(uid):
        """Validate if setting item with UID is allowed.

        return {
            'success': [True|False],
            'error': 'Error message if no success',
        }
        """

    def validate_count(uid, count):
        """Validate if setting n items with UID is allowed.

        return {
            'success': [True|False],
            'error': 'Error message if no success',
        }
        """

    def net(items):
        """Calculate net sum of cart items.
        """

    def vat(items):
        """Calculate vat sum of cart items.
        """

    def shipping(items):
        """Calculate shipping costs for cart items.
        """

    def cart_items(items):
        """Return list of dicts with format returned by ``self.item``.
        """

    def item(uid, title, count, price, url, comment='', description='',
             comment_required=False, quantity_unit_float=False,
             quantity_unit='', preview_image_url=''):
        """Create cart item entry for JSON response.

        @param uid: catalog uid
        @param title: string
        @param count: item count as int
        @param price: item price as float
        @param url: item URL
        @param comment: item comment
        @param description: item description
        @param comment_required: Flag whether comment is required
        @param quantity_unit_float: Flag whether item count can be float
        @param quantity_unit: Quantity unit
        @param preview_image_url: URL for item preview image
        """


class ICartItemDataProvider(Interface):
    """Provide information relevant for being cart item.
    """
    net = Attribute(u"Item net price as float")

    vat = Attribute(u"Item vat as float")

    display_gross = Attribute(u"Flag whether whether to display gross "
                              u"instead of net")

    comment_enabled = Attribute(u"Flag whether customer comment can be added "
                                u"when adding buyable to cart")

    comment_required = Attribute(u"Flag whether comment input is required in "
                                 u"order to add buyable to cart")

    quantity_unit_float = Attribute(u"Flag whether quantity unit value is "
                                    u"allowed as float")

    quantity_unit = Attribute(u"Quantity unit")



class ICartItemPreviewImage(Interface):
    """ provides preview image url for cart item
    """

    url = Attribute(u"Item preview image url")

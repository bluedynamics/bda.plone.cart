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
    
    checkout_url = Attribute(u"URL to checkout view.")
    
    cart_url = Attribute(u"URL to cart view.")
    
    def validate_count(uid, count):
        """Validate if ordering n items of UID is allowed.
        """


class ICartItemDataProvider(Interface):
    """Provide information relevant for being cart item.
    """
    net = Attribute(u"Item net price as float")
    
    vat = Attribute(u"Item vat as float")
    
    # XXX
    #currency = Attribute(u"Item currency")
    
    display_gross = Attribute(u"Flag whether whether to display gross "
                              u"instead of net")
    
    comment_enabled = Attribute(u"Flag whether customer comment can be added "
                                u"when adding buyable to cart")
    
    comment_required = Attribute(u"Flag whether comment input is required in "
                                 u"order to add buyable to cart")
    
    quantity_unit_float = Attribute(u"Flag whether quantity unit value is "
                                    u"allowed as float")
    
    # XXX
    #quantity_label = Attribute(u"Quantity label")
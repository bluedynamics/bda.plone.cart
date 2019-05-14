/* jslint browser: true */
/* global jQuery, bdajax, createCookie, readCookie */
// Dependencies: jQuery, cookie_functions.js

(function($, bdajax) {
    "use strict";

    var CART_EXECUTION_CONTEXT = null,
        CART_EXECUTION_URL = null,
        CART_PORTLET_IDENTIFYER = '#portlet-cart',
        CART_VIEWLET_IDENTIFYER = '#cart_viewlet',
        UID_DELIMITER = "|",
        COUNT_DELIMITER = ":";

    function Cart() {
        // flag whether cart contains items which are no longer available
        this.no_longer_available = false;
        // initially nothing addable, real value gets delivered via cart data
        this.cart_max_article_count = 0;
        // default translation messages
        this.messages = {
            'total_limit_reached': "Total limit reached",
            'not_a_number': "Input not a number",
            'max_unique_articles_reached': "Unique article limit reached",
            'comment_required': "Comment is required",
            'integer_required': "Input not an integer",
            'no_longer_available': "One or more items in cart are only " +
                                   "partly or no longer available. Please " +
                                   "update or remove related items",
            'cart_item_added': "Item has been added to cart",
            'cart_item_updated': "Item has been updated in cart",
            'cart_item_removed': "Item has been removed from cart"
        };
        this.last_cart_item_count_focus = null;
    };

    Cart.prototype.init = function() {
        this.cart_node = $('#cart').get(0);
        if (!this.cart_node) {
            return;
        }
        var template_sel = '#cart_item_template .cart_item';
        this.item_template = $($(template_sel).get(0)).clone();
        $('#cart_item_template').remove();
    };

    Cart.prototype.add = function(uid, count, comment) {
        if (!this.validateOverallCountAdd(count)) {
            return;
        }
        this.writecookie(uid, count, comment, true);
        this.query(uid);
    };

    Cart.prototype.set = function(uid, count, comment) {
        if (!this.validateOverallCountSet(uid, count)) {
            return;
        }
        this.writecookie(uid, count, comment, false);
        this.query(uid);
    };

    Cart.prototype.writecookie = function(uid, count, comment, add) {
        // XXX: support cookie size > 4096 by splitting up cookie
        count = Number(count);
        // item uid consists of ``object_uid;comment``
        uid = uid + UID_DELIMITER + comment;
        var items = this.items();
        var existent = false;
        var itemuid;

        for (itemuid in items) {
            if (!itemuid) {
                continue;
            }
            if (uid === itemuid) {
                if (add) {
                    items[itemuid] += count;
                } else {
                    items[itemuid] = count;
                }
                existent = true;
                break;
            }
        }
        if (!existent) {
            items[uid] = Number(count);
        }
        var cookie = '';
        for (itemuid in items) {
            if (!itemuid || items[itemuid] === 0) {
                continue;
            }
            cookie = cookie + itemuid + COUNT_DELIMITER + String(items[itemuid]) + ',';
        }
        if (cookie) {
            cookie = cookie.substring(0, cookie.length - 1);
        }
        if (cookie.length > 4096) {
            bdajax.error(cart.messages.max_unique_articles_reached);
            return;
        }
        createCookie('cart', cookie);
    };

    Cart.prototype.render = function(data) {
        this.cart_max_article_count = data.cart_settings.cart_max_article_count;
        if (data.cart_items.length === 0) {
            if (!data.cart_settings.hide_cart_if_empty) {
                $(CART_PORTLET_IDENTIFYER).css('display', 'block');
                $(CART_VIEWLET_IDENTIFYER).css('display', 'block');
            } else {
                $(CART_PORTLET_IDENTIFYER).css('display', 'none');
                $(CART_VIEWLET_IDENTIFYER).css('display', 'none');
            }
            $('#cart_items', this.cart_node).css('display', 'none');
            $('#cart_no_items', this.cart_node).css('display', 'block');
            $('#cart_summary', this.cart_node).css('display', 'none');
            $('.cart_total_count').html(0);
        } else {
            $(CART_PORTLET_IDENTIFYER).css('display', 'block');
            $(CART_VIEWLET_IDENTIFYER).css('display', 'block');
            $('#cart_no_items', this.cart_node).css('display', 'none');
            $('#cart_items', this.cart_node).empty();
            $('#cart_items', this.cart_node).css('display', 'block');
            var render_no_longer_available = false;
            var cart_total_count = 0;
            var to_focus = null;
            for (var i = 0; i < data.cart_items.length; i++) {
                var cart_item = $(this.item_template).clone();
                var cart_item_data = data.cart_items[i];
                // item control flags
                var quantity_unit_float = cart_item_data.quantity_unit_float;
                var comment_required = cart_item_data.comment_required;
                var no_longer_available = cart_item_data.no_longer_available;
                // delete item control flags from cart_item_data
                delete cart_item_data.quantity_unit_float;
                delete cart_item_data.comment_required;
                delete cart_item_data.no_longer_available;
                if (no_longer_available) {
                    $('input', cart_item).prop('disabled', true);
                    $('input.cart_item_count', cart_item)
                        .prop('disabled', false)
                        .css('background-color', 'red');
                    render_no_longer_available = true;
                }
                for (var item in cart_item_data) {
                    var attribute = '';
                    var css = '.' + item;
                    if (item.indexOf(COUNT_DELIMITER) !== -1) {
                        attribute = item.substring(item.indexOf(COUNT_DELIMITER) + 1,
                                                   item.length);
                        css = css.substring(0, item.indexOf(COUNT_DELIMITER) + 1);
                    }
                    var value = cart_item_data[item];
                    if (item === 'cart_item_comment' && !value) {
                        $('.cart_item_comment_wrapper', cart_item)
                            .hide().find('*').hide();
                    }
                    if (item === 'cart_item_discount' && value === 0) {
                        $('.cart_item_discount_wrapper', cart_item)
                            .hide().find('*').hide();
                    }
                    if (item === 'cart_item_alert') {
                        $('.cart_item_alert', cart_item).show();
                    }
                    if (css === '.cart_item_preview_image' && value === '') {
                        $('.cart_item_preview_image', cart_item).hide();
                    }
                    var is_count = item === 'cart_item_count';
                    if (is_count) {
                        cart_total_count += value;
                    }
                    var placeholder = $(css, cart_item);
                    $(placeholder).each(function(e) {
                        // case set attribute of element
                        if (attribute !== '') {
                            $(this).attr(attribute, value);
                        // case element is input
                        } else if (this.tagName.toUpperCase() === 'INPUT') {
                            // check if comment and set required class
                            var is_comment = item === 'cart_item_comment';
                            if (is_comment && comment_required) {
                                $(this).addClass('required');
                            }
                            // check if item count
                            if (is_count) {
                                // check if quantity unit float
                                if (quantity_unit_float) {
                                    $(this).addClass('quantity_unit_float');
                                    value = cart.round(value);
                                }
                                // check if focus should be set
                                var focus = cart.last_cart_item_count_focus;
                                if (focus === cart_item_data.cart_item_uid) {
                                    // need to remember element here and focus
                                    // later, elem not in DOM tree yet.
                                    to_focus = $(this);
                                }
                            }
                            $(this).attr('value', value);
                            $(this).val(value);
                        // case set element text
                        } else {
                            // not count element, set value
                            if (!is_count) {
                                $(this).html(value);
                            // if count element has 'style' attribute 'display'
                            // set to 'none', do not change it's value. This is
                            // necessary for cart item removal.
                            } else {
                                var mode = $(this).css('display');
                                if (mode.toLowerCase() !== 'none') {
                                    $(this).html(value);
                                }
                            }
                        }
                    });
                }
                $('#cart_items', this.cart_node).append(cart_item);
            }
            if (to_focus) {
                to_focus.focus();
                var focus_val = to_focus.val();
                to_focus.val('').val(focus_val);
            }
            var cart_summary = $('#cart_summary', this.cart_node).get(0);
            for (var item in data.cart_summary) {
                var css = '.' + item;
                var value = data.cart_summary[item];
                $(css, cart_summary).html(value);
            }
            var discount_sel = '#cart_summary .discount';
            if (data.cart_summary.discount_total_raw > 0) {
                $(discount_sel, this.cart_node).css('display', 'table-row');
            } else {
                $(discount_sel, this.cart_node).css('display', 'none');
            }
            var shipping_sel = '#cart_summary .shipping';
            if (data.cart_settings.include_shipping_costs) {
                $(shipping_sel, this.cart_node).css('display', 'table-row');
            } else {
                $(shipping_sel, this.cart_node).css('display', 'none');
            }
            $('#cart_summary', this.cart_node).css('display', 'block');
            $('.cart_total_count').html(cart_total_count);
            if (render_no_longer_available) {
                this.no_longer_available = true;
                bdajax.warning(cart.messages.no_longer_available);
            } else {
                this.no_longer_available = false;
            }
        }
    };

    Cart.prototype.bind = function(context) {
        $('#cart_viewlet_summary a', context)
            .unbind('click')
            .bind('click', function(e) {
                e.preventDefault();
                var container = $(this).closest('#cart_viewlet');
                var cart_wrapper = $('#cart_viewlet_details', container);
                if (cart_wrapper.is(':visible')) {
                    cart_wrapper.hide();
                } else {
                    cart_wrapper.show();
                }
            });
        $('.prevent_if_no_longer_available', context)
            .unbind('click')
            .bind('click', function(e) {
                if (cart.no_longer_available) {
                    e.preventDefault();
                    bdajax.warning(cart.messages.no_longer_available);
                }
            });
        $('.add_cart_item', context).each(function() {
            $(this).unbind('click').bind('click', function(e) {
                e.preventDefault();
                cart.add_cart_item(this);
            });
        });
        $('.update_cart_action', context).each(function() {
            $(this).unbind('click').bind('click', function(e) {
                e.preventDefault();
                cart.update_cart_item(this, '.cart_item_content');
            });
        });
        $('.remove_from_cart_action', context).each(function() {
            $(this).unbind('click').bind('click', function(e) {
                e.preventDefault();
                cart.update_cart_item(this, '.cart_item_remove');
            });
        });
        var defer_timer = null;
        function bind_key_changed(parent_selector) {
            $(this).unbind('keyup').bind('keyup', function(e) {
                var kc = e.keyCode;
                if ((kc >= 48 && kc <= 57) ||
                    (kc >= 96 && kc <= 105) ||
                    kc == 190 || kc == 110 || kc == 8 || kc == 46) {
                    clearTimeout(defer_timer);
                    var parent = cart.find_extraction_parent($(this));
                    var uid = $('.cart_item_uid', parent).first().text();
                    cart.last_cart_item_count_focus = uid;
                    defer_timer = setTimeout(function () {
                        cart.update_cart_item(this, );
                    }.bind(this), 500);
                }
            });
        }
        $('.buyable .cart_item_count', context).each(function() {
            bind_key_changed('.buyable');
        });
        $('.cart_item_content .cart_item_count', context).each(function() {
            bind_key_changed('.cart_item_content');
        });
    };

    Cart.prototype.add_cart_item = function(node) {
        var defs;
        try {
            defs = cart.extract(node, '.buyable');
        } catch (ex) {
            bdajax.error(ex.message);
            return;
        }
        var uid = defs[0];
        var count = defs[1];
        var items = cart.items();
        for (var item in items) {
            if (!item) {
                continue;
            }
            var item_uid = item.split(UID_DELIMITER)[0];
            if (uid === item_uid) {
                count += items[item];
            }
        }
        var params = {
            uid: defs[0],
            count: count + '',
            comment: defs[2]
        };
        if (CART_EXECUTION_CONTEXT) {
            params.execution_context = CART_EXECUTION_CONTEXT;
        }
        var $node = $(node);
        var status_message = $node.hasClass('show_status_message');
        bdajax.request({
            url: CART_EXECUTION_URL + '/validate_cart_item',
            params: params,
            type: 'json',
            success: function(data) {
                if (data.success === false) {
                    bdajax.info(decodeURIComponent(data.error));
                    if (data.update) {
                        cart.query();
                    }
                } else {
                    cart.add(defs[0], defs[1], defs[2]);
                    var evt = $.Event('cart_modified');
                    evt.uid = defs[0];
                    evt.count = count;
                    $('*').trigger(evt);
                    if (status_message) {
                        cart.status_message(
                            $node, cart.messages.cart_item_added);
                    }
                }
            }
        });

    };

    Cart.prototype.update_cart_item = function(node, definitions_selector) {
        var defs;
        try {
            defs = cart.extract(node, definitions_selector);
        } catch (ex) {
            bdajax.error(ex.message);
            return;
        }
        var uid = defs[0];
        var count = defs[1];
        if (count > 0) {
            var items = cart.items();
            for (var item in items) {
                if (!item) {
                    continue;
                }
                if (item === uid + UID_DELIMITER + defs[2]) {
                    continue;
                }
                var item_uid = item.split(UID_DELIMITER)[0];
                if (uid === item_uid) {
                    count += items[item];
                }
            }
        }
        var params = {
            uid: defs[0],
            count: count + '',
            comment: defs[2]
        };
        if (CART_EXECUTION_CONTEXT) {
            params.execution_context = CART_EXECUTION_CONTEXT;
        }
        var $node = $(node);
        var status_message = $node.hasClass('show_status_message');
        bdajax.request({
            url: CART_EXECUTION_URL + '/validate_cart_item',
            params: params,
            type: 'json',
            success: function(data) {
                if (data.success === false) {
                    bdajax.info(decodeURIComponent(data.error));
                    if (data.update) {
                        cart.query();
                    }
                } else {
                    cart.set(defs[0], defs[1], defs[2]);
                    var evt = $.Event('cart_modified');
                    evt.uid = defs[0];
                    evt.count = count;
                    $('*').trigger(evt);
                    if (status_message && defs[1] === 0) {
                        cart.status_message(
                            $node, cart.messages.cart_item_removed);
                    } else if (status_message && defs[1] !== 0) {
                        cart.status_message(
                            $node, cart.messages.cart_item_updated);
                    }
                }
            }
        });
    };

    Cart.prototype.round = function(x) {
        var ret = (Math.round(x * 100) / 100).toString();
        ret += (ret.indexOf('.') === -1) ? '.00' : '00';
        return ret.substring(0, ret.indexOf('.') + 3);
    };

    Cart.prototype.find_extraction_parent = function($node) {
        // Find the first parent node, which has a childelement with class
        // cart_item_uid
        var parent = $node.parent();
        if ($('.cart_item_uid', parent).length === 0) {
            return this.find_extraction_parent(parent);
        }
        return parent;
    };

    Cart.prototype.extract = function(node, parent_selector) {
        node = $(node);
        var parent = node.closest(parent_selector)
        var uid = $('.cart_item_uid', parent).first().text();
        var count_node = $('.cart_item_count', parent).get(0);
        var count;
        var tagname = count_node.tagName.toUpperCase();
        if (tagname === 'INPUT' || tagname === 'SELECT') {
            count = $(count_node).val();
        } else {
            count = $(count_node).text();
        }
        count = Number(count);
        if (isNaN(count)) {
            throw {
                name: 'Number Required',
                message: cart.messages.not_a_number
            };
        }
        var force_int = !$(count_node).hasClass('quantity_unit_float');
        if (force_int && count > 0 && count % 1 !== 0) {
            throw {
                name: 'Integer Required',
                message: cart.messages.integer_required
            };
        }
        var comment_node = $('.cart_item_comment', parent).get(0);
        var comment = '';
        if (comment_node) {
            if (comment_node.tagName.toUpperCase() === 'INPUT') {
                comment = $(comment_node).val();
                if ($(comment_node).hasClass('required') && !comment.trim()) {
                    throw {
                        name: 'Comment Required',
                        message: cart.messages.comment_required
                    };
                }
            } else {
                comment = $(comment_node).text();
            }
            comment = encodeURIComponent(comment);
        }
        return [uid, count, comment];
    };

    Cart.prototype.cookie = function() {
        // XXX: support cookie size > 4096 by splitting up cookie
        var cookie = readCookie('cart');
        if (cookie === null) {
            cookie = '';
        }
        return cookie;
    };

    /*
     * items is a key/value mapping in format items['obj_uid;comment'] = count
     */
    Cart.prototype.items = function() {
        var cookie = this.cookie();
        var cookieitems = cookie.split(',');
        var items = {};
        for (var i = 0; i < cookieitems.length; i++) {
            var item = cookieitems[i].split(COUNT_DELIMITER);
            items[item[0]] = Number(item[1]);
        }
        return items;
    };

    Cart.prototype.validateOverallCountAdd = function(addcount) {
        var count = 0;
        var items = this.items();
        for (var item in items) {
            if (!item) {
                continue;
            }
            count += items[item];
        }
        count += Number(addcount);
        if (count > this.cart_max_article_count + 1) {
            var msg;
            msg = cart.messages.total_limit_reached;
            bdajax.info(decodeURIComponent(msg));
            return false;
        }
        return true;
    };

    Cart.prototype.validateOverallCountSet = function(uid, setcount) {
        var count = 0;
        var items = this.items();
        for (var item in items) {
            if (!item) {
                continue;
            }
            var item_uid = item.split(UID_DELIMITER)[0];
            if (uid === item_uid) {
                continue;
            }
            count += items[item];
        }
        count += Number(setcount);
        if (count > this.cart_max_article_count + 1) {
            var msg;
            msg = cart.messages.total_limit_reached;
            bdajax.info(decodeURIComponent(msg));
            return false;
        }
        return true;
    };

    Cart.prototype.status_message = function(elem, message) {
        var show_message = function(anchor_elem, status_message) {
            var offset = anchor_elem.offset();
            var width = anchor_elem.width();
            var height = anchor_elem.height();
            var body_width = $('body').width();
            var top = offset.top + height + 3;
            var right = body_width - offset.left - width - 8;
            status_message.css('top', top);
            status_message.css('right', right);
            $('body').append(status_message);
            status_message.fadeIn(500, function() {
                setTimeout(function() {
                    status_message.fadeOut(500, function() {
                        status_message.remove();
                    });
                }, 2000);
            });
        };
        var status_message = $('<div class="cart_status_message"></div>');
        status_message.html(message);
        show_message(elem, status_message);
    };

    /*
     * @param uid_changed: uid of item which was added or set before querying
     */
    Cart.prototype.query = function(uid_changed) {
        // trigger cart_changed event on elements with
        // css class ``cart_item_${uid_changed}``
        if (uid_changed) {
            var evt = $.Event('cart_changed');
            var selector = '.cart_item_' + uid_changed;
            $(selector).trigger(evt);
        }
        if (!this.cart_node) {
            return;
        }
        if (document.location.href.indexOf('/portal_factory/') !== -1) {
            return;
        }
        var params = {};
        if (CART_EXECUTION_CONTEXT) {
            params.execution_context = CART_EXECUTION_CONTEXT;
        }
        bdajax.request({
            url: CART_EXECUTION_URL + '/cartData',
            params: params,
            type: 'json',
            success: function(data) {
                cart.render(data);
                cart.bind();
            }
        });
    };

    var cart = new Cart();
    window.bda_plone_cart = cart;

    $(document).ready(function() {
        var execution_context = $('.cart_execution_context');
        if (execution_context.length) {
            CART_EXECUTION_CONTEXT = execution_context.text();
        }
        var execution_url = $('#cart');
        if (execution_url.length) {
            CART_EXECUTION_URL = execution_url.data('context-url');
        }
        cart.init();
        cart.query();
        if (window.Faceted !== undefined) {
            $(window.Faceted.Events).bind(window.Faceted.Events.AJAX_QUERY_SUCCESS, function(e){
                cart.bind();
            });
        }
        $.extend(bdajax.binders, {
            cart_binder: cart.bind
        });
    });

})(jQuery, bdajax);

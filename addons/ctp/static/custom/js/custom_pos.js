odoo.define('berdikari.pos', function(require){
    "use strict";

    var session = require('web.session');
    var Backbone = window.Backbone;
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var QWeb = core.qweb;
    var _t = core._t;
    var obj = screens.ProductListWidget.include({
        init: function(group, options){
            var self = this;
            this._super(group, options);

            this.click_product_handler = function(e){
                var article = $(this).parent();
                var product_id = article.data('product-id');
//                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                var product = self.pos.db.get_product_by_id(product_id);
                options.click_product_action(product);
            };

            this.click_product_qty = function(e){
                var article = $(this).parent();
                var product_id = article.data('product-id');
//                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                var product = self.pos.db.get_product_by_id(product_id);
                options.click_product_action(product);

                var url = '/web#id=' + product_id + '&model=product.template&view_type=form&menu_id=';
                var win = window.open(url, '_blank');
                win.focus();
            };
        },
        renderElement: function() {
            var el_str  = QWeb.render(this.template, {widget: this});
            var el_node = document.createElement('div');
                el_node.innerHTML = el_str;
                el_node = el_node.childNodes[1];

            if(this.el && this.el.parentNode){
                this.el.parentNode.replaceChild(el_node,this.el);
            }
            this.el = el_node;

            var list_container = el_node.querySelector('.product-list');
            for(var i = 0, len = this.product_list.length; i < len; i++){
                var product_node = this.render_product(this.product_list[i]);

                var list_product_img = product_node.getElementsByClassName('product-img');
                if (list_product_img.length > 0) {
                    var product_img = list_product_img[0];
                    product_img.addEventListener('click',this.click_product_handler);
                }

                var list_product_name = product_node.getElementsByClassName('product-name');
                if (list_product_name.length > 0) {
                    var product_name = list_product_name[0];
                    product_name.addEventListener('click',this.click_product_qty);
                }
//                product_img.addEventListener('click',this.click_product_handler);

//                console.log('product_img length: ', product_img.length);
//                product_node.addEventListener('click',this.click_product_handler);
//                product_node.addEventListener('keypress',this.keypress_product_handler);

//                product_node.addEventListener('click',this.click_product_handler);
//                product_node.addEventListener('keypress',this.keypress_product_handler);
                list_container.appendChild(product_node);
            }
        },
    });

    return {ProductListWidget: obj};
});


//odoo.define('berdikari.context_menu_pos_product', function (require) {
//    "use strict";
//
//    var screens = require('point_of_sale.screens');
//    var obj = screens.ProductListWidget.include({
//        init: function (parent) {
////            parent.init();
//            this._super(parent);
//            console.log('####################################################');
//            console.log('####################################################');
//            console.log('####################################################');
////            this.click_product_handler = function(){
////                var product = self.pos.db.get_product_by_id(this.dataset.productId);
////                debugger;
//////                options.click_product_action(product);
////                this._super();
////            };
//        },
//    });
////    screens.define_action_button({
////        'name': 'OrderLine_Clear',
////        'widget': OrderLineClear,
////    });
//    return {
//        ProductListWidget: obj,
//    };
//});
//
////
////odoo.define('berdikari.context_menu_pos_product', function (require) {
////    'use strict';
////    var core = require('web.core');
////    var screens = require('point_of_sale.screens');
////    var _t = core._t;
////
//////    var ProductListWidget = require("point_of_sale.ProductListWidget");
////    var ProductListWidget = screens.ProductListWidget;
////    var obj = ProductListWidget.include({
//////        init: function (parent) {
////////            parent.init();
//////            this._super(parent);
////////            this.click_product_handler = function(){
////////                var product = self.pos.db.get_product_by_id(this.dataset.productId);
////////                debugger;
//////////                options.click_product_action(product);
////////                this._super();
////////            };
//////        },
//////        renderElement: function() {
//////            var el_str  = QWeb.render(this.template, {widget: this});
//////            var el_node = document.createElement('div');
//////                el_node.innerHTML = el_str;
//////                el_node = el_node.childNodes[1];
//////
//////            if(this.el && this.el.parentNode){
//////                this.el.parentNode.replaceChild(el_node,this.el);
//////            }
//////            this.el = el_node;
//////
//////            var list_container = el_node.querySelector('.product-list');
//////            for(var i = 0, len = this.product_list.length; i < len; i++){
//////                var product_node = this.render_product(this.product_list[i]);
//////                product_node.addEventListener('click',this.click_product_handler);
//////                product_node.addEventListener('keypress',this.keypress_product_handler);
//////                list_container.appendChild(product_node);
//////            }
//////        },
////    });
////
////    return obj;
////});
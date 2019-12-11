String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

odoo.define('jekdoo.char', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
//    var web = require('web');
    var Widget = require('web.Widget');
    var Session = require('web.session');
    var AbstractField = require('web.AbstractField');
//    var FormWidget = require('web.FormWidget');
    var registry = require('web.field_registry');
    var FormView = require('web.FormView');
//    var BasicModel = require('web.BasicModel');
    var FormController = require('web.FormController');

    var QWeb = core.qweb;
    var _t = core._t;

    var obj = AbstractField.extend({
        start: function (event) {
            var me = this;

            var field_name = me.name;
            var value = me.value;
            var hasil_html = '';
            if(me.mode === 'readonly') {
                hasil_html += '<span>' + value + '</span>';
            } else {
                hasil_html += '<input type="text" name="'+field_name+'" value="'+value+'" class="form-control"/>';
            }
            $(hasil_html).appendTo(me.$el);
        },
    });
    registry.add('jekdoo_char', obj);
});

$(document).ready(function() {
    var class_search2 = 'select.oe_select2_search';

    $(class_search2).select2();

    $(document).on('focus', class_search2, function(){
        $(this).select2();
    });
});
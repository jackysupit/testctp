odoo.define('jekdoo_dynamic_list.shcolumns', function (require) {
    "use strict";

    var core = require('web.core');
    var BaseImport = require('base_import.import');
    var ListController = require('web.ListController');
    var QWeb = core.qweb;
    var all_cols = [];

    ListController.include({
        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (!this.noLeaf && this.hasButtons) {
                this.$buttons.on('click', '.oe_select_columns', this.my_setup_columns.bind(this));
                this.$buttons.on('click', '.oe_dropdown_btn', this.hide_show_columns.bind(this));
                this.$buttons.on('click', '.oe_dropdown_btn2', this.apply2.bind(this));
                this.$buttons.on('click', '.oe_dropdown_menu', this.stop_event.bind(this));
            }
            if (this.$buttons) {
                this.contents = this.$buttons.find('ul#showcb');
                var columns = [];

                all_cols = [];
                _.each(this.initialState.fields, function (item) {
                    var field_name = item.name;
                    var description = item.string;
                    all_cols.push({
                        'tag': 'field',
                        'attrs': {
                            'name': field_name,
                            'description': description,
                            'modifiers': {}
                            },
                        'children': []
                    });
                });

                var cols_default = {};
                _.each(this.renderer.columns, function (item) {
                    var field_name = item.attrs.name;
                    var description = item.string;
                    cols_default[field_name] = true;
                });

                _.each(all_cols, function(node){
                   var name = node.attrs.name;
                   var description = node.attrs.description;
                   var invisible = cols_default[name];

                   columns.push({
                       'field_name': name,
                       'label': description,
                       'invisible': !invisible
                   });
               });

                this.contents.append($(QWeb.render('ColumnSelectionDropDown', {widget: this, columns: columns})));
            }
        },

        my_setup_columns: function () {
            $("#showcb").toggle();
        },
        stop_event: function (e) {
            e.stopPropagation();
        },

        hide_show_columns: function () {
            $("#showcb").hide();
            this.setup_columns();
            // var state = this.model.get(this.handle);
            // this.renderer.updateState(state, {reload: true});
        },
        apply2: function () {
            alert('start apply2');

            var route_apply2 = '/jekdoo/apply2'
            var ajax = require('web.ajax');
            ajax.jsonRpc(route_apply2, 'call').then(function(hasil){
                alert('return: ' + hasil);
            });


            //
            //    #NOTEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
            //    #//ini Javascript
                  //panggil di dalam odoo.define('nama-module'
            //    #NOTEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
            //    # Calling a method on a python model:
            //    # return this._rpc({
            //    #     model: 'some.model',
            //    #     method: 'some_method',
            //    #     args: [some, args],
            //    # });
            //    # Directly calling a controller:
            //    # return this._rpc({
            //    #     route: '/some/route/',
            //    #     params: { some: kwargs},
            //    # });
        },
        setup_columns: function () {
            var self = this;
            var my_columns = [];
            _.each(this.contents.find('li.item_column'), function(item){
               var checkbox_item = $(item).find('input');
               var is_checked = checkbox_item.prop('checked');
               if (is_checked) {
                   my_columns.push(checkbox_item.data('name'));
               }
            });

            var state = this.model.get(this.handle);
            var data = {
                'model': state.model,
                'columns': JSON.stringify(my_columns)
            };
            var url = '/jekdoo/set_dynamic_list';
            $.post(url, data, function (hasil) {
                hasil = JSON.parse(hasil);
                var status = hasil.status;
                if(status) {
                  window.location.reload();
                } else {
                  alert(hasil.msg);
                }
            });
        },
    });

    $(document).click(function () {
        $("#showcb").hide();
    });
});

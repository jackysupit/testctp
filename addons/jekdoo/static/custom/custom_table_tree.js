// First, checks if it isn't implemented yet.
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

odoo.define('x_jekdoo_table_tree_js', function (require) {
    var AbstractController = require('web.AbstractController');
    var AbstractModel = require('web.AbstractModel');
    var AbstractRenderer = require('web.AbstractRenderer');
    var AbstractView = require('web.AbstractView');

    var MapController = AbstractController.extend({});

    var MapModel = AbstractModel.extend({
        get: function() {
            return {
                model: this.model,
                kategori: this.kategori,
            };
        },
        load: function(params) {
            this.displayContacts = true;
            return this._load(params);
        },
        _load: function(params) {
            this.domain = params.domain || this.domain || [];
            if(this.displayContacts) {
                var self = this;

                this._rpc({
                        model: 'ir.model',
                        method: 'search_read',
                        fields: ['id','name'],
                        domain: [['model', '=', 'product.category']],
                        limit: 1,
                    })
                    .then(function(result){
                        self.model = result;
                    });

                return this._rpc({
                        model: 'product.category',
                        method: 'search_read',
                        fields: ['id','name','parent_id','child_id'],
                        domain: this.domain,
                    })
                    .then(function(result){
                        self.kategori = result;
                    });
            }
            this.kategori = [];
            this.model = [];
            return $.when();
        }
    });

    var kategori_json = [];
    var MapRenderer = AbstractRenderer.extend({
        className: "o_jekdoo_table_tree_view",
        on_attach_callback: function() {
            $('#the_jstree').jstree({
              "core" : {
                "animation" : 0,
                "check_callback" : true,
                "themes" : { "stripes" : true },
                'data' : kategori_json
              },
              "types" : {
                "#" : {
                  "max_children" : 1,
                  "max_depth" : 4,
                  "valid_children" : ["root"]
                },
                "root" : {
                  "icon" : "glyphicon glyphicon-folder-open",
                  "valid_children" : ["default"]
                },
                "default" : {
                  "valid_children" : ["default","file"]
                },
                "file" : {
                  "icon" : "glyphicon glyphicon-file",
                  "valid_children" : []
                }
              },
              "plugins" : [
                "dnd", "search",
                "state", "types", "wholerow"
              ]
            });
        },
        _render: function() {
            this.$el.html("<h1 class='text-center'>Product Categories Tree</h1>");
            var kategori = this.state.kategori;
            kategori_json = [];
            if(kategori) {
                $.each(kategori, function(index, item){
                    kategori_json.push(
                        {
                            "id": item.id,
                            "parent": item.parent_id === false ? "#" : item.parent_id[0],
                            "text": item.name
                        }
                    );
                });
            }
            this.$el.append("<div id='the_jstree'>No Records</div>");
            return $.when();
        }
    });


    var TableTreeView = AbstractView.extend({
        config: {
            Model: MapModel,
            Controller: MapController,
            Renderer: MapRenderer,
        },
        view_type: 'jekdoo_table_tree',
        icon: 'fa-tree',
        cssLibs: [
            '/jekdoo/static/3rd/jsTree/themes/default/style.css',
        ],
        jsLibs: [
            '/jekdoo/static/3rd/jsTree/jstree.js',
        ]
    });

    var viewRegistry = require('web.view_registry');
    viewRegistry.add('jekdoo_table_tree', TableTreeView);

    return viewRegistry;
});
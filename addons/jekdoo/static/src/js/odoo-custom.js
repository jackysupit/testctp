var juke_number = function (value) {
    var result = "0";
    var amount = value;
    var amount_to_format = 0;

    ribu1 = 1000;
    juta1 = 1000 * ribu1;
    milyar1 = 1000 * juta1;
    trilyun1 = 1000 * milyar1;

    if (value < juta1) {
        amount_to_format = amount;
        ext = "";
    } else if (value < milyar1) {
        amount_to_format = amount / juta1;
        ext = " JT";
    } else if (value < trilyun1) {
        amount_to_format = amount / milyar1;
        ext = " M";
    } else {
        amount_to_format = amount / trilyun1;
        ext = " T";
    }

    var val = amount_to_format;
    var val_str = "";
    if (amount_to_format % 1 == 0) {
        val_str = val;
//            val_str = parseFloat(val);
        val_str = val_str.toFixed(0);
        val_str = addCommas(val_str);
    } else {
        if (typeof formatMoney2 === 'function') {
            val_str = formatMoney2((val + '').replaceAll(',',''), 2, ".", ",");
        } else {
            if (typeof $.number === 'function') {
                val_str = $.number(val, 2);
            } else {
                val_str = parseFloat(val);
                val_str = val_str.toFixed(2);
                val_str = addCommas(val_str);
            }
        }
    }
    result = val_str + ext;
    return result;
}
var juke_app_title = 'Berdikari';
var default_jekdoo_max_upload_size = 25;
var jekdoo_max_upload_size = default_jekdoo_max_upload_size;
var pipeline_tree_url = '/';

var is_admin = false;
var is_me_an_am = false;
var is_me_an_am_head = false;
var file_extention_allowed = 'doc, docx, xls, xlsx, pdf, jpg, png';
var el_date = false;
var obj_date = false;

//ganti title window
odoo.define('juke_crm.ganti_odoo', function (require) {
    'use strict';
    var core = require('web.core');
    var _t = core._t;

    var AbstractWebClient = require("web.AbstractWebClient");
    var obj = AbstractWebClient.include({
        init: function (parent) {
            this._super();

            this.set('title_part', {"zopenerp": juke_app_title});
        },
    });

    return obj;
});

//datepicker, set obj_date value to empty on error
//odoo.define('juke_crm.dialog', function (require) {
//    'use strict';
//    var core = require('web.core');
//    var _t = core._t;
//
//    var webDialog = require("web.Dialog");
//    var myDialog = webDialog.include({
//        open: function () {
//            this.title = juke_app_title || 'Info';
//            this.subtitle = '';
//
//            if(el_date && (typeof el_date.hasClass === 'function') && el_date.hasClass('o_datepicker_input') ) {
//                if (typeof this.$content.html === 'function') {
//                    var msg = this.$content.html();
//                    if(msg.indexOf('Invalid Date: ') >= 0 || msg.indexOf('Invalid Due Date') >= 0) {
//                        var value = false;
//                        el_date.val(value);
////                        debugger;
//                        obj_date.readonly = false;
//                        obj_date.setValue(value);
//                        obj_date.trigger('changed');
//                        obj_date.set({'value': null});
//                        obj_date.picker.date(null);
//                    }
//                }
//            }
//            return this._super();
//        },
//    });
//
//    return myDialog;
//});

////datepicker, set obj_date var
//odoo.define('juke_crm.datepicker', function (require) {
//    'use strict';
//    var core = require('web.core');
//    var _t = core._t;
//
//    var web_datepicker = require("web.datepicker");
//    var DateWidget = web_datepicker.DateWidget;
//    var time = require('web.time');
//
//    var obj = DateWidget.include({
//        changeDatetime: function () {
//            if (this.isValid()) {
//                var oldValue = this.getValue();
//                this._setValueFromUi();
//                var newValue = this.getValue();
//                var hasChanged = !oldValue !== !newValue;
//                if (oldValue && newValue) {
//                    var formattedOldValue = oldValue.format(time.getLangDatetimeFormat());
//                    var formattedNewValue = newValue.format(time.getLangDatetimeFormat())
//                    if (formattedNewValue !== formattedOldValue) {
//                        hasChanged = true;
//                    }
//                }
//                if (hasChanged) {
//                    el_date = this.$input;
//                    obj_date = this;
//                    // The condition is strangely written; this is because the
//                    // values can be false/undefined
//                    this.trigger("datetime_changed");
//                }
//            }
//        },
//    });
//
//    return {
//        DateWidget: obj,
//    };
//});
//
////datepicker, set widget.value before validation. so it will be added into invalidFields
//odoo.define('juke_crm.webBaseRenderer', function (require) {
//    'use strict';
//    var Super = require("web.BasicRenderer");
//    var obj = Super.include({
//        canBeSaved: function (recordID) {
//            var i = 3;
//            var self = this;
//            var invalidFields = [];
//            _.each(this.allFieldWidgets[recordID], function (widget) {
//                if(typeof widget.$input !== 'undefined') {
//                    if(typeof widget.$input.hasClass === 'function') {
//                        if (widget.$input.hasClass('o_datepicker_input')) {
//                            if(!widget.$input.val()) {
//                                widget.value = false;
//                            }
//                        }
//                    }
//                }
//                var canBeSaved = self._canWidgetBeSaved(widget);
//                if (!canBeSaved) {
//                    invalidFields.push(widget.name);
//                }
//                widget.$el.toggleClass('o_field_invalid', !canBeSaved);
//            });
//            return invalidFields;
//        },
//    });
//    return obj;
//});
//
////dialog, ganti Your Odoo Session Expired
//odoo.define('juke_crm.CrashManager', function (require) {
//    'use strict';
//    var core = require('web.core');
//    var _t = core._t;
//    var QWeb = core.qweb;
//    var Dialog = require('web.Dialog');
//
//    var Super = require("web.CrashManager");
//    var obj = Super.include({
//        rpc_error: function(error) {
//            var self = this;
//            if (!this.active) {
//                return;
//            }
//            if (this.connection_lost) {
//                return;
//            }
//            if (error.data.name === "odoo.http.SessionExpiredException" || error.data.name === "werkzeug.exceptions.Forbidden") {
//                this.show_warning({type: _t("Odoo Session Expired"), data: {message: _t("Your Berdikari session expired. Please refresh the current web page.")}});
//                return;
//            }
//            this._super(error);
//        },
//    });
//
//    return obj;
//});

//saving record
//console.log('loading: juke_crm.save_record');
//odoo.define('juke_crm.save_record', function (require) {
//    'use strict';
//    var core = require('web.core');
//    var _t = core._t;
//
//    var webController = require('web.FormController');
//    var FormController = webController.include({
//        saveRecord: function() {
//            var xxx = 0;
//            var self = this;
//            return this._super.apply(this, arguments).then(function(changedFields) {
//                self.set('title', self.getTitle());
//                self._updateEnv();
//                var alert_length = 0;
//                if (_t.database.multi_lang && changedFields.length) {
//                    var fields = self.renderer.state.fields;
//                    var data = self.renderer.state.data;
//                    var alertFields = [];
//                    for (var k = 0; k < changedFields.length; k++) {
//                        var field = fields[changedFields[k]];
//                        var fieldData = data[changedFields[k]];
//                        if (field.translate && fieldData) {
//                            alertFields.push(field);
//                        }
//                    }
//                    alert_length = alertFields.length;
//                    if (alertFields.length) {
//                        self.renderer.displayTranslationAlert(alertFields);
//                    }
//                }
//                if (changedFields.length > 0 && alert_length === 0) {
//                    var modelName = self.modelName;
//                    var urlParams = new URLSearchParams(window.location.href);
//                    var model = '';
//                    if (urlParams.has('model')) {
//                        model = urlParams.get('model');
//                    }
//                    var msg = '';
//                    if (model == 'crm.lead') {
//                        if (is_admin) {
//                            //self.renderer.displayTranslationAlert(alertFields);
//                            msg = 'And YEAYYYYY!!!! We will not redirect you to the pipeline list :)';
//                        } else {
//                            window.location.href = pipeline_tree_url;
//                        }
//                    }
//                    //self.renderer.displayTranslationAlert(alertFields);
//                    msg = msg || 'Your data has been saved successfully.';
//                    self.do_notify('Success!', msg);
//                }
//                return changedFields;
//            });
//        }
//    });
//    return FormController;
//});

//validasi record
//console.log('loading: juke_crm.validasi_save');
//odoo.define('juke_crm.validasi_save', function (require) {
//    'use strict';
//    var core = require('web.core');
//    var _t = core._t;
//
//    var BasicController = require('web.BasicController');
//    var obj = BasicController.include({
//        canBeSaved: function (recordID) {
//            if (this.mode == 'readonly') {
//                console.log('override return true');
//                return true;
//            } else {
//                return this._super.apply(this, arguments);
////                return this._super(recordID);
//            }
//        },
//    });
//    return obj;
//});

////kanban summary amount
//odoo.define('juke_crm.kanban', function (require) {
//    'use strict';
//    var core = require('web.core');
//    var utils = require('web.utils');
//
//    var _t = core._t;
//
//    var xxx = 0;
//    var kanbanCol = require('web.KanbanColumnProgressBar');
//    var obj = kanbanCol.include({
//        start: function () {
//            var self = this;
//
//            this.$bars = {};
//            _.each(this.colors, function (val, key) {
//                self.$bars[val] = self.$('.bg-' + val + '-full');
//            });
//            this.$counter = this.$('.o_kanban_counter_side');
//            this.$number = this.$counter.find('b');
//
//            xxx=1;
//            if (this.currency) {
//                xxx=2;
//                var $currency = $('<span/>', {
//                    text: this.currency.symbol,
//                });
//                if (this.currency.position === 'before') {
//                    $currency.prependTo(this.$counter);
//                } else {
//                    $currency.appendTo(this.$counter);
//                }
//            }
//
//            return this._super.apply(this, arguments).then(function () {
//                // This should be executed when the progressbar is fully rendered
//                // and is in the DOM, this happens to be always the case with
//                // current use of progressbars
//
//                var subgroupCounts = {};
//                _.each(self.colors, function (val, key) {
//                    var subgroupCount = self.columnState.progressBarValues.counts[key] || 0;
//                    if (self.activeFilter === key && subgroupCount === 0) {
//                        self.activeFilter = false;
//                    }
//                    subgroupCounts[key] = subgroupCount;
//                });
//
//                self.groupCount = self.columnState.count;
//                self.subgroupCounts = subgroupCounts;
//                self.prevTotalCounterValue = self.totalCounterValue;
//                self.totalCounterValue = self.sumField ? (self.columnState.aggregateValues[self.sumField] || 0) : self.columnState.count;
//                self._notifyState();
//                self._render();
//            });
//        },
//        _render: function () {
//            var self = this;
//
//            // Update column display according to active filter
//            this.trigger_up('tweak_column', {
//                callback: function ($el) {
//                    $el.removeClass('o_kanban_group_show');
//                    _.each(self.colors, function (val, key) {
//                        $el.removeClass('o_kanban_group_show_' + val);
//                    });
//                    if (self.activeFilter) {
//                        $el.addClass('o_kanban_group_show o_kanban_group_show_' + self.colors[self.activeFilter]);
//                    }
//                },
//            });
//            this.trigger_up('tweak_column_records', {
//                callback: function ($el, recordData) {
//                    var categoryValue = recordData[self.fieldName];
//                    _.each(self.colors, function (val, key) {
//                        $el.removeClass('oe_kanban_card_' + val);
//                    });
//                    if (self.colors[categoryValue]) {
//                        $el.addClass('oe_kanban_card_' + self.colors[categoryValue]);
//                    }
//                },
//            });
//
//            // Display and animate the progress bars
//            var barNumber = 0;
//            var barMinWidth = 6; // In %
//            _.each(self.colors, function (val, key) {
//                var $bar = self.$bars[val];
//                var count = self.subgroupCounts && self.subgroupCounts[key] || 0;
//
//                if (!$bar) {
//                    return;
//                }
//
//                // Adapt tooltip
//                $bar.attr('data-original-title', count + ' ' + key);
//                $bar.tooltip({
//                    delay: '0',
//                    trigger:'hover',
//                    placement: 'top'
//                });
//
//                // Adapt active state
//                $bar.toggleClass('active progress-bar-striped', key === self.activeFilter);
//
//                // Adapt width
//                $bar.removeClass('o_bar_has_records transition-off');
//                window.getComputedStyle($bar[0]).getPropertyValue('width'); // Force reflow so that animations work
//                if (count > 0) {
//                    $bar.addClass('o_bar_has_records');
//                    // Make sure every bar that has records has some space
//                    // and that everything adds up to 100%
//                    var maxWidth = 100 - barMinWidth * barNumber;
//                    self.$('.progress-bar.o_bar_has_records').css('max-width', maxWidth + '%');
//                    $bar.css('width', (count * 100 / self.groupCount) + '%');
//                    barNumber++;
//                } else {
//                    $bar.css('width', '');
//                }
//            });
//            this.$('.progress-bar.o_bar_has_records').css('min-width', barMinWidth + '%');
//
//            // Display and animate the counter number
//            var start = this.prevTotalCounterValue;
//            var end = this.totalCounterValue;
//            var animationClass = start > 999 ? 'o_kanban_grow' : 'o_kanban_grow_huge';
//            if (start !== undefined && end > start && this.ANIMATE) {
//                $({currentValue: start}).animate({currentValue: end}, {
//                    duration: 1000,
//                    start: function () {
//                        self.$counter.addClass(animationClass);
//                    },
//                    step: function () {
//                        self.$number.html(_getCounterHTML(this.currentValue));
//                    },
//                    complete: function () {
//                        self.$number.html(_getCounterHTML(this.currentValue));
//                        self.$counter.removeClass(animationClass);
//                    },
//                });
//            } else {
//                this.$number.html(_getCounterHTML(end));
//            }
//
//            function _getCounterHTML(value) {
//                return juke_number(value);
////                    return utils.human_number(value, 0, 3);
//            }
//        },
//    });
//    return obj;
//});

//Opty Attachment filter
odoo.define('juke_crm.opty_attachment', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');

    var field_registry = require('web.field_registry');
    var basic_fields = require('web.basic_fields');
    var FieldBinaryFile = basic_fields.FieldBinaryFile;

    var FieldOptyAttachment = FieldBinaryFile.extend({
        template: 'FieldBinaryFileUploaderOptyAttachment',
        on_file_change: function (e) {
            var self = this;
            var file_node = e.target;
            if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
                if (this.useFileAPI) {
                    var file = file_node.files[0];
                    if (file.size > this.max_upload_size) {
                        var msg = _t("The selected file exceed the maximum file size of %s.");
                        this.do_warn(_t("File upload size limit exceeded"), _.str.sprintf(msg, utils.human_size(this.max_upload_size)));
                        return false;
                    }

                    var array_name = file.name.split('.');
                    var file_ext = array_name[array_name.length-1];
                    var clean_file_extention_allowed = file_extention_allowed;
                    clean_file_extention_allowed = (clean_file_extention_allowed.indexOf('.')>=0) ? clean_file_extention_allowed.replaceAll('.','')  : clean_file_extention_allowed;
                    clean_file_extention_allowed = (clean_file_extention_allowed.indexOf(' ')>=0) ? clean_file_extention_allowed.replaceAll(' ','')  : clean_file_extention_allowed;
                    var file_allowed = clean_file_extention_allowed.split(',');
                    if (!file_allowed.includes(file_ext)) {
                        var msg = _t("Only these types of file allowed: ") + file_extention_allowed;
                        this.do_warn(_t("File extention is invalid"), msg);
                        return false;
                    }

                    var filereader = new FileReader();
                    filereader.readAsDataURL(file);
                    filereader.onloadend = function (upload) {
                        var data = upload.target.result;
                        data = data.split(',')[1];
                        self.on_file_uploaded(file.size, file.name, file.type, data);
                    };
                } else {
                    this.$('form.o_form_binary_form input[name=session_id]').val(this.getSession().session_id);
                    this.$('form.o_form_binary_form').submit();
                }
                this.$('.o_form_binary_progress').show();
                this.$('button').hide();
            }
        }
    });

    field_registry.add('opty_attachment', FieldOptyAttachment);
});

//File size limit
odoo.define('juke_crm.juke_file_size_limit', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');

    var field_registry = require('web.field_registry');
    var basic_fields = require('web.basic_fields');
    var FieldBinaryFile = basic_fields.FieldBinaryFile;
    var FieldBinaryImage = basic_fields.FieldBinaryImage;

    var myFieldBinaryFile = FieldBinaryFile.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            this.fields = record.fields;
            this.useFileAPI = !!window.FileReader;

            this.max_upload_size = jekdoo_max_upload_size * 1024 * 1024; // 25Mo

            if (!this.useFileAPI) {
                var self = this;
                this.fileupload_id = _.uniqueId('o_fileupload');
                $(window).on(this.fileupload_id, function () {
                    var args = [].slice.call(arguments).slice(1);
                    self.on_file_uploaded.apply(self, args);
                });
            }
        },
        on_file_change: function (e) {
            var self = this;
            var file_node = e.target;
            if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
                if (this.useFileAPI) {
                    var file = file_node.files[0];
                    if (file.size > this.max_upload_size) {
                        var msg = _t("The selected file exceed the maximum file size of %s.");
                        this.do_warn(_t("File upload size limit exceeded"), _.str.sprintf(msg, utils.human_size(this.max_upload_size)));
                        return false;
                    }
                    var filereader = new FileReader();
                    filereader.readAsDataURL(file);
                    filereader.onloadend = function (upload) {
                        var data = upload.target.result;
                        data = data.split(',')[1];
                        self.on_file_uploaded(file.size, file.name, file.type, data);
                    };
                } else {
                    this.$('form.o_form_binary_form input[name=session_id]').val(this.getSession().session_id);
                    this.$('form.o_form_binary_form').submit();
                }
                this.$('.o_form_binary_progress').show();
                this.$('button').hide();
            }
        }
    });
    var myFieldBinaryImage = FieldBinaryImage.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            this.fields = record.fields;
            this.useFileAPI = !!window.FileReader;

            this.max_upload_size = jekdoo_max_upload_size * 1024 * 1024; // 25Mo

            if (!this.useFileAPI) {
                var self = this;
                this.fileupload_id = _.uniqueId('o_fileupload');
                $(window).on(this.fileupload_id, function () {
                    var args = [].slice.call(arguments).slice(1);
                    self.on_file_uploaded.apply(self, args);
                });
            }
        },
        on_file_change: function (e) {
            var self = this;
            var file_node = e.target;
            if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
                if (this.useFileAPI) {
                    var file = file_node.files[0];
                    if (file.size > this.max_upload_size) {
                        var msg = _t("The selected file exceed the maximum file size of %s.");
                        this.do_warn(_t("File upload size limit exceeded"), _.str.sprintf(msg, utils.human_size(this.max_upload_size)));
                        return false;
                    }
                    var filereader = new FileReader();
                    filereader.readAsDataURL(file);
                    filereader.onloadend = function (upload) {
                        var data = upload.target.result;
                        data = data.split(',')[1];
                        self.on_file_uploaded(file.size, file.name, file.type, data);
                    };
                } else {
                    this.$('form.o_form_binary_form input[name=session_id]').val(this.getSession().session_id);
                    this.$('form.o_form_binary_form').submit();
                }
                this.$('.o_form_binary_progress').show();
                this.$('button').hide();
            }
        }
    });
    return {
        FieldBinaryFile: myFieldBinaryFile,
        FieldBinaryImage: myFieldBinaryImage,
    }
});

//odoo.define('web_editor.summernote_override', function (require) {
//    'use strict';
//    var core = require('web.core');
//    var config = require('web.config');
//    var backend = require('web_editor.backend');
//    var FieldTextHtmlSimple = backend.FieldTextHtmlSimple;
//
//    var obj = FieldTextHtmlSimple.include({
//        /**
//         * @private
//         * @returns {Object} the summernote configuration
//         */
//        _getSummernoteConfig: function () {
//            var summernoteConfig = {
//                model: this.model,
//                id: this.res_id,
//                focus: false,
//                height: 180,
//                toolbar: [
//                    ['style', ['style']],
//                    ['font', ['bold', 'italic', 'underline', 'clear']],
//                    ['fontsize', ['fontsize']],
//                    ['color', ['color']],
//                    ['para', ['ul', 'ol', 'paragraph']],
//                    ['table', ['table']],
//                    // ['insert', this.nodeOptions['no-attachment'] ? ['link'] : ['link', 'picture']],
//                    ['history', ['undo', 'redo']]
//                ],
//                prettifyHtml: false,
//                styleWithSpan: false,
//                inlinemedia: ['p'],
//                lang: "odoo",
//                onChange: this._doDebouncedAction.bind(this),
//                disableDragAndDrop: !!this.nodeOptions['no-attachment'],
//            };
//
//            var fieldNameAttachment =_.chain(this.recordData)
//                .pairs()
//                .find(function (value) {
//                    return _.isObject(value[1]) && value[1].model === "ir.attachment";
//                })
//                .first()
//                .value();
//
//            if (fieldNameAttachment) {
//                this.fieldNameAttachment = fieldNameAttachment;
//                this.attachments = [];
//                summernoteConfig.onUpload = this._onUpload.bind(this);
//            }
//            summernoteConfig.getMediaDomain = this._getAttachmentsDomain.bind(this);
//
//
//            if (config.debug) {
//                summernoteConfig.toolbar.splice(7, 0, ['view', ['codeview']]);
//            }
//            return summernoteConfig;
//        }
//    });
//
//
//
//    return {
//        FieldTextHtmlSimple: obj,
//    };
//
//    // var editor = require('web_editor.summernote');
//    // require('summernote/summernote'); // wait that summernote is loaded
//    // var _t = core._t;
//    // var options = $.summernote.options;
//
//    // // disable some editor features
//    // // XXX: this is not working, unfortunately but `options.styleTags` below is. weird :S
//    // options.toolbar = [
//    //     ['font', ['bold', 'italic', 'underline', 'superscript', 'clear']],
//    //     ['para', ['ul', 'ol', 'paragraph']],
//    //     ['height', ['height']],
//    //     ['insert', []],
//    //     ['view', ['fullscreen', 'codeview']],
//    //     ['help', ['help']],
//    //     ['height', ['height']]
//    // ];
//
//    // // limit style tags
//    // options.styleTags = ['p', 'blockquote'];
//    // options.fontSizes = [_t('Default'), 8, 9, 10, 11, 12, 13, 14, 16, 18, 24, 36, 48, 62];
//    // return $.summernote;
//});

console.log("####### GET SETUP...");
//change kanban color & load custom setup
odoo.define('juke_crm.setup', function (require) {
    "use strict";
    var url = '/jekdoo/setup/json';
    var ajax = require('web.ajax');
    ajax.jsonRpc(url, 'call', {
//            model:  nama_model_sale_order,
//            method: 'get_data_master',
//            args: [],
//            kwargs: {}
    })
    .then(function(result) {
        result = JSON.parse(result);
        var status = result.status;
        console.log('status javascript odoo-custom.js: ', status)

        if(status) {
            var setup = result.setup;

            juke_app_title = setup.name || juke_app_title;
            jekdoo_max_upload_size = setup.jekdoo_max_upload_size || default_jekdoo_max_upload_size;

            is_admin = setup.is_admin
            if (setup.juke_file_extention_allowed) {
                file_extention_allowed = setup.juke_file_extention_allowed
            }

            var body = $("head") ;
            var new_html = '';
            new_html += '<!---- ##################### -->';
            new_html += '<!---- CUSTOM STYLE BY JACKY SUPIT - STARTED -->';
            new_html += '<!---- ##################### -->';
//            new_html += '<!---- ';
            new_html += '<style class="style-kanban">';

//            new_html += '.database_expiration_panel {';
//            new_html += '    display: none;';
//            new_html += '    display: none !important;';
//            new_html += '}';
            console.log('setup.is_user_biasa : ', setup.is_user_biasa)
            if(setup.is_user_biasa) {
//                new_html += ' .btn.btn-primary.o_list_button_add {display: none; display: none !important;} ';
//                new_html += ' .btn.btn-secondary.o_button_import {display: none; display: none !important;} ';
//                new_html += ' .o_form_button_edit {display: none; display: none !important;} ';
//                new_html += ' .o_form_button_create {display: none; display: none !important;} ';
////                new_html += ' .o_dropdown_toggler_btn.btn.btn-secondary.dropdown-toggle {display: none; display: none !important;} ';
////                new_html += ' .dropdown-menu.o_dropdown_menu.show {display: none; display: none !important;} ';

                //form buttons
                new_html += ' .o_form_statusbar .o_statusbar_buttons {display: none; display: none !important;} ';

                //operational buttons
                new_html += ' .o_cp_left .o_cp_buttons {display: none; display: none !important;} ';
                new_html += ' .o_cp_left .o_cp_sidebar {display: none; display: none !important;} ';
            }

            new_html += '</style>';
//            new_html += '-->';
            new_html += '<link rel="stylesheet" href="/jekdoo/static/src/css/backend-custom.css"/>';
            new_html += '<!---- ##################### -->';
            new_html += '<!---- CUSTOM STYLE BY JACKY SUPIT - ENDED -->';
            new_html += '<!---- ##################### -->';

//            body.find("style.style-kanban").remove();
            body.append(new_html);
        } else {
            console.log('Warning', result.msg);
        }
    });

})

//$ = jQuery;
//$(document).ready(function(e) {
//    $(document).on("keypress", "input.input-number, .o_field_monetary input, o_field_number input, input.o_field_float, input.o_field_number", function(e) {
//          var res = e.metaKey || // cmd/ctrl
//            e.which <= 0 || // arrow keys
//            e.which == 8 || // delete key
//            /[0-9]/.test(String.fromCharCode(e.which)); // numbers
//          return res;
//    })
//
//    $(document).on("paste", ".o_field_monetary input, o_field_number input, input.o_field_float, input.o_field_number", function(e) {
//        e.preventDefault();
//    })
//
//    $(document).on("keypress", "input.o_datepicker_input, .o_datepicker, .o_field_date", function(e) {
//          return false;
//    })
//
//    $(document).on("focusin", ".o_field_monetary input, o_field_number input, input.o_field_float, input.o_field_number", function(e) {
//        var val = $(this).val() || 0;
//        if(val) {
//            var val_str = val;
//            var lanjut = typeof formatMoney2 === 'function';
//            if (lanjut) {
//                val_str = formatMoney2(val.replaceAll(',',''), 2, ".", ",");
//                if(val_str == '0.00') {
//                    val_str = '';
//                    $(this).val('');
////                    console.log(' empty input. previous val: ', val);
//                }
//            }
//        }
//        $(this).select();
//    })
//
//    console.log("####### Activating $.number() ...");
//    $(document).on("focusout", ".o_field_monetary input, o_field_number input, input.o_field_float, input.o_field_number", function(e) {
//        var val = $(this).val();
//        var val_str = val;
//        if(val_str) {
//            if (typeof formatMoney2 === 'function') {
//                val_str = formatMoney2(val.replaceAll(',',''), 2, ".", ",");
//            } else {
//                if (typeof $.number === 'function') {
//                    val_str = $.number(val, 2);
//                } else {
//                    val_str = parseFloat(val);
//                    val_str = val_str.toFixed(2);
//                    val_str = addCommas(val_str);
//                }
//            }
//        } else {
//            val_str = "0.00";
//        }
//        $(this).val(val_str);
//    })
//
//    $(document).on("focusin", "input", function(e) {
//        $(this).select();
//    })
//
//    $("input").attr('autocomplete', 'off');
//
//    setTimeout(
//      function()
//      {
//        console.log("####### Removing empty first option...");
//        var select = $("select.o_required_modifier");
//        $.each(select, function(index, item) {
//            var first_option = $(this).find("option:first");
//            if (first_option.val() === 'false') {
//                first_option.remove();
//            }
//        });
//    }, 10 * 1000);
//})

//function d3_geom_voronoiHalfEdge(edge, lSite, rSite) {
//    var va = edge.a, vb = edge.b;
//
//    if (typeof vb.x === 'undefined') return;
//
//    this.edge = edge;
//    this.site = lSite;
//    this.angle = rSite ? Math.atan2(rSite.y - lSite.y, rSite.x - lSite.x) : edge.l === lSite ? Math.atan2(vb.x - va.x, va.y - vb.y) : Math.atan2(va.x - vb.x, vb.y - va.y);
//}
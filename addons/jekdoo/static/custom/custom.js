var $ = jQuery;
var SITE_URL = "";



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


$.fn.serializeJson = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

$.fn.getBase64 = function (withoutTag64, callback) {
    var that = null;
    if(this.files && this.files[0]) {
        //go
        that=this;
    } else {
        if(typeof (this[0]) !== 'undefined' ) {
            that = this[0];
        }
    }

    if (!$(that).val()) return false;

   var file = that.files[0];
   var str = '';
   var reader = new FileReader();
   reader.readAsDataURL(file);
   reader.onload = function () {
        str = reader.result;
        if(str) {
            if(withoutTag64) {
                var array_str = str.split(',');
                if (array_str.length > 1) {
                    str = array_str[1];
                    console.log('application/type: ' + array_str[0]);
                }
            }
        }
        if(typeof(callback) === 'function') {
            callback(str);
        }
   };
   reader.onerror = function (error) {
     //console.log('Error: ', error);
   };
}

var var_to_check = false;
var check_wait = function(){
    if(var_to_check){
        // run when condition is met
        //ok go
    }
    else {
        console.log('BELUM ADA');
        setTimeout(check_wait, 1000); // check again in a second
    }
}


function convertToRupiah(angka, withRpSymbol)
{
	var rupiah = '';
	var angkarev = angka.toString().split('').reverse().join('');
	for(var i = 0; i < angkarev.length; i++) {
	    if(i%3 == 0) {
	        rupiah += rupiah ? '.' : '';
	        rupiah += angkarev.substr(i,3);
	    }
	}

	var hasil = rupiah.toString().split('').reverse().join('');
	if (typeof(withRpSymbol) !== 'undefined' && withRpSymbol) hasil = 'Rp.' + hasil

	return hasil;
}

function getBase64(file, withoutTag64, callback) {
   var str = '';
   var reader = new FileReader();
   reader.readAsDataURL(file);
   reader.onload = function () {
     console.log(reader.result);
     str = reader.result;
     if(typeof(callback) === 'function') {
        callback(str);
     }
   };
   reader.onerror = function (error) {
     console.log('Error: ', error);
   };
   if(str) {
        if(withoutTag64) {
            var array_str = str.split(',');
            if (array_str.length > 1) {
                str = array_str[1];
                console.log('application/type: ' + array_str[0]);
            }
        }
   }
   return str;
}

function scrollTo(hash) {
    location.hash = "#" + hash;
}
function formatErrorMessage(jqXHR, exception) {

    if (jqXHR.status === 0) {
        return ('Not connected.\nPlease verify your network connection.');
    } else if (jqXHR.status == 404) {
        return ('The requested page not found. [404]');
    } else if (jqXHR.status == 500) {
        return ('Internal Server Error [500].');
    } else if (exception === 'parsererror') {
        return ('Requested JSON parse failed.');
    } else if (exception === 'timeout') {
        return ('Time out error.');
    } else if (exception === 'abort') {
        return ('Ajax request aborted.');
    } else {
        return ('Uncaught Error.\n' + jqXHR.responseText);
    }
}

function ajax_fail(xhr, err) {
    if (xhr.status === 401) {
        alert('Sorry, No Access');
    } else {
        var responseTitle = $(xhr.responseText).filter('title').get(0);
        alert($(responseTitle).text() + "\n" + formatErrorMessage(xhr, err));
    }
}
function ajax_get(url, data, sukses) {
    $.get(url, data)
        .done(function (result) {
            if(typeof(sukses) === 'function') {
                sukses(result);
            } else {
                //do nothing
            }
        })
        .fail(ajax_fail)
}
function ajax_post(url, data, sukses) {
    $.post(url, data)
        .done(function (result) {
            if(typeof(sukses) === 'function') {
                sukses(result);
            } else {
                //do nothing
            }
        })
        .fail(ajax_fail)
}
function ajax_post_json(url, data, sukses) {
    data = JSON.stringify(data);

    $.ajax({
        type: "POST",
        url: url,
        // data: JSON.stringify({ Markers: markers }),
        data: data,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(hasil){
            sukses(hasil)
        },
        failure: function(errMsg) {
            alert(errMsg);
        }
    });
}

function ajax_odoo(url, data, sukses) {
    ajax_post_json(url, data, function (hasil) {
        is_true = false;
        if (hasil.hasOwnProperty('result') )
            if (hasil.result.hasOwnProperty('status') )
                is_true = hasil.result.status

        if (is_true) {
            sukses(hasil);
        } else {
            var msg = '';
            if (hasil.hasOwnProperty('error') )
                if (hasil.error.hasOwnProperty('data') )
                    if (hasil.error.data.hasOwnProperty('message') )
                        msg = hasil.error.data.message;

            if(!msg)
                if (hasil.hasOwnProperty('result') )
                    if (hasil.result.hasOwnProperty('message') )
                        msg = hasil.result.message;

            if (!msg) msg = 'Failed!';

            alert(msg);
        }
    })
}
function ajax_odoo_get(url, data, sukses) {
    $.ajax({
        type: "GET",
        url: url,
        // data: JSON.stringify({ Markers: markers }),
        data: data,
        // contentType: "application/json; charset=utf-8",
        // dataType: "json",
        success: function (hasil) {
            sukses(hasil);
        },
        statusCode: {
            500: function(hasil) {
                if(typeof  hasil.responseText === 'undefined') {
                    alert(hasil);
                    return;
                }

                var msg = $(hasil.responseText).find("#exception_traceback").html();
                if(msg) {
                    var array_msg = msg.split("Warning:");
                    if (array_msg.length === 2) {
                        alert(array_msg[1]);
                    } else {
                        alert(msg);
                    }
                } else {
                    alert("Server returned error 500");
                }
            }
        }
    });
}


function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
}

function redirect_click(url) {
    window.location.href = url;
}
function redirect_http(url) {
    window.location.replace(url);
}


// Thanks to Yoshi for the hint!
// Polyfill for IE < 9
if (!Node) {
    var Node = {};
}
if (!Node.COMMENT_NODE) {
    // numeric value according to the DOM spec
    Node.COMMENT_NODE = 8;
}

function getComments(elem) {
  var children = elem.childNodes;
  var comments = [];

  for (var i=0, len=children.length; i<len; i++) {
    if (children[i].nodeType == Node.COMMENT_NODE) {
      comments.push(children[i]);
    }
  }
  return comments;
}

function month_1_to_01(m) {
    var hasil = m;
    if (hasil < 10) {
        hasil = '0' + hasil;
    }
    hasil = '' + hasil;
    return hasil;
}
function mmm_to_mm_str(mmm) {
    var hasil = mmm_to_mm(mmm);
    if (hasil < 10) {
        hasil = '0' + hasil;
    }
    hasil = '' + hasil;
    return hasil;
}
function mmm_to_mm(mmm) {
    var hasil = 0;
    switch(mmm) {
        case 'Jan':
            hasil= 1;
            break;
        case 'Feb':
            hasil= 2;
            break;
        case 'Mar':
            hasil= 3;
            break;
        case 'Apr':
            hasil= 4;
            break;
        case 'May':
            hasil= 5;
            break;
        case 'Mei':
            hasil= 5;
            break;
        case 'Jun':
            hasil= 6;
            break;
        case 'Jul':
            hasil= 7;
            break;
        case 'Aug':
            hasil= 8;
            break;
        case 'Agu':
            hasil= 8;
            break;
        case 'Sep':
            hasil= 9;
            break;
        case 'Okt':
            hasil=10;
            break;
        case 'Oct':
            hasil=10;
            break;
        case 'Nov':
            hasil=11;
            break;
        case 'Nop':
            hasil=11;
            break;
        case 'Dec':
            hasil=12;
            break;
        case 'Des':
            hasil=12;
            break;
    }
    return hasil;
}
function number_format(number, decimals, dec_point, thousands_sep) {
    // http://kevin.vanzonneveld.net
    // +   original by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +     bugfix by: Michael White (http://getsprink.com)
    // +     bugfix by: Benjamin Lupton
    // +     bugfix by: Allan Jensen (http://www.winternet.no)
    // +    revised by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // +     bugfix by: Howard Yeend
    // +    revised by: Luke Smith (http://lucassmith.name)
    // +     bugfix by: Diogo Resende
    // +     bugfix by: Rival
    // +      input by: Kheang Hok Chin (http://www.distantia.ca/)
    // +   improved by: davook
    // +   improved by: Brett Zamir (http://brett-zamir.me)
    // +      input by: Jay Klehr
    // +   improved by: Brett Zamir (http://brett-zamir.me)
    // +      input by: Amir Habibi (http://www.residence-mixte.com/)
    // +     bugfix by: Brett Zamir (http://brett-zamir.me)
    // +   improved by: Theriault
    // +   improved by: Drew Noakes
    // *     example 1: number_format(1234.56);
    // *     returns 1: '1,235'
    // *     example 2: number_format(1234.56, 2, ',', ' ');
    // *     returns 2: '1 234,56'
    // *     example 3: number_format(1234.5678, 2, '.', '');
    // *     returns 3: '1234.57'
    // *     example 4: number_format(67, 2, ',', '.');
    // *     returns 4: '67,00'
    // *     example 5: number_format(1000);
    // *     returns 5: '1,000'
    // *     example 6: number_format(67.311, 2);
    // *     returns 6: '67.31'
    // *     example 7: number_format(1000.55, 1);
    // *     returns 7: '1,000.6'
    // *     example 8: number_format(67000, 5, ',', '.');
    // *     returns 8: '67.000,00000'
    // *     example 9: number_format(0.9, 0);
    // *     returns 9: '1'
    // *    example 10: number_format('1.20', 2);
    // *    returns 10: '1.20'
    // *    example 11: number_format('1.20', 4);
    // *    returns 11: '1.2000'
    // *    example 12: number_format('1.2000', 3);
    // *    returns 12: '1.200'
    var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        toFixedFix = function (n, prec) {
            // Fix for IE parseFloat(0.55).toFixed(0) = 0;
            var k = Math.pow(10, prec);
            return Math.round(n * k) / k;
        },
        s = (prec ? toFixedFix(n, prec) : Math.round(n)).toString().split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}

$(document).ready(function(){
    $(document).on("click", ".btn-submit-click", function(e) {
        e.preventDefault();
        var that = this,
            me = $(that),
            form = me.closest("form"),
            form_id = form.attr('id')
            ;
        form.submit();
    });

    $(document).ajaxStart(function() {
      let span_spin = $(".span-spin");
      span_spin.css('display', 'inline-block');
      let parents = span_spin.parent();
      $.each(parents, function(index, item){
          let parent = $(this);
          let is_button = false;
          let element_type = parent.prop('nodeName').toLowerCase();
          if(parent.hasClass('btn')) is_button = true;
          if(element_type === 'a') is_button=true;
          if(element_type === 'button') is_button=true;
          if (is_button) {
                parent.css('cursor', 'wait');
                parent.prop('disabled', true);
          }
      });
    });

    $(document).ajaxStop(function() {
      let span_spin = $(".span-spin");
      span_spin.css('display', 'none');
      let parents = span_spin.parent();
      $.each(parents, function(index, item){
        var parent = $(this);
        var is_button = false;
        var element_type = parent.prop('nodeName').toLowerCase();
        if(parent.hasClass('btn')) is_button = true;
        if(element_type === 'a') is_button=true;
        if(element_type === 'button') is_button=true;
        if (is_button) {
            parent.css('cursor', 'pointer');
            parent.prop('disabled', false);
        }
      });
    });
});




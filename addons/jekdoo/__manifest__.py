# -*- coding: utf-8 -*-
{
    'name': "Jekdoo Functions",
    'summary': """my custom free snippets""",
    'description': """
        Make your life easier
    """,

    'author': "Jacky supit",
    'website': "http://www.jeksu.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'functions',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'web',
                'mail',
                'website',
                # 'web_widget_color',
                ],

    # always loaded
    'data': [
        'data/ids.xml',
        'security/ir.model.access.csv',
        'views/jekdoo_template.xml',
        'views/setup.xml',
        # 'views/custom_view.xml',
        'views/menu.xml'
    ],
    'qweb': [
        #matikan, user jadi nggak terkontrol
        # 'static/src/xml/dynamic_listview_button_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
}
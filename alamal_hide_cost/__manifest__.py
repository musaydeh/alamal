# -*- coding: utf-8 -*-
{
    'name': "Alamal Hide Product Cost Price",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Smartr Teknoloji",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'purchase', 'sale_margin'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/views.xml',
    ],

}

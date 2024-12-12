{
    'name': 'Smartr Alamal Salse Custom',
    'version': '1.0',
    'summary': 'Smartr Alamal Salse Custom',
    'description': 'Smartr Alamal Salse Custom',
    'author': 'Smartr Teknoloji',
    'depends': ['sale', 'delivery', 'purchase_stock', 'alamal_tires'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/inherit_view_partner_form.xml',
        'security/security.xml',
        'report/report_so_all_deliveries.xml',
        'views/account_journal_views.xml',
        'views/inherit_sale_order.xml',
        'views/procurement_group_views.xml',
        'views/inherit_purchase_order.xml',
        'views/inherit_product_product.xml',
        'views/inherit_res_partner.xml',
        'views/res_company_views.xml',
        'views/res_user_views.xml',
        'views/product_pricelist_views.xml',
        'views/product_pricelist_item_views.xml',
        'views/stock_move_line_views.xml',
        'views/purchase_order_type_views.xml',
        'views/stock_picking_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'smartr_alamal_sale_enhancements/static/src/**/*.js',
            'smartr_alamal_sale_enhancements/static/src/**/*.xml',
        ]
    },
    'installable': True,
    'auto_install': False,
}

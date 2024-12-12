{
    'name': 'Fast SO/PO From Stock',
    'version': '1.0',
    'summary': 'Fast SO/PO From Stock',
    'description': 'Fast SO/PO From Stock',
    'author': 'Smartr Teknoloji',
    'depends': ['stock', 'sale', 'sale_stock', 'purchase', 'alamal_tires', 'alamal_hide_cost'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/internal_warehouse_transfer_views.xml',
        'views/view.xml',
        'views/wizard_views.xml',
        'views/inherit_stock_route_form.xml',
        'views/inherit_stock_location_form.xml',
        'views/inherit_sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
}

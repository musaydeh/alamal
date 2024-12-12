{
    'name': 'Smartr Tires Custom Purchase Reports',
    'version': '1.0',
    'summary': 'Smartr Tires Custom Purchase Reports',
    'description': 'Smartr Tires Custom Purchase Reports',
    'author': 'Smartr Teknoloji',
    # 'website': '',
    'depends': ['fast_so_po_from_stock_adj', 'smartr_alamal_sale_enhancements', 'sale_purchase_inter_company_rules'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/inherit_purchase_order_form_view.xml',
        'views/inherit_sale_order_form_view.xml',
        'views/inherit_product_template_form_view.xml',
        'views/mrp_tag_views.xml',
        'views/product_category_views.xml',
        'views/purchase_requisition_views.xml',
        'views/res_partner_views.xml',
        'views/stock_lot_views.xml',
        'views/stock_quant_views.xml',
        'views/stock_picking_views.xml',
        'views/wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
{
    'name': 'Warehouse Access Control',
    'version': '18.0.1.0.0',
    'summary': 'Control user access to warehouses across companies',
    'description': '''
        This module allows configuring user access to specific warehouses across different companies.
        Features:
        - Grant users access to read quantities in specific warehouses from other companies
        - Configure warehouse access per user
        - Respect company security rules while allowing controlled cross-company access
        - Archive/unarchive warehouse access rules
        - Search and filter warehouse access by various criteria
    ''',
    'category': 'Inventory/Inventory',
    'author': 'Smartr Teknoloji',
    'website': '',
    'depends': ['stock', 'smartr_alamal_sale_enhancements'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/warehouse_access_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}

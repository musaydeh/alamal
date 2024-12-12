{
    'name': 'Cross Company Inventory Access',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Manage cross-company warehouse access rights',
    'description': """
        This module allows specific users from one company to access 
        inventory quantities of specific warehouses in another company.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/warehouse_access_rules.xml',
        'views/warehouse_access_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
# -*- coding: utf-8 -*-
{
    'name': "SMG Create user",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr','helpdesk'],

    # always loaded
    'data': [
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/drive_and_odoo.xml',
        'views/views.xml',
        'views/helpdesk.xml',
        'views/templates.xml',
        'data/floor_simple_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
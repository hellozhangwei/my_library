# -*- coding: utf-8 -*-
{
    'name': "my_library",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Library', #odoo会为此处分类名创建一个小写的base.module_category_<声明文件中分类名称>XML ID，并将空格替换为下划线。这可以用于通过应用分类来关联安全组。本例中，我们使用了Library分类名，它生成了一个base.module_category_library的XML标识符。
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/groups.xml',
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_book.xml',
        'views/library_book_rent.xml',
        'views/library_book_statistics.xml',
        'views/templates.xml',
        'views/my_contacts.xml',
        'wizard/library_book_rent_wizard.xml',
        'wizard/library_book_return_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'post_init_hook': 'add_book_hook', #只有在安装的时候才被执行

}

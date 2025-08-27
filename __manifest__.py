# -*- coding: utf-8 -*-
{
    'name': "School Master",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Irshad K T",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'School',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/receipt_sequence.xml',
        'views/views.xml',
        'views/student_master.xml',
        'views/error.action.message.xml',
        'views/teacher_master.xml',
        'views/settings.xml',
        'views/student_fee.xml',
        'views/student_fee_receipt.xml',
        'views/student_courses.xml',
        'views/fee_update_wizard.xml',
    ],

    'assets': {
        'web.assets_backend': [

            #'school_master/static/src/js/student_warining_okbutton.js',

            #'school_master/static/src/js/auto_logout.js',
            'school_master/static/src/css/student_master.css'

        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

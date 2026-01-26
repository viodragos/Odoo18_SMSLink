{
    'name': 'SMSLink Romania Integration',
    'version': '18.0.1.0.0',
    'summary': 'Integrare SMSLink.ro pentru trimitere SMS-uri',
    'description': """
        Modul pentru integrarea cu SMSLink.ro pentru trimiterea automată de SMS-uri
        și automatizări pe baza acțiunilor în Odoo.
    """,
    'category': 'SMS',
    'author': 'Viorel Dragos',
    'website': 'https://www.smslink.ro',
    'depends': ['base', 'mail', 'repair'],  # Dacă folosești modulul repair
    'data': [
        'security/ir.model.access.csv',
        #'views/sms_template_views.xml',    # NOU - template-uri
        'views/sms_config_views.xml',
        'views/sms_history_views.xml',
        'views/repair_simple_views.xml',     # NOU - repair integration
        'smslink_wizard/contact_sms_wizard_view.xml',
        'views/sms_compose_contact_view.xml',
        'views/menu.xml',
        'views/report_picking_templates.xml',
        # 'data/ir_cron.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}


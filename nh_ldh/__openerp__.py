# -*- encoding: utf-8 -*-
{
    'name': 'NH Clinical LDH Configuration',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs_mobile','nh_etake_list', 'nh_etake_list_theme'],
    'data': ['ldh_master_data.xml'],
    'demo': ['eobs_locations.xml',
             'etake_list_locations.xml',
             'ldh_user_data.xml'],
    'qweb': ['static/src/xml/nh_ldh.xml'],
    'application': True,
    'installable': True,
    'active': False,
}
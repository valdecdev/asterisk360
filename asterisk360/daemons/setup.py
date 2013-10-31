#!/usr/bin/env python
'''
Asterisk360 distutils script.
'''
__author__ = 'Les Green'
__id__ = '$Id$'

from distutils.core import setup

setup(
    name =          'asterisk360',
    version =       '1.0',
    description =   'Asterisk Manager Screen Pop and Call Handler for OpenERP.',
    author =        'Les Green',
    author_email =  'l.green@valuedecision.com',
    license =       'AGPL3',
    url =           'http://www.valuedecision.com/asterisk360',
    packages =      ['callmanager'],
    scripts =       ['call_manager', 'openerp_wamp_server','scripts/get_cid_name.py' ],
    data_files =    [('/etc/asterisk', ['config/etc/asterisk/py-asterisk.conf.default']),
                     ('/usr/local/bin',['scripts/get_cid_name_timeout.sh.example'])]
)

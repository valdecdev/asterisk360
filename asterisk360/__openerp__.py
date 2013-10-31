# -*- coding: utf-8 -*-
##############################################################################
#
#    Asterisk 360 module for OpenERP
#    Copyright (C) 2012 Les Green <l.green@valuedecision.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Asterisk 360',
    'category': 'Telephony Integration',
    'description': """
This module adds the ability to recognise and pop-up the history of customers and log incoming calls via Asterisk.
==================================================================================================================

Detailed documentation can be found at http://www.valuedecision.com/asterisk360

The module is based on and a significant extension of the asterisk_click2dial module of Akkretion.
This module has been developed in co-operation with Cmass Ltd. http://www.cmass-ni.com

The module has the following abilities:

    - Initiates outgoing calls from scheduled phone calls
    - Creates phone logs for outgoing and incoming calls
    - Auto pop-up of partner history if phone number is recognised for incoming calls
    - Population of phone log with partner and contact as well as call duration

... and much more.

Requirements and Installation
-----------------------------
This module is complex; proficient knowledge of Asterisk and OpenERP is necessary.
Detailed instructions can be found at http://www.valuedecision.com/asterisk360

    """,
    'version': '2.1',
    'depends': ['web','asterisk_click2dial','crm'],
    'js': ['static/src/js/asterisk360.js',
           'static/src/js/autobahn.js'],
    'css': ['static/src/css/asterisk360.css'],
    'qweb': ['static/src/xml/asterisk360.xml'],
    'data': ['asterisk360_view.xml',
             'wizard/asterisk360_inbound_call_partner_view.xml',
             'wizard/asterisk360_configuration_view.xml'],
    'test': ['test/asterisk360_partnertest.yml'],
    'auto_install': False,
    'web_preload': False,
    'application': True,
    'installable': True
}
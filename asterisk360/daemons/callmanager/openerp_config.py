# -*- encoding: utf-8 -*-
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

from Asterisk.Config import Config, ConfigParser, ConfigurationError

class OpenERPConfig(Config):
 
    def get_openerp_connection(self, openerp=None):
        conf = self.conf
        try:
            if openerp is None:
                openerp = conf.get('py-asterisk', 'default openerp')

            items = dict(conf.items('openerp: ' + openerp))

        except ConfigParser.Error, e:
            raise ConfigurationError(str(e))
    
        items['uri']='http://%s:%s/xmlrpc/object' % (items['server'], items['port'])
    
        return items  

    def get_ws_connection(self, ws=None):
        conf = self.conf
        try:
            if ws is None:
                ws = conf.get('py-asterisk', 'default websockets')

            items = dict(conf.items('websockets: ' + ws))

        except ConfigParser.Error, e:
            raise ConfigurationError(str(e))
    
        items['uri']='ws://%s:%s' % ( items['ws-server'], items['ws-port'])
        return items

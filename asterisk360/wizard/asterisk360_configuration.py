__author__ = 'les'

from openerp.osv import fields
from openerp.osv.orm import TransientModel
from mako.template import Template

class asterisk360_configuration_output(TransientModel):
    _name="asterisk360.configuration.wizard.output"
    _columns= {
        'output': fields.text('Output', readonly=True)
    }

    def configuration_done(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}


class asterisk360_configuration_wizard(TransientModel):
    _name="asterisk360.configuration.wizard"
    _description="Asterisk360 Configuration Helper"

    _columns= {
        'user_id': fields.many2one('res.users', 'User for Asterisk',required=True),
        'user_password': fields.char('Password for User', size=100, required=True),
        'openerp_ip_address': fields.char('OpenERP Server', size=50,
                    help='OpenERP Server IP / DNS location', required=True),
        'openerp_port': fields.integer('Port', required=True),
        'asterisk_server_id': fields.many2one('asterisk.server', 'Asterisk Server',
                    help='Asterisk Server Configuration to use', required=True),
        'asterisk_server_address': fields.related('asterisk_server_id','ip_address'),
        'asterisk_port': fields.related('asterisk_server_id','port', string="Asterisk Port", type="integer", readonly=True),
        'websocket_server_address': fields.related('asterisk_server_id','ws_address', string="Web Socket Server", type="char", readonly=True),
        'agi_path': fields.char('Path to AGI Script', size=100, required=True,
                    help='Path to the AGI script which asterisk AGI calls'),
        'agi_timeout': fields.integer('Timeout',required=True,
                    help='Timeout after which control is returned to asterisk (in the case of OpenERP connection failure)'),
        'ws_logfile': fields.char('Logfile', size=100),
        'ws_debug': fields.boolean('Debug'),
    }

    _defaults= {
        'openerp_ip_address': '127.0.0.1',
        'openerp_port': 8069,
        'agi_path': '/usr/local/bin/get_cid_name.py',
        'agi_timeout': 2,
        'ws_debug': False
    }

    def onchange_asterisk_server_id(self, cr, uid, ids, server_id, context=None):
        if not server_id:
            return {'value':{}}
        server= self.pool.get('asterisk.server').browse(cr, uid, server_id, context)
        return {'value':{'websocket_server_address': server.ws_address,
                         'asterisk_port': server.port }}


    def generate_pyasterisk(self, cr, uid, ids, context=None):

        config = self.read(cr, uid, ids,[])[0]
        wsserver = config['websocket_server_address'].split(':')
        config['websocket_server_port']= wsserver[-1]
        config['websocket_server_address']= wsserver[-2].replace('/','')
        config['asterisk_server_id'] = config['asterisk_server_id'][0]

        return self._output_window(cr, uid, 'py-asterisk.conf.mako', config, context)

    def generate_agi_script(self, cr, uid, ids, context=None):
        config = self.read(cr, uid, ids,[])[0]
        return self._output_window(cr, uid, 'get_cid_name_timeout.sh.mako', config, context)

    def configuration_done(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def _output_window(self, cr, uid, templatename, config, context):

        if not context:
            context={}

        views = self.pool.get('ir.ui.view')
        view_id = views.search(cr, uid, [('name','=','view_asterisk360_configuration_wizard_output')])

        config['openerp_db'] = cr.dbname
        config['user_id'] = config['user_id'][0]

        import os
        templatefile = '%s/%s' % (os.path.dirname(os.path.abspath(__file__)), templatename)
        template = Template(filename=templatefile)

        context['default_output']= template.render(cfg=config)
        context['title']= 'Asterisk360 - Copy Requested Configuration to File'

        return {'type':'ir.actions.act_window',
                'view_id': view_id,
                'res_model': 'asterisk360.configuration.wizard.output',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'nodestroy': True,
                'context': context}
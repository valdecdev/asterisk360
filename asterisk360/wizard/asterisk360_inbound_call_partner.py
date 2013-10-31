__author__ = 'les'

from openerp import pooler
from openerp.osv import fields,osv
import logging

_logger = logging.getLogger(__name__)

class asterisk360_inbound_call_partner(osv.TransientModel):
    _name = "asterisk360.inbound.call.partner"
    _description = "Inbound Call PopUp"

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Calling', required=True),
        'call_id': fields.many2one('crm.phonecall','Call Details',  type='many2one'),
        'call_summary': fields.related('call_id','name', type='char', relation='crm.phonecall'),
        'call_description': fields.related('call_id','description', type='char', relation='crm.phonecall')
    }

    def save_call(self, cr, uid, ids, context=None):
        print "poo"


    def read(self, cr, uid, ids, fields=None, context=None):
        if len(ids)>1: raise LookupError("Can only read One inbound Call here")
        ret = []
        _logger.warn(context)
        result =  self.pool['res.partner'].read(cr, uid, ids, [], context)
        if 'openerp_call_id' in context:
            call = self.pool['crm.phonecall'].read(cr, uid, context['openerp_call_id'], ['name','description'], context)

        for partner in result:
            partner['partner_id'] = partner['id']
            partner['call_id'] = call['id']
            partner['call_summary'] = call['name']
            partner['call_description'] = call['description']
            ret.append(partner)
        _logger.warn(fields)
        _logger.warn(ret)
        return ret

    def write(self, cr, uid, ids, vals, context=None):
        _logger.warn("Need to update the write field here")
        #return self.pool.get('crm.phonecall').write(cr, uid, ids, fields, context)

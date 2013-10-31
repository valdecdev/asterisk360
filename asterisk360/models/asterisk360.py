__author__ = 'les'

from openerp.osv import orm, fields
from openerp.tools.translate import _

class asterisk_server(orm.Model):
    _inherit = "asterisk.server"

    _columns = {
        'ws_address': fields.char('Asterisk WebSocket Server Full Address or DNS', size=150, help="Full URI of the WebSockets Server including port  e.g ws://<ip>:<port>")
    }

class res_users(orm.Model):
    _inherit = "res.users"

    _columns = {
        'asterisk_chan_type': fields.selection([
                                                   ('SIP', 'SIP'),
                                                   ('IAX2', 'IAX2'),
                                                   ('DAHDI', 'DAHDI'),
                                                   ('Zap', 'Zap'),
                                                   ('Skinny', 'Skinny'),
                                                   ('MGCP', 'MGCP'),
                                                   ('mISDN', 'mISDN'),
                                                   ('H323', 'H323'),
                                                   ('USTM', 'USTM'),
                                                   ('SCCP', 'SCCP'),
                                                   ('Local','Local')], 'Asterisk channel type', help="Asterisk channel type, as used in the Asterisk dialplan. If the user has a regular IP phone, the channel type is 'SIP'."),
        'screen_pop': fields.boolean('Screen Pop', help="Check to enable screen pops for this user"),
        #'screen_pop_form': fields.one2many('ir.actions')
        'log_calls': fields.boolean('Log Calls', help="Log calls for this user")
    }

class res_partner(orm.Model):
    _inherit = "res.partner"

    _columns = {
        'call_ids': fields.one2many('crm.phonecall', 'partner_id', 'Calls'),
    }

    def _get_caller_name(self, details):
        person = details['contact_name'] if 'contact_name' in details else False
        partner = details['partner_name'] if 'partner_name' in details else False


        if person:
            if partner and len(partner)>0:
                return '%s (%s)' % (person, partner)
            return person

        if partner: return partner

        return 'Unknown'

    def setup_call_inbound(self, cr, uid, number, extension, context=None):
        details = {
            'extension': extension,
        }
        res = self.get_partner_from_phone_number(cr, uid, number, context=context)
        if res:
            details['contact_id'] = res[0]
            details['contact_name'] = res[2]
            details['parent_id'] = res[1]
            details['parent_name'] = '%s' % self.read(cr, uid, res[1],['name'])['name'] if res[1] else ""

        # if we want to record the calls
        details['openerp_call_id'] = self.create_inbound_call(cr, uid, details, number, context)
        return details

    def create_inbound_call(self, cr, uid, details, inbound_number, context):
        inbound_category_id = self.pool.get('crm.case.categ').search(cr, uid, [('name', '=', 'Inbound')])
        return self.create_call(cr, uid, details, inbound_number, inbound_category_id, context)

    def create_call(self, cr, uid, details, number, category_id, context={}):
        vals = {
            'name': '%s %s' % (self._get_caller_name(details),_('Inbound')),
            'partner_phone': number,
            'categ_id': category_id[0],
            }
        if 'extension' in details:
            user_obj = self.pool.get('res.users')
            search_results = user_obj.search(cr, uid, [('internal_number','=',details['extension'])])
            if len(search_results)>0:
                vals['user_id'] = search_results[0]


                ret = user_obj.read(cr, uid, vals['user_id'],['context_section_id','log_calls'])
                if not ret['log_calls']: return

                if 'context_section_id' in ret:
                    section_id = ret['context_section_id']
                    vals['section_id'] = section_id[0]

        if 'contact_id' in details: vals['partner_id'] = details['contact_id']

        call_object = self.pool.get('crm.phonecall')

        if not context:
            context={}
        context['mail_create_nosubscribe'] = True

        call_id = call_object.create(cr, uid, vals, context)
        if 'user_id' in vals:
            call_object.message_subscribe_users(cr, uid, [call_id], [vals['user_id']])
        call_object.case_open(cr, uid, [call_id])
        return call_id

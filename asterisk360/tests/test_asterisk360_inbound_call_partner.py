from openerp.tests import common
from datetime import datetime

class TestAsterisk360InboundCallPartner(common.SingleTransactionCase):

    def setUp(self):
        """***setup configuration tests***"""
        super(TestAsterisk360InboundCallPartner, self).setUp()
        cr, uid, = self.cr, self.uid

        self.asterisk360_inboundcallpartner = self.registry('asterisk360.inbound.call.partner')
        self.asterisk_server = self.registry('asterisk.server')
        self.users = self.registry('res.users')
        self.partners = self.registry('res.partner')

        self.partner_id = self.partners.create(cr, uid, {
            'name': 'logged_in_partner_for_user'
        })

        self.user_id = self.users.create(cr, uid,{
            'name': 'my_callpartner_user',
            'login': 'my_callpartner_user',
            'password': 'my_callpartner_password',
            'partner_id': self.partner_id
        }, context=None)



    def tearDown(self):
        cr, uid = self.cr, self.uid
        self.users.unlink(cr, uid, [self.user_id])
        self.partners.unlink(cr, uid, [self.partner_id])
        super(TestAsterisk360InboundCallPartner, self).tearDown()

    def test_inboundcallpartner_gets_partner_details_from_context(self):
        cr, uid = self.cr, self.uid
        icp = self.asterisk360_inboundcallpartner.read(cr, uid, [self.partner_id],
                                                          [], context=None)
        self.assertTrue(icp['partner_id'] == self.partner_id)


from openerp.tests import common
from datetime import datetime

class TestAsterisk360Configuration(common.SingleTransactionCase):

    def setUp(self):
        """***setup configuration tests***"""
        super(TestAsterisk360Configuration, self).setUp()
        cr, uid, = self.cr, self.uid

        self.asterisk360_configuration = self.registry('asterisk360.configuration.wizard')
        self.asterisk_server = self.registry('asterisk.server')
        self.users = self.registry('res.users')

        self.user_id = self.users.create(cr, uid,{
            'name': 'my_demo_user',
            'login': 'my_demo_user',
            'password': 'my_demo_password'
        }, context=None)

        self.asterisk_server_id = self.asterisk_server.create(cr, uid, {
            'name': 'Local Asterisk Server',
            'ip_address': '127.0.0.1',
            'port': 5038,
            'context': 'localcontext',
            'password': 'secret',
            'login': 'asterisk_login',
            'ws_address': 'ws://192.168.222.222:9000'
        }, context=None)

        self.config = self.asterisk360_configuration.create(cr, uid, {
            'user_id': self.user_id,
            'user_password': 'testpassword',
            'asterisk_server_id': self.asterisk_server_id,

        }, context=None)

    def tearDown(self):
        cr, uid = self.cr, self.uid
        self.users.unlink(cr, uid, [self.user_id])
        self.asterisk_server.unlink(cr, uid, [self.asterisk_server_id])
        self.asterisk360_configuration.unlink(cr, uid, [self.config])

        super(TestAsterisk360Configuration, self).tearDown()

    def test_pyasterisk_configuration(self):
        cr, uid = self.cr, self.uid
        pyasterisk =  self.asterisk360_configuration.generate_pyasterisk(cr, uid, [self.config], None)

        output = pyasterisk['context']['default_output']

        self.assertTrue('[py-asterisk]' in output)
        self.assertTrue('ir.actions.act_window' in pyasterisk['type'])

    def test_agi_script_configuration(self):
        cr, uid = self.cr, self.uid
        agi = self.asterisk360_configuration.generate_agi_script(cr, uid, [self.config], None)

        self.assertTrue('default_output' in agi['context'])
        self.assertTrue('timeout 2s' in agi['context']['default_output'])

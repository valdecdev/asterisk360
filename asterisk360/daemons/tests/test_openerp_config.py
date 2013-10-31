import unittest
from callmanager.openerp_config import OpenERPConfig

class TestOpenERPConfig(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_openerp_connection(self):
        config = OpenERPConfig().get_openerp_connection()
        print config
        self.assertTrue(config.has_key('uid'))
        self.assertEqual(7, len(config.keys()),'Wrong number of keys - %s' % len(config.keys()))

    def test_get_ws_connection(self):
        config = OpenERPConfig().get_ws_connection()
        print config
        self.assertTrue(config.has_key('uri'))
        self.assertEqual(5, len(config.keys()),'Wrong number of keys - %s' % len(config.keys()))


from autobahn.wamp import WampClientProtocol, WampClientFactory, WampServerFactory
from autobahn.websocket import connectWS

from callmanager.openerp_wamp_server_protocol import OpenERPWampServerProtocol
from threading import Thread

from twisted.internet import reactor


import unittest
import sys

class OpenERPWampClientProtocol(WampClientProtocol):

    def sendCall(self):
        self.publish("callsto:"+self.extension,self.call_details)
        print "Sent Call"

    def onSessionOpen(self):
        self.prefix("callsto", "asterisk360/callsto#")
        self.subscribe("callsto:"+self.extension, self.sendCall())
        self.sendCall()
        print "Sent Call"


class TestWampClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print "Starting Server"
        ws_server = WampServerFactory("ws://127.0.0.1:9091", debug=True)
        ws_server.protocol = OpenERPWampServerProtocol
        reactor.listenTCP(9091, ws_server)
        cls._ws_server = ws_server
        Thread(target=reactor.run, args=(False,)).start()
        print "Started Server"

    @classmethod
    def tearDownClass(cls):
        print "Tear Down"
        reactor.callLater(2, reactor.stop)


    def test_send_message(self):
        factory = WampClientFactory("ws://127.0.0.1:9091")
        factory.protocol = OpenERPWampClientProtocol
        factory.protocol.call_details = {'hello':'world'}
        factory.protocol.extension = "11"
        connectWS(factory)
        self.assertEquals("blan","blah")
        print "Blah"

        #reactor.run()
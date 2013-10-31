from twisted.python import log
from autobahn.wamp import WampServerProtocol

class OpenERPWampServerProtocol(WampServerProtocol):

    def onConnect(self, connectionRequest):
        core = "asterisk360/callsto#"
        self.registerForPubSub(core, True)
        log.msg("Web Socket Server Connected:%s" % core)
        return 'wamp'

#! /usr/bin/python
# -*- encoding: utf-8 -*-
"""
 CallerID name lookup in OpenERP for Asterisk IPBX

 When executed from the dialplan on an incoming phone call, it will lookup in
 OpenERP's partner addresses, and, if it finds the phone number, it will get the
 corresponding name of the person and use this name as CallerID name for the incoming call.

 Requires the "asterisk_click2dial" module
 available from https://code.launchpad.net/openerp-asterisk-connector
 for OpenERP version >= 5.0

 This script is designed to be used as an AGI on an Asterisk IPBX...
 BUT I advise you to use a wrapper around this script to control the
 execution time. Why ? Because if the script takes too much time to
 execute or get stucks (in the XML-RPC request for example), then the
 incoming phone call will also get stucks and you will miss a call !
 The simplest solution I found is to use the "timeout" shell command to
 call this script, for example :

 # timeout 1s get_cid_name.py <OPTIONS>

 See my sample wrapper "get_cid_name_timeout.sh"

 Asterisk dialplan example :

 [from-extern]
 exten => _0141981242,1,AGI(/usr/local/bin/get_cid_name_timeout.sh)
 exten => _0141981242,n,Dial(SIP/10, 30)
 exten => _0141981242,n,Answer()
 exten => _0141981242,n,Voicemail(10@default,u)
 exten => _0141981242,n,Hangup()

 It's probably a good idea to create a user in OpenERP dedicated to this task.
 This user only needs to be part of the group "Asterisk CallerID", which has
 read access on the 'res.partner' object, nothing more.
 
 
 April 2012
 ==========
 The original author of this script is Alexis de Lattre <alexis.delattre@akretion.com>
 Additions have been made to enable communication with a WAMP Web Socket Server and
 some changes to how the OpenERP server is called and what methods are called. 
 
"""

__author__ = "Les Green <l.green@valuedecision.com"
__date__ = "June 2013"
__version__ = "2.0"

#  Copyright (C) 2010 Alexis de Lattre <alexis.delattre@akretion.com>
#            (C) 2012 Les Green <l.green@valuedecision.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xmlrpclib
import sys
from optparse import OptionParser
from twisted.internet import reactor
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol

class OpenERPWampClientProtocol(WampClientProtocol):

    def sendCall(self):
        self.publish("callsto:"+self.extension,self.call_details)
        reactor.callLater(2,reactor.stop)
        
    def onSessionOpen(self):
        self.prefix("callsto", "asterisk360/callsto#")
        self.sendCall()

# CID Name that will be displayed if there is no match in res.partner.address
default_cid_name = "Not in OpenERP"

# Define command line options
option_server = {'names': ('-s', '--server'), 'dest': 'server', 'type': 'string', 'help': 'DNS or IP address of the OpenERP server. Default = localhost', 'action': 'store', 'default':'localhost'}
option_port = {'names': ('-p', '--port'), 'dest': 'port', 'type': 'int', 'help': "Port of OpenERP's XML-RPC interface. Default = 8069", 'action': 'store', 'default': 8069}
option_ssl = {'names': ('-e', '--ssl'), 'dest': 'ssl', 'help': "Use XML-RPC secure i.e. with SSL instead of clear XML-RPC. Default = no, use clear XML-RPC.", 'action': 'store_true', 'default': False}
option_database = {'names': ('-d', '--database'), 'dest': 'database', 'type': 'string', 'help': "OpenERP database name. Default = openerp", 'action': 'store', 'default': 'openerp'}
option_user = {'names': ('-u', '--user-id'), 'dest': 'user', 'type': 'int', 'help': "OpenERP user ID to use when connecting to OpenERP. Default = 2", 'action': 'store', 'default': 2}
option_password = {'names': ('-w', '--password'), 'dest': 'password', 'type': 'string', 'help': "Password of the OpenERP user. Default = demo", 'action': 'store', 'default': 'demo'}
option_ascii = {'names': ('-a', '--ascii'), 'dest': 'ascii', 'help': "Convert name from UTF-8 to ASCII. Default = no, keep UTF-8", 'action': 'store_true', 'default': False}
option_wsserver = {'names': ('-z', '--ws-server'), 'dest': 'wsserver', 'help': "DNS or IP address of the Web Socket Server", 'action': 'store', 'default': 'localhost'}

options = [option_server, option_port, option_ssl, option_database, option_user, option_password, option_ascii, option_wsserver]

def stdout_write(string):
    '''Wrapper on sys.stdout.write'''
    sys.stdout.write(string.encode(sys.stdout.encoding or 'utf-8', 'replace'))
   # sys.stdout.write(string)
    sys.stdout.flush()
    # When we output a command, we get an answer "200 result=1" on stdin
    # Purge stdin to avoid these Asterisk error messages :
    # utils.c ast_carefulwrite: write() returned error: Broken pipe
    input_line = sys.stdin.readline()
    return True

def stderr_write(string):
    '''Wrapper on sys.stderr.write'''
    sys.stderr.write(string.encode(sys.stdout.encoding or 'utf-8', 'replace'))
    #sys.stderr.write(string)
    sys.stderr.flush()
    return True


def reformat_phone_number_before_query_openerp(number):
    '''We match only on the end of the phone number'''
    if len(number) >= 9:
        return number[-9:len(number)] # Take 9 last numbers
    else:
        return number

def convert_to_ascii(my_unicode):
    '''Convert to ascii, with clever management of accents (é -> e, è -> e)'''
    import unicodedata
    if isinstance(my_unicode, unicode):
        my_unicode_with_ascii_chars_only = ''.join((char for char in unicodedata.normalize('NFD', my_unicode) if unicodedata.category(char) != 'Mn'))
        return str(my_unicode_with_ascii_chars_only)
    # If the argument is already of string type, we return it with the same value
    elif isinstance(my_unicode, str):
        return my_unicode
    else:
        return False

def main(options, arguments):
    
    def _get_caller_name(details):
        person = details['contact_name'] if 'contact_name' in details else False
        partner = details['partner_name'] if 'partner_name' in details else False
        
        if person:
            if partner: return '%s (%s)' % (person, partner)
            return person
        
        if partner: return partner
        
        return 'Name Not Found'


    # AGI passes parameters to the script on standard input
    stdinput = {}
    while 1:
        input_line = sys.stdin.readline()
        if not input_line:
            break
        line = input_line.strip()
        try:
            variable, value = line.split(':')
        except:
            break
        if variable[:4] != 'agi_': # All AGI parameters start with 'agi_'
            stderr_write("bad stdin variable : %s\n" % variable)
            continue
        variable = variable.strip()
        value = value.strip()
        if variable and value:
            stdinput[variable] = value

    stderr_write("full AGI environment :\n")
    
    for variable in stdinput.keys():
        stderr_write("%s = %s\n" % (variable, stdinput.get(variable)))

    # If we already have a "True" caller ID name
    # i.e. not just digits, but a real name, then we don't try to
    # connect to OpenERP or geoloc, we just keep it
    if stdinput.get('agi_calleridname') and not stdinput.get('agi_calleridname').isdigit() and stdinput.get('agi_calleridname').lower() not in ['asterisk', 'unknown', 'anonymous']:
        stdout_write('VERBOSE "Incoming CallerID name is %s"\n' % stdinput.get('agi_calleridname'))
        stdout_write('VERBOSE "As it is a real name, we do not change it"\n')
        return True


    input_cid_number = stdinput.get('agi_callerid', False)
    extension = stdinput.get('agi_extension',False)

    stderr_write('stdout encoding = %s\n' % sys.stdout.encoding or 'utf-8')

    if not isinstance(input_cid_number, str):
        stdout_write('VERBOSE "CallerID number is empty"\n')
        exit(0)
    # Match for particular cases and anonymous phone calls
    # To test anonymous call in France, dial 3651 + number
    if not input_cid_number.isdigit():
        stdout_write('VERBOSE "CallerID number (%s) is not a digit"\n' % input_cid_number)
        exit(0)

    stdout_write('VERBOSE "CallerID number = %s"\n' % input_cid_number)

    #query_number = reformat_phone_number_before_query_openerp(input_cid_number) - Les2Do - improve this 
    #Do the number formatting for query in openerp otherwise the called in number gets cut.  Depends on the settings
    #of the inbound trunk.
    query_number = input_cid_number
    stderr_write("phone number sent to OpenERP = %s\n" % query_number)

    stdout_write('VERBOSE "Starting XML-RPC request on OpenERP %s:%s"\n' % (options.server, str(options.port)))
   
    protocol = 'https' if options.ssl else 'http'
    stdout_write('VERBOSE "Starting %s XML-RPC request on OpenERP %s:%s"\n' % ('clear' if protocol=='http' else 'secure' ,options.server, str(options.port)))
    
    sock = xmlrpclib.ServerProxy('%s://%s:%s/xmlrpc/object' % (protocol, options.server, str(options.port)))

    call_details = sock.execute(options.database, options.user, options.password, 'res.partner', 'setup_call_inbound', query_number, extension)

    if 'openerp_call_id' in call_details:
        stdout_write('SET VARIABLE OPENERP_CALL_ID %s\n' % call_details['openerp_call_id'])
 
    # To simulate a long execution of the XML-RPC request
    #import time
    #time.sleep(5)
    res = _get_caller_name(call_details)
    stdout_write('VERBOSE "End of XML-RPC request on OpenERP"\n')

    # Function to limit the size of the CID name to 40 chars
    if res:
        if len(res) > 40:
            res = res[0:40]
    else:
        # if the number is not found in OpenERP, we put 'default_cid_name' as CID Name
        res = default_cid_name

    # All SIP phones should support UTF-8... but in case you have analog phones over TDM
    # or buggy phones, you should use the command line option --ascii
    if options.ascii:
        res = convert_to_ascii(res)

    stdout_write('VERBOSE "CallerID Name = %s"\n' % res)
    stdout_write('SET CALLERID "%s"<%s>\n' % (res, input_cid_number))
   
    if not extension:
        stdout_write('VERBOSE "No Called Number was passed - highly unusual"\n')
        return

    #Web Sockets Call
    if not options.wsserver.startswith('ws://'):
        wsserver = 'ws://%s' % options.wsserver
    else:
        wsserver = options.wsserver

    factory = WampClientFactory(wsserver)
    factory.protocol = OpenERPWampClientProtocol
    factory.protocol.call_details = call_details
    factory.protocol.extension = extension
    connectWS(factory)
    reactor.run()

if __name__ == '__main__':
    parser = OptionParser()
    for option in options:
        param = option['names']
        del option['names']
        parser.add_option(*param, **option)
    options, arguments = parser.parse_args()
    sys.argv[:] = arguments
    main(options, arguments)

;
; asterisk360 generated sample configuration file.
;

[py-asterisk]
default connection=my-pbx
default openerp=local
default websockets=local

[connection: my-pbx]
hostname=${cfg['asterisk_server_address']}
port=${cfg['asterisk_port']}
username=callevent
secret=asterisk

[openerp: local]
server=${cfg['openerp_ip_address']}
port=${cfg['openerp_port']}
uid=${cfg['user_id']}
pwd=${cfg['user_password']}
timeout=${cfg['agi_timeout']}
db=${cfg['openerp_db']}

[websockets: local]
ws-server=${cfg['websocket_server_address']}
ws-port=${cfg['websocket_server_port']}
log-file=${cfg['ws_logfile']}
debug=${cfg['ws_debug']}

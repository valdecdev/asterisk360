timeout ${cfg['agi_timeout']}s ${cfg['agi_path']} -s ${cfg['openerp_ip_address']} -d ${cfg['openerp_db']} -u ${cfg['user_id']} -w "${cfg['user_password']}" -z "${cfg['websocket_server_address']}"

openerp.asterisk360 = function(instance) {

    var QWeb = instance.web.qweb,
        _t = instance.web._t,
        abSession = null;

instance.asterisk360.Indicator = instance.web.Widget.extend({
    template: 'Systray.Asterisk360',

    init: function() {
        this._super();
        this.on('load', this, this.load);
    },

    onEvent: function(topicUri, event) {
        console.log(event);

        var action_manager = instance.webclient.action_manager;
        var form = new instance.web.form.FormOpenPopup(action_manager);

        if (event.contact_id) {
            var showId = event.contact_id

           // form.show_element('asterisk360.inbound.call.partner', showId,
             form.show_element('', showId,
                {'no_dial_button': true,
                 'openerp_call_id': event.openerp_call_id },
                {'title':_.str.sprintf(_t("Incoming Call From %(contact_name)s (%(parent_name)s)"),
                    { contact_name: event.contact_name, parent_name: event.parent_name }
                ) });

            form.view_form.has_been_loaded.pipe(function (){
                var elem = form.$el.find('a[href*="#notebook"]:contains("' + _t('Calls') +'")');
                form.$el.find(elem[0]).click();
            });
        } else {
            form.show_element('crm.phonecall', event.openerp_call_id ,{'no_dial_button':true }, {
                'title':_t('Incoming Call From Unknown Caller'),
                'readonly':false,
                'no_dial_button':true,
                'view_id': 349 //TODO: PUT THIS INTO CONFIG
            });
        }
    },

    start: function() {
        var self = this;
        this._super();

        this.trigger('load');
    },

    aboutbox: function(e) {
       // e.preventDefault();
       // var $help = $(QWeb.render("valuedecision.about", {}));
       // $help.dialog({autoOpen: true, modal: true, width: 960, title: "About ValueDecision Ltd."});
       // return false;
        var event = {
            contact_id: 53,
            contact_name: "Arthur Gomez",
            parent_id: 20,
            parent_name: "Spark Systems"
        }
        console.log(event);

        var action_manager = instance.webclient.action_manager;
        var form = new instance.web.form.FormOpenPopup(action_manager);

        if (event.contact_id) {
            var showId = event.contact_id

            form.show_element('asterisk360.inbound.call.partner', showId, {'no_dial_button': true},
                {'title':_.str.sprintf(_t("Incoming Call From %(contact_name)s (%(parent_name)s)"),
                    { contact_name: event.contact_name, parent_name: event.parent_name }
                ), 'readonly':true});

            form.view_form.has_been_loaded.pipe(function (){
                var elem = form.$el.find('a[href*="#notebook"]:contains("' + _t('Calls') +'")');
                form.$el.find(elem[0]).click();
            });
        }


    },

    load: function() {
        var self = this;

        new instance.web.DataSet(this, "res.users")
            .read_ids([this.session.uid],
                ['name','screen_pop','internal_number','asterisk_server_id'])
            .then(function(result) {
                var user = result[0];
                var sess = instance.webclient.session;
                sess.screen_pop = user.screen_pop;
                sess.user_phone = user.internal_number;
                if (sess.screen_pop==true) {
                    new instance.web.DataSetStatic(this, "asterisk.server")
                        .read_ids([user.asterisk_server_id[0]],
                            ['name','ws_address'])
                        .then(function(result){
                            sess.ws_address=result[0].ws_address;
                            self.connect();
                        });
                } else {
                    self.set_title_img(_t("Screen Pop Off"));
                }
            });

        this.$el.click(self.aboutbox);
    },

    set_title_img: function(title, src){
        var elem = this.$el.find("#t4_web_telephony_indicator");
        elem.attr("title", title);
        if (src) {
            elem.css('background-image', 'url("' + "/asterisk360/static/src/img/" + src + '")');
        }
    },

    connect: function() {
        var sess = instance.webclient.session;
        var self = this;
        console.log('CONNECTING');
        if (!self.abSession) {
            self.wsconnecting = true;
            ab.connect(sess.ws_address,
                function(session) {
                    self.abSession = session;
                    self.abSession.prefix("callsto","asterisk360/callsto#");
                    console.log("subscribing:" + sess.user_phone);
                    self.abSession.subscribe("callsto:" + sess.user_phone,
                        //On event Callback
                        self.onEvent);
                    self.set_title_img(_t("Connected"), "call_green.png");
                },
                //Wamp Session Disconnected - not exisiting
                function(){
                    console.log("failure");
                    self.set_title_img(_t("Not Connected"), "call_red.png");
                    self.abSession = null;
                    var connecting = self.wsconnecting;
                    if (!connecting){
                        self.connect();
                    }
                })
        }
    }
});

// here you may tweak globals object, if any, and play with on_* or do_* callbacks on them
instance.web.UserMenu.include({
    do_update: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.update_promise.done(function() {
            if (self.asterisk360) {
                self.asterisk360.trigger('load');
            } else {
                self.asterisk360 = new instance.asterisk360.Indicator(self);
                self.asterisk360.appendTo(instance.webclient.$el.find('.oe_systray'));
            }
        });
    }
});


instance.web.Login = instance.web.Login.extend({
    start: function() {
        console.log('Hello there');
        console.log(instance.web.client_actions);

        return this._super.apply(this,arguments);
    }
});

instance.web.WebClient.extend({
    show_application: function() {
        var self = this;
        self.toggle_bars(false);
        self.update_logo();
        self.menu = new instance.web.Menu(self);
        self.menu.replace(this.$el.find('.oe_menu_placeholder'));
        self.menu.on('menu_click', this, this.on_menu_action);
        self.user_menu = new instance.web.UserMenu(self);
        self.user_menu.replace(this.$el.find('.oe_user_menu_placeholder'));
        self.user_menu.on('user_logout', self, self.on_logout);
        self.user_menu.do_update();
        self.bind_hashchange();
        self.set_title();
        self.check_timezone();
    }
});

//    instance.web.Sidebar = instance.web.Widget.extend({
//        init: function(){
//
//            console.log("SIDEBAR INIT FOO");
//
//        },
//        start: function() {
//            console.log("SIDEBAR START FOO");
//        },
//        add_items: function() {
//            console.log("I WON'T ADD ITEMS");
//        },
//        redraw: function() {
//            console.log("I REFUSE TO REDRAW");
//        }
//
//});

};

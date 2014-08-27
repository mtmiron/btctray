#!/usr/bin/env python

# CoinDesk price URL is https://api.coindesk.com/v1/bpi/currentprice.json 
# (however the returned JSON is of a different structure than Coinbase)


import os
import sys
import gtk
import gio
import urllib
import json
import glib
import time


class BTCTray(gtk.StatusIcon):
        # The spot_rate is defined by Coinbase as falling somewhere between their current buy & sell prices
        PRICEURL = 'https://coinbase.com/api/v1/prices/spot_rate'
        UPDATEINTERVAL = 3600

        def __init__(self):
            gtk.StatusIcon.__init__(self)
            menu = '''
                        <ui>
                         <menubar name="Menubar">
                          <menu action="Menu">
                           <menuitem action="Options"/>
                           <menuitem action="About"/>
                           <separator/>
                           <menuitem action="Quit"/>
                          </menu>
                         </menubar>
                        </ui>
            '''
            actions = [
                ('Menu',  None, 'Menu'),
                ('Options', gtk.STOCK_PREFERENCES, '_Options', None, 'Open the pref dialog', self.on_options),
                ('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit the application', self.on_quit),
                ('About', gtk.STOCK_ABOUT, '_About...', None, 'About BTCTray', self.on_about),
            ]

            self.options = {'update_interval': self.UPDATEINTERVAL}
            sets = gtk.settings_get_default()
            sets.set_long_property('gtk-tooltip-timeout', 0, 'BTCTray.__init__')

            ag = gtk.ActionGroup('Actions')
            ag.add_actions(actions)
            self.manager = gtk.UIManager()
            self.manager.insert_action_group(ag, 0)
            self.manager.add_ui_from_string(menu)
            self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent

            self.set_from_file("bitcoin-black.png")
            self.set_visible(True)
            self.connect('activate', self.on_activate)
            self.connect('popup-menu', self.on_popup_menu)
            self.price = { 'amount': '0.00', 'currency': 'USD' }


        def set_update_interval(self, data):
            self.options['update_interval'] = int(self.update_interval_entry.get_text())

        def on_options(self, data):
            self.options_window = gtk.Window()
            self.update_interval_entry = entry = gtk.Entry()
            entry.set_tooltip_text("Update interval in minutes.")
            entry.set_text(str(self.options['update_interval']))
            entry.connect('activate', self.set_update_interval)
            hbox = gtk.HBox()
            label = gtk.Label("Update interval: ")
            hbox.pack_start(label)
            hbox.pack_end(entry)
            self.options_window.add(hbox)
            entry.show()
            hbox.show()
            label.show()
            self.options_window.show()


        def on_activate(self, data):
            # Reset our update timer since user has just forced a refresh
            glib.source_remove(self.current_timeout_id)
            self.current_timeout_id = glib.timeout_add_seconds(self.options['update_interval'], self.update_price)
            self.update_price()


        def on_popup_menu(self, status, button, time):
            self.menu.popup(None, None, None, button, time)


        def on_about(self, data):
            dialog = gtk.AboutDialog()
            dialog.set_name('BTCTray')
            dialog.set_authors(('Murray Miron',))
            dialog.set_website('https://github.com/mtmiron/btctray')
            dialog.set_comments('A bitcoin price "widget."  Click to manually update price (auto updates every ' + str(BTCTray.UPDATEINTERVAL) + ' secs).')
            dialog.run()
            dialog.destroy()


        def on_quit(self, data):
            os._exit(0)


        def update_price(self, data = None, uri = PRICEURL):
            '''Updates the current price via a REST call.'''
            try:
                url = urllib.urlopen(uri)
                resp = url.read()
                url.close()
                self.price = json.loads(resp)
		self.set_tooltip_markup("<b>$%s</b>   <small>%s</small>" % (self.price['amount'], time.strftime("%X")))
            except IOError as err:
                str_price = "%s %s" % (self.price['amount'], self.price['currency'])
                self.set_tooltip(str(err) + " (last known price " + str_price + ')')
            return True


        def daemonize(self):
            try:
                sys.stdin.close()
                #sys.stdout.close()
                #sys.stderr.close()
            except (OSError, IOError, SystemError):
                pass

            try:
                pid = os.fork()
            except OSError, e:
                raise Exception, "%s [%d]" % (e.strerror, e.errno)
            if (pid == 0):
                os.setsid()
                try:
                    pid = os.fork()
                except OSError, e:
                    raise Exception, "%s [%d]" % (e.strerror, e.errno)
                if (pid == 0):
                    os.chdir('/')
                else:
                    os._exit(0)
            else:
                os._exit(0)


if __name__ == '__main__':
    app = BTCTray()
    app.daemonize()
    app.update_price()
    app.current_timeout_id = glib.timeout_add_seconds(BTCTray.UPDATEINTERVAL, app.update_price)
    gtk.mainloop()

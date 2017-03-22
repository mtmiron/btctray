#!/usr/bin/env python2

# CoinDesk price URL is https://api.coindesk.com/v1/bpi/currentprice.json 
# (however the returned JSON is of a different structure than Coinbase)


import os
import sys
import gtk
import gio
import urllib2
import json
import glib
import time


class BTCTray(gtk.StatusIcon):
        # The spot_rate is defined by Coinbase as falling somewhere between their current buy & sell prices
        PRICEURL = 'https://coinbase.com/api/v1/prices/spot_rate'
        UPDATEINTERVAL = 60

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

            self.options = {}
            self.options['update_interval'] = self.read_update_interval()
            self.options['price_alert'] = self.read_price_alert()
            self.price_alert = self.options['price_alert']

            sets = gtk.settings_get_default()
            sets.set_long_property('gtk-tooltip-timeout', 0, 'BTCTray.__init__')

            ag = gtk.ActionGroup('Actions')
            ag.add_actions(actions)
            self.manager = gtk.UIManager()
            self.manager.insert_action_group(ag, 0)
            self.manager.add_ui_from_string(menu)
            self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent

            self.set_from_file(os.path.dirname(os.path.realpath(sys.argv[0])) + "/bitcoin.png")
            self.set_visible(True)
            self.connect('activate', self.on_activate)
            self.connect('popup-menu', self.on_popup_menu)
            self.price = { 'amount': '0.00', 'currency': 'USD' }


        def set_update_interval(self, data = None, filename = None):
            self.options['update_interval'] = int(self.update_interval_entry.get_text())
            if filename is None:
                filename = os.environ['HOME'] + '/.btctray/update_interval'
            if not os.path.exists(filename):
                try:
                    os.mkdir(os.path.dirname(filename))
                except Exception, e:
                    sys.stderr.write(str(e))
            f = open(filename, 'w')
            f.write(str(self.options['update_interval']))
            f.close()
            self.options_window.destroy()


        def set_price_alert(self, data = None, filename = None):
            self.options['price_alert'] = float(self.price_alert_entry.get_text())
            self.price_alert = self.options['price_alert']
            if filename is None:
                filename = os.environ['HOME'] + '/.btctray/price_alert'
            if not os.path.exists(filename):
                try:
                    os.mkdir(os.path.dirname(filename))
                except Exception, e:
                    sys.stderr.write(str(e))
            f = open(filename, 'w')
            f.write(str(self.options['price_alert']))
            f.close()
            self.options_window.destroy()


        def read_update_interval(self, data = None, filename = None):
            if filename is None:
                filename = os.environ['HOME'] + '/.btctray/update_interval'
            if os.path.exists(filename):
                f = open(filename, 'r')
                try:
                    self.options['update_interval'] = int(f.read())
                    return self.options['update_interval']
                finally:
                    f.close()
            else:
                return BTCTray.UPDATEINTERVAL


        def read_price_alert(self, data = None, filename = None):
            if filename is None:
                filename = os.environ['HOME'] + '/.btctray/price_alert'
            if os.path.exists(filename):
                f = open(filename, 'r')
                try:
                    self.options['price_alert'] = float(f.read())
                    self.price_alert = self.options['price_alert']
                    return self.options['price_alert']
                finally:
                    f.close()
            else:
                return self.price_alert


        def on_options(self, data):
            self.options_window = gtk.Window()
            self.update_interval_entry = entry = gtk.Entry()
            entry.set_tooltip_text("Update interval in minutes (enter 0 for manual updates only).")
            entry.set_text(str(self.options['update_interval']))
            entry.connect('activate', self.set_update_interval)
            entry.connect('activate', self.set_price_alert)

            vbox = gtk.VBox()
            vbox.show()

            hbox = gtk.HBox()
            label = gtk.Label("Update interval: ")
            hbox.pack_start(label)
            hbox.pack_end(entry)
            vbox.pack_start(hbox)

            hbox2 = gtk.HBox()
            label2 = gtk.Label("Notify on price breaking: ")
            self.price_alert_entry = entry2 = gtk.Entry()
            entry2.set_text(str(self.options['price_alert']))
            entry2.connect('activate', self.set_price_alert)
            entry2.connect('activate', self.set_update_interval)

            hbox2.pack_start(label2)
            hbox2.pack_end(entry2)
            vbox.pack_end(hbox2)

            hbox2.show()
            label2.show()
            entry2.show()

            entry.show()
            hbox.show()
            label.show()

            self.options_window.add(vbox)
            self.options_window.show()


        def on_activate(self, data = None):
            # Reset our update timer since user has just forced a refresh
            try:
                glib.source_remove(self.current_timeout_id)
            except e:
                sys.stderr.write(str(e))
            if self.options['update_interval'] != 0:
                self.current_timeout_id = glib.timeout_add_seconds(self.options['update_interval'] * 60, self.update_price)
            self.update_price()


        def on_popup_menu(self, status, button, time):
            self.menu.popup(None, None, None, button, time)


        def on_about(self, data):
            dialog = gtk.AboutDialog()
            dialog.set_name('BTCTray')
            dialog.set_authors(('Murray Miron',))
            dialog.set_website('https://github.com/mtmiron/btctray')
            dialog.set_comments('A bitcoin price "widget."  Click to manually update price (auto updates every ' + str(self.options['update_interval']) + ' mins).')
            dialog.run()
            dialog.destroy()


        def show_price_alert(self, data = None):
            dialog = gtk.AboutDialog()
            dialog.set_name('Price Alert')
            dialog.set_comments("The Bitcoin price has passed your specified value.")
            dialog.run()
            dialog.destroy()


        def on_quit(self, data):
            os._exit(0)


        def update_price(self, data = None, url = PRICEURL):
            '''Updates the current price via a REST call.'''
            try:
                old_price = float(self.price['amount'])
                self.set_tooltip_markup("<b>Loading...</b>  <small>%s</small>" % time.strftime("%X"))
                op = urllib2.build_opener()
                op.addheaders = [('User-Agent', "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"), ('Connection', 'close')]
                sock = op.open(url)
                resp = sock.read()
                sock.close()
                self.price = json.loads(resp)
                self.set_tooltip_markup("<b>$%s</b>   <small>%s</small>" % (self.price['amount'], time.strftime("%X")))

                #sys.stderr.write("old_price: %f  price_alert: %f  price:  %f\n" % (old_price, self.price_alert, float(self.price['amount'])))
                if (old_price == 0):
                    return
                elif (old_price > self.price_alert) and (float(self.price['amount']) < self.price_alert):
                    self.show_price_alert()
                elif (old_price < self.price_alert) and (float(self.price['amount']) > self.price_alert):
                    self.show_price_alert()

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
    app.current_timeout_id = glib.timeout_add_seconds(2, app.on_activate)
    gtk.mainloop()

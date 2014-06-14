#!/usr/bin/env python


import os
import gtk
import gio
import urllib
import json
import glib


class BTCTray(gtk.StatusIcon):
        PRICEURL = 'https://coinbase.com/api/v1/prices/spot_rate'
        UPDATEINTERVAL = 300

	def __init__(self):
		gtk.StatusIcon.__init__(self)
		menu = '''
			<ui>
			 <menubar name="Menubar">
			  <menu action="Menu">
                           <menuitem action="Quit"/>
			   <separator/>
			   <menuitem action="About"/>
			  </menu>
			 </menubar>
			</ui>
		'''
		actions = [
			('Menu',  None, 'Menu'),
                        ('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit the application', self.on_quit),
			('About', gtk.STOCK_ABOUT, '_About...', None, 'About BTCTray', self.on_about),
                ]

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

	def on_activate(self, data):
            self.update_price()
            #os.spawnlpe(os.P_NOWAIT, 'tracker-search-tool', os.environ)

	def on_popup_menu(self, status, button, time):
		self.menu.popup(None, None, None, button, time)

        def on_about(self, data):
		dialog = gtk.AboutDialog()
		dialog.set_name('BTCTray')
		dialog.set_version('0.1')
		dialog.set_comments('A bitcoin price "widget."  Click to issue a manual price update (default interval ' + str(BTCTray.UPDATEINTERVAL) + 's).')
		dialog.run()
		dialog.destroy()

        def on_quit(self, data):
            exit(0)


        def update_price(self):
            try:
                url = urllib.urlopen(BTCTray.PRICEURL)
                resp = url.read()
                url.close()
                self.price = json.loads(resp)
		self.set_tooltip(self.price['amount'] + " " + self.price['currency'])
            except IOError:
                pass



if __name__ == '__main__':
	app = BTCTray()
        app.update_price()

        glib.timeout_add_seconds(BTCTray.UPDATEINTERVAL, app.update_price)
	gtk.main()

#!/usr/bin/env python

# price URL: https://coinbase.com/api/v1/prices/spot_rate



import os
import gtk

class TrackerStatusIcon(gtk.StatusIcon):
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
		#search = self.manager.get_widget('/Menubar/Menu/Search')
		#search.get_children()[0].set_markup('<b>_Search...</b>')
		#search.get_children()[0].set_use_underline(True)
		#search.get_children()[0].set_use_markup(True)
		#search.get_children()[1].set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
		self.set_from_stock(gtk.STOCK_FIND)
		self.set_tooltip('Tracker Desktop Search')
		self.set_visible(True)
		self.connect('activate', self.on_activate)
		self.connect('popup-menu', self.on_popup_menu)

	def on_activate(self, data):
		os.spawnlpe(os.P_NOWAIT, 'tracker-search-tool', os.environ)

	def on_popup_menu(self, status, button, time):
		self.menu.popup(None, None, None, button, time)

        def on_about(self, data):
		dialog = gtk.AboutDialog()
		dialog.set_name('Tracker')
		dialog.set_version('0.5.0')
		dialog.set_comments('A desktop indexing and search tool')
		dialog.set_website('www.freedesktop.org/Tracker')
		dialog.run()
		dialog.destroy()

        def on_quit(self, data):
            exit(0)


if __name__ == '__main__':
	TrackerStatusIcon()
	gtk.main()



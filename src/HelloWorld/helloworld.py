#!/usr/bin/python3
# pylint: disable=E1101

"""
# File: helloworld.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Plugin example for MiAZ
"""

import os
import sys

from gi.repository import GObject
from gi.repository import Peas
from gi.repository import Adw

from MiAZ.backend.log import MiAZLog

path = os.path.join(os.path.abspath(__file__), 'example')
sys.path.insert(1, os.path.abspath(__file__))
from example.test import PluginTest

class HelloWorld(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'HelloWorldPlugin'
    object = GObject.Property(type=GObject.Object)
    info = {}

    def register_plugin(self):
        plugin_file = __file__.replace('.py', '.plugin')
        self.info = self.object.get_plugin_attributes(plugin_file)
        module = self.info['Module']
        self.app.add_widget(f'plugin-{module}', self)
        self.log.info(f"Registered widget plugin plugin-{module}")

    def do_activate(self):
        """Plugin activation"""

        # Get app pointer
        self.app = self.object.app

        # Register logger
        self.log = MiAZLog('Plugin.HelloWorld')

        # Register plugin
        self.register_plugin()

        # Get necessary services

        ## Workspace widget will emit a signal when it is loaded
        ## Plugin connects to it to start up the plugin
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)

        ## Actions service will emit a signal when settings were loaded
        ## Plugin connects to it to add its custom settings
        actions = self.app.get_service('actions')
        actions.connect('settings-loaded', self._on_settings_loaded)


    def do_deactivate(self):
        """Plugin deactivation"""
        print("Deactivation not implemented. Restart app to disable plugins.")

    def startup(self, *args):
        factory = self.app.get_service('factory')

        # Create menu item for plugin
        menuitem = factory.create_menuitem('plugin-menuitem-helloworld', 'Hello World!', self._on_menuitem_activate, None, [])
        self.app.add_widget('window-headerbar-togglebutton-workspace-view', menuitem)

        # Add plugin to its default (sub)category
        category = self.info['Category']
        subcategory = self.info['Subcategory']
        subcategory_submenu = self.app.install_plugin_menu(category, subcategory)
        subcategory_submenu.append_item(menuitem)

    def _on_menuitem_activate(self, *args):
        test = PluginTest(self.app)

    def _on_settings_loaded(self, *args):
        group = self.app.get_widget('window-preferences-page-aspect-group-ui')
        row = Adw.SwitchRow(title=_("Hello world!"), subtitle=_('Plugin HelloWorld'))
        row.connect('notify::active', self._on_activate_setting)
        group.add(row)

    def _on_activate_setting(self, row, gparam):
        srvdlg = self.app.get_service('dialogs')
        active = row.get_active()
        dtype = "info"
        title = _(f'<big>Row active {active}</big>')
        body=''
        window = row.get_root()
        dialog = srvdlg.create(dtype=dtype, title=title, body=body, widget=None)
        dialog.present(window)

    def show_settings(self):
        self.log.info("Got it!")

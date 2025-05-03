#!/usr/bin/python3
# pylint: disable=E1101

"""
# File: hello.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Scan plugin
"""

import os
import re
import glob

from gi.repository import Adw
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.pluginsystem import MiAZPlugin


class MiAZSidebarToggleButtonPlugin(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZSidebarToggleButtonPlugin'
    object = GObject.Property(type=GObject.Object)
    plugin = None
    file = __file__.replace('.py', '.plugin')

    def do_activate(self):
        """Plugin activation"""
        # Setup plugin
        ## Get pointer to app
        self.app = self.object.app
        self.plugin = MiAZPlugin(self.app)

        ## Initialize plugin
        self.plugin.register(self.file)

        ## Get logger
        self.log = self.plugin.get_logger()

        # Connect signals to startup
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        self.log.warning("Deactivation not implemented")

    def startup(self, *args):
        # Create menu item for plugin
        menuitem = self.plugin.get_menu_item(callback=None)

        # Add plugin to its default (sub)category
        self.plugin.install_menu_entry(menuitem)

        factory = self.app.get_service('factory')
        sidebar = self.app.get_widget('sidebar')
        hdb_left = self.app.get_widget('headerbar-left-box')
        tgbSidebar = self.app.get_widget('workspace-togglebutton-sidebar')
        if tgbSidebar is None:
            tgbSidebar = factory.create_button_toggle('io.github.t00m.MiAZ-sidebar-show-left-symbolic', callback=self.toggle_sidebar)
            self.app.add_widget('workspace-togglebutton-sidebar', tgbSidebar)
            tgbSidebar.set_tooltip_text("Show sidebar and filters")
            tgbSidebar.set_active(True)
            tgbSidebar.set_hexpand(False)
            tgbSidebar.get_style_context().add_class(class_name='dimmed')
            hdb_left.append(tgbSidebar)

            evk = self.app.get_widget('window-event-controller')
            evk.connect("key-pressed", self._on_key_press)

            self.log.debug("Plugin sidebartgb activated")

    def toggle_sidebar(self, *args):
        """ Sidebar not visible when active = False"""
        sidebar = self.app.get_widget('sidebar')
        tgbSidebar = self.app.get_widget('workspace-togglebutton-sidebar')
        active = tgbSidebar.get_active()
        sidebar.set_visible(active)

    def _on_key_press(self, event, keyval, keycode, state):
        keyname = Gdk.keyval_name(keyval)
        if keyname == 'Escape':
            tgbSidebar = self.app.get_widget('workspace-togglebutton-sidebar')
            active = tgbSidebar.get_active()
            tgbSidebar.set_active(not active)

    def _on_settings_loaded(self, *args):
        group = self.app.get_widget('window-preferences-page-aspect-group-ui')
        row = Adw.SwitchRow(title=_("Display sidebar toggle button?"), subtitle=_('Plugin Sidebar ToggleButton'))
        row.connect('notify::active', self._on_activate_setting)
        tgbSidebar = self.app.get_widget('workspace-togglebutton-sidebar')
        visible = tgbSidebar.get_visible()
        row.set_active(visible)
        group.add(row)

    def _on_activate_setting(self, row, gparam):
        active = row.get_active()
        togglebutton = self.app.get_widget('workspace-togglebutton-sidebar')
        togglebutton.set_visible(active)





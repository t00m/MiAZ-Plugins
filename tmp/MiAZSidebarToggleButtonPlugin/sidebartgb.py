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
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.log import MiAZLog


class MiAZSidebarToggleButtonPlugin(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZSidebarToggleButtonPlugin'
    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        self.log = MiAZLog('Plugin.SidebarTgb')
        self.app = None
        self.scanapp = None

    def do_activate(self):
        self.app = self.object.app
        actions = self.app.get_service('actions')
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.add_menuitem)
        actions.connect('settings-loaded', self._on_settings_loaded)

    def do_deactivate(self):
        self.log.error("Plugin deactivated")
        # ~ hdb_left = self.app.get_widget('headerbar-left-box')
        # ~ tgbSidebar = self.app.get_widget('workspace-togglebutton-sidebar')
        # ~ if tgbSidebar is not None:
            # ~ hdb_left.remove(tgbSidebar)
            # ~ self.log.info("Plugin sidebartgb deactivated")
        # ~ self.log.warning("Plugin deactivation not possible. Widget doesn't exist")

    def check_plugin(self, *args):
        self.log.info(f"Plugin loaded? {self.plugin_info.is_loaded()}")

    def add_menuitem(self, *args):
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

            # Create menu item for plugin
            menuitem = factory.create_menuitem('togglebutton_sidebar', 'Toggle sidebar button', None, None, [])
            self.app.add_widget('window-headerbar-togglebutton-sidebar', menuitem)

            # ~ # Add plugin to its default (sub)category
            category = self.app.get_widget('workspace-menu-plugins-visualisation-and-diagrams-dashboard-widgets')
            category.append_item(menuitem)

            # This is a common action: add to shortcuts
            # ~ menu_shortcut_import = self.app.get_widget('workspace-menu-shortcut-import')
            # ~ menu_shortcut_import.append_item(menuitem)
            self.log.debug("Plugin sidebartgb activated")

    def toggle_sidebar(self, *args):
        """ Sidebar not visible when active = False"""
        sidebar = self.app.get_widget('sidebar')
        tgbSidebar = self.app.get_widget('workspace-togglebutton-sidebar')
        active = tgbSidebar.get_active()
        sidebar.set_visible(active)

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





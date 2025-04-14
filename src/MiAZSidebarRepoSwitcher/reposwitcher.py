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
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.log import MiAZLog
from MiAZ.backend.models import Repository
from MiAZ.backend.config import MiAZConfigRepositories


class MiAZSidebarRepoSwitcher(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZSidebarRepoSwitcherPlugin'
    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        self.log = MiAZLog('Plugin.SidebarRepoSwitch')
        self.app = None
        self.scanapp = None

    def do_activate(self):
        self.app = self.object.app
        actions = self.app.get_service('actions')
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)
        # ~ actions.connect('settings-loaded', self._on_settings_loaded)

    def do_deactivate(self):
        self.log.error("Plugin deactivated")

    def check_plugin(self, *args):
        self.log.info(f"Plugin loaded? {self.plugin_info.is_loaded()}")

    def startup(self, *args):
        actions = self.app.get_service('actions')
        factory = self.app.get_service('factory')
        sidebar = self.app.get_widget('sidebar')
        sidebar_box_title = self.app.get_widget('sidebar-box-title')
        sidebar_title = self.app.get_widget('sidebar-title')
        dd_repo = self.app.get_widget('sidebar-repo-switcher')
        if dd_repo is None:
            #### Configure repository dropdown
            dd_repo = factory.create_dropdown_generic(item_type=Repository, ellipsize=False, enable_search=True)
            dd_repo.connect("notify::selected-item", self._on_use_repo)
            self.app.add_widget('sidebar-repo-switcher', dd_repo)
            dd_repo.set_valign(Gtk.Align.CENTER)
            dd_repo.set_hexpand(False)
            togglebutton = dd_repo.get_first_child()
            togglebutton.set_has_frame(False)
            dd_repo.set_show_arrow(True)
            actions.dropdown_populate(MiAZConfigRepositories, dd_repo, Repository, any_value=False, none_value=False)
            sidebar_box_title.remove(sidebar_title)
            sidebar_box_title.append(dd_repo)
            sidebar_box_title.set_hexpand(False)

            # Create menu item for plugin
            # ~ menuitem = factory.create_menuitem('togglebutton_sidebar', 'Toggle sidebar button', None, None, [])
            # ~ self.app.add_widget('window-headerbar-togglebutton-sidebar', menuitem)

            # ~ # Add plugin to its default (sub)category
            # ~ category = self.app.get_widget('workspace-menu-plugins-visualisation-and-diagrams-dashboard-widgets')
            # ~ category.append_item(menuitem)

            # This is a common action: add to shortcuts
            # ~ menu_shortcut_import = self.app.get_widget('workspace-menu-shortcut-import')
            # ~ menu_shortcut_import.append_item(menuitem)

            self.log.debug(f"Plugin {__class__.__name__} activated")

    def _on_use_repo(self, *args):
        """
        Load repository automatically whenever is selected.
        Once loaded, it is set as the default in the app config.
        """
        workflow = self.app.get_service('workflow')
        dd_repo = self.app.get_widget('sidebar-repo-switcher')
        repo = dd_repo.get_selected_item()
        if repo is None:
            return
        self.log.debug(f"Repository chosen: {repo.id}")
        config = self.app.get_config_dict()
        config['App'].set('current', repo.id)
        valid = workflow.switch_start()
        self.log.debug(f"Repository {repo.id} loaded successfully? {valid}")

    # ~ def _on_settings_loaded(self, *args):
        # ~ group = self.app.get_widget('window-preferences-page-aspect-group-ui')
        # ~ row = Adw.SwitchRow(title=_("Display sidebar toggle button?"), subtitle=_('Plugin Sidebar ToggleButton'))
        # ~ row.connect('notify::active', self._on_activate_setting)
        # ~ tgbSidebar = self.app.get_widget('workspace-togglebutton-sidebar')
        # ~ visible = tgbSidebar.get_visible()
        # ~ row.set_active(visible)
        # ~ group.add(row)

    # ~ def _on_activate_setting(self, row, gparam):
        # ~ active = row.get_active()
        # ~ togglebutton = self.app.get_widget('workspace-togglebutton-sidebar')
        # ~ togglebutton.set_visible(active)





#!/usr/bin/python3
# pylint: disable=E1101

"""
# File: export2text.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Plugin for exporting items filenames to plain text
"""

import tempfile
from gettext import gettext as _

from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.log import MiAZLog


class Copy2Clipboard(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZCopy2ClipboardPlugin'
    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        self.log = MiAZLog('Plugin.Copy2Clipboard')
        self.app = None

    def do_activate(self):
        self.app = self.object.app
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        print("Deactivation not implemented. Restart app to disable plugins.")


    def startup(self, *args):
        if self.app.get_widget('workspace-menu-export-copy2clipboard') is None:
            factory = self.app.get_service('factory')

            # Create menu item for plugin
            menuitem = factory.create_menuitem('copy-to-clipboard', _('... to clipboard'), self.export, None, [])
            self.app.add_widget('workspace-menu-export-copy2clipboard', menuitem)

            # Add plugin to its default (sub)category
            category = self.app.get_widget('workspace-menu-plugins-data-management-export')
            category.append_item(menuitem)

            # This is a common action: add to shortcuts
            submenu_export = self.app.get_widget('workspace-menu-selection-menu-export')
            submenu_export.append_item(menuitem)

    def export(self, *args):
        srvdlg = self.app.get_service('dialogs')
        actions = self.app.get_service('actions')
        workspace = self.app.get_widget('workspace')
        items = workspace.get_selected_items()
        if actions.stop_if_no_items(items):
            return

        text = ""
        for item in items:
            text += f"{item.id}\n"
        workspace.get_clipboard().set(text)
        body = ''
        window = workspace.get_root()
        srvdlg.create(enable_response=False, dtype='info', title=_(f"{len(items)} documents copied to clipboard"), body=body).present(window)

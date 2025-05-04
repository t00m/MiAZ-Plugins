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

from MiAZ.backend.pluginsystem import MiAZPlugin


class Export2Text(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZExport2TextPlugin'
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
        self.plugin.register(self.file, self)

        ## Get logger
        self.log = self.plugin.get_logger()

        # Connect signals to startup
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        self.log.warning("Deactivation not implemented")

    def startup(self, *args):
        if not self.plugin.menu_item_loaded():
            # Create menu item for plugin
            menuitem = self.plugin.get_menu_item(callback=self.export)

            # Add plugin to its default (sub)category
            self.plugin.install_menu_entry(menuitem)

    def export(self, *args):
        actions = self.app.get_service('actions')
        srvdlg = self.app.get_service('dialogs')
        ENV = self.app.get_env()
        util = self.app.get_service('util')
        workspace = self.app.get_widget('workspace')
        window = workspace.get_root()
        items = workspace.get_selected_items()
        if actions.stop_if_no_items(items):
            return

        text = ""
        for item in items:
            text += f"{item.id}\n"
        fp, filepath = tempfile.mkstemp(dir=ENV['LPATH']['TMP'], suffix='.txt')
        with open(filepath, 'w') as temp:
            temp.write(text)
        temp.close()
        util.filename_display(filepath)
        body = '<big>Check your default text editor</big>'
        srvdlg.create(dtype='info', title=_('Export successfull'), body=body).present(window)

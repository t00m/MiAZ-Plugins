#!/usr/bin/python3
# pylint: disable=E1101

"""
# File: export2csv.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Plugin for exporting items to CSV
"""

import csv
import tempfile
from gettext import gettext as _

from gi.repository import GObject
from gi.repository import Peas

from MiAZ.frontend.desktop.services.pluginsystem import MiAZPlugin


class Export2CSV(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZExport2CSVPlugin'
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

        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        self.log.debug("Plugin deactivation not implemented")

    def startup(self, *args):
        if not self.plugin.menu_item_loaded():
            # Create menu item for plugin
            menuitem = self.plugin.get_menu_item(callback=self.export)

            # Add plugin to its default (sub)category
            self.plugin.install_menu_entry(menuitem)

    def export(self, *args):
        util = self.app.get_service('util')
        actions = self.app.get_service('actions')
        srvdlg = self.app.get_service('dialogs')
        workspace = self.app.get_widget('workspace')
        window = workspace.get_root()
        ENV = self.app.get_env()
        fields = [_('Date'), _('Country'), _('Group'), _('Send by'), _('Purpose'), _('Concept'), _('Send to'), _('Extension')]
        items = workspace.get_selected_items()
        if actions.stop_if_no_items(items):
            return

        rows = []
        for item in items:
            name, ext = util.filename_details(item.id)
            row = name.split('-')
            row.append(ext)
            rows.append(row)
        fp, filepath = tempfile.mkstemp(dir=ENV['LPATH']['TMP'], suffix='.csv')
        with open(filepath, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerows(rows)
        util.filename_display(filepath)
        body = f"Check your default spreadsheet application"
        srvdlg.create(dtype='info', title=_('Export successfull'), body=body).present(window)

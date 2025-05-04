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

from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.pluginsystem import MiAZPlugin


class MiAZImportFromScanPlugin(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZImportFromScanPlugin'
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

        # Check any scan app and connect signal to startup
        scanapp = self._search_scan_app()
        if scanapp is not None:
            workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        self.log.warning("Deactivation not implemented")

    def startup(self, *args):
        if not self.plugin.menu_item_loaded():
            # Create menu item for plugin
            menuitem = self.plugin.get_menu_item(callback=self.exec_scanner)

            # Add plugin to its default (sub)category
            self.plugin.install_menu_entry(menuitem)

    def _search_scan_app(self):
        scanapp = None
        try:
            desktop_files = glob.glob('/usr/share/applications/*.desktop')
            DAI = Gio.DesktopAppInfo()
            for desktop_path in desktop_files:
                desktop_name = os.path.basename(desktop_path)
                try:
                    appinfo = DAI.new(desktop_name)
                    categories = appinfo.get_categories()
                    if categories is not None:
                        if re.search('scan', categories, re.IGNORECASE):
                            scanapp = appinfo
                            break
                except TypeError as error:
                    pass
                    # ~ self.log.error(f"Plugin 'scan' couldn't be activated: {error}")

        except AttributeError as error:
            # Not available in Windows/MSYS2
            self.log.error(f"Plugin 'scan' couldn't be activated: {error}")
        return scanapp

    def exec_scanner(self, *args):
        scanapp = self._search_scan_app()
        if scanapp is not None:
            scanapp.launch()

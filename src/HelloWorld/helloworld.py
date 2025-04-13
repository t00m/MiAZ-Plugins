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

    def __init__(self):
        self.log = MiAZLog('Plugin.HelloWorld')
        self.app = None

    def do_activate(self):
        """Plugin activation"""

        # Get app pointer
        self.app = self.object.app

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
        dialog = srvdlg.create(enable_response=False, dtype=dtype, title=title, body=body, widget=None)
        dialog.present(window)

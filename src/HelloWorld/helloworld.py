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
        self.app = self.object.app
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        print("Deactivation not implemented. Restart app to disable plugins.")

    def startup(self, *args):
        test = PluginTest(self.app)
        test.hello()

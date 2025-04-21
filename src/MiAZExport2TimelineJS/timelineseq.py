#!/usr/bin/python3

"""
# File: timelineseq.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Example of MiAZuser plugin
"""

import os
import html
import tempfile

from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.log import MiAZLog

TPL_MERMAID="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid.js Sequence Diagram</title>
    <!-- Include Mermaid.js library -->
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true });
    </script>
</head>
<body>
    <!-- Mermaid.js sequence diagram -->
    <div class="mermaid">
        sequenceDiagram
            %s
    </div>
</body>
</html>"""

class MiAZExamplePlugin(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZTimelineSeqPlugin'
    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        self.log = MiAZLog('Plugin.TimelineSeq')

    def do_activate(self):
        self.app = self.object.app
        self.srvutl = self.app.get_service('util')
        self.srvpmg = self.app.get_service('plugin-system')
        self.srvfty = self.app.get_service('factory')
        self.srvdlg = self.app.get_service('dialogs')
        self.app = self.object.app
        workspace = self.app.get_widget('workspace')
        workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        # Remove button
        pass
        # ~ toolbar = self.app.get_widget('headerbar-right-box')
        # ~ button = self.app.get_widget('toolbar-top-button-example')
        # ~ toolbar.remove(button)
        # ~ self.app.remove_widget('toolbar-top-button-example')

    def startup(self, *args):
        if self.app.get_widget('workspace-menu-export-timelinejs') is None:
            factory = self.app.get_service('factory')

            # Create menu item for plugin
            menuitem = factory.create_menuitem('export-to-seq', _('...create timeline sequence'), self.export, None, [])
            self.app.add_widget('workspace-menu-export-timelinejs', menuitem)

            # Add plugin to its default (sub)category
            category = self.app.get_widget('workspace-menu-plugins-visualisation-and-diagrams-data-visualisation')
            category.append_item(menuitem)

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
            text += f"\t\t\t{item.sentby_dsc}->>{item.sentto_dsc}: {item.title}\n"
        html = TPL_MERMAID % text.strip()
        fp, filepath = tempfile.mkstemp(dir=ENV['LPATH']['TMP'], suffix='.html')
        with open(filepath, 'w') as temp:
            temp.write(html)
        temp.close()
        stack = self.app.get_widget('stack')
        webbrowser = self.app.get_widget('webbrowser')
        webbrowser.load_file(filepath)
        stack.set_visible_child_name('page-webbrowser')

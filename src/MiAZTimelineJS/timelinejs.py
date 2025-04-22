#!/usr/bin/python3

"""
# File: timelineseq.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Example of MiAZuser plugin
"""

import os
import html
import shutil
import tempfile

from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.log import MiAZLog


class MiAZTimelineJSPlugin(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZTimelineJSPlugin'
    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        self.log = MiAZLog('Plugin.MiAZTimelineJS')

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
        pass

    def startup(self, *args):
        if self.app.get_widget('workspace-menu-export-timelinejs') is None:
            factory = self.app.get_service('factory')

            # Create menu item for plugin
            menuitem = factory.create_menuitem('export-to-timelinejs', _('...create timeline sequence'), self.export, None, [])
            self.app.add_widget('workspace-menu-export-timelinejs', menuitem)

            # Add plugin to its default (sub)category
            category = self.app.get_widget('workspace-menu-plugins-visualisation-and-diagrams-data-visualisation')
            category.append_item(menuitem)

    def export(self, *args):
        actions = self.app.get_service('actions')
        srvdlg = self.app.get_service('dialogs')
        util = self.app.get_service('util')
        ENV = self.app.get_env()
        util = self.app.get_service('util')
        workspace = self.app.get_widget('workspace')
        window = workspace.get_root()
        items = workspace.get_selected_items()
        if actions.stop_if_no_items(items):
            return

        # Generate timeline data
        timelinejs_data = {}
        timelinejs_data['events'] = []
        for item in items:
            category = item.group_dsc
            title = item.title
            timestamp = item.date
            url = item.title
            human_date = util.filename_date_human(timestamp)
            dt = util.string_to_datetime(timestamp)
            event = {}
            text = f"<p>Saved in Category <b>{category}</b> on {human_date}</p><p>Access to <a href='{url}' target='_top'>document</a></p>"
            event['start_date'] = {}
            event['start_date']['year'] = str(dt.year)
            event['start_date']['month'] = str(dt.month)
            event['start_date']['day'] = str(dt.day)
            event['text'] = {}
            event['text']['headline'] = f"{item.purpose_dsc} ({item.subtitle}) sent by {item.sentby_dsc} to {item.sentto_dsc}"
            event['text']['text'] = text
            event['group'] = category
            timelinejs_data['events'].append(event)

        webserver = self.app.get_service('webserver')
        wdir = webserver.get_directory()

        # Resources: TimelineJS Library
        ## Source
        timelinejs_path_source = os.path.join(ENV['LPATH']['PLUGINS'], 'MiAZTimelineJS', 'js', 'timeline.js')
        ## Target (path)
        timelinejs_path_target = os.path.join(wdir, 'MiAZTimelineJS', 'js', 'timeline.js')
        self.log.debug(f"TimelineJS Source: {timelinejs_path_source}")
        self.log.debug(f"TimelineJS Target: {timelinejs_path_target}")
        os.makedirs(os.path.dirname(timelinejs_path_target), exist_ok=True)
        shutil.copy(timelinejs_path_source, timelinejs_path_target)
        ## Target (url)
        host = webserver.get_host()
        port = webserver.get_port()
        timelinejs_url = f"http://{host}:{port}/MiAZTimelineJS/js/timeline.js"

        # Resources: TimelineJS CSS
        ## Source
        timelinecss_path_source = os.path.join(ENV['LPATH']['PLUGINS'], 'MiAZTimelineJS', 'css', 'timeline.css')

        ## Target (path)
        timelinecss_path_target = os.path.join(wdir, 'MiAZTimelineJS', 'css', 'timeline.css')
        self.log.debug(f"TimelineJS CSS Source: {timelinecss_path_source}")
        self.log.debug(f"TimelineJS CSSTarget: {timelinecss_path_target}")
        os.makedirs(os.path.dirname(timelinecss_path_target), exist_ok=True)
        shutil.rmtree(os.path.dirname(timelinecss_path_target))
        shutil.copytree(os.path.dirname(timelinecss_path_source), os.path.dirname(timelinecss_path_target))
        ## Target (url)
        timelinecss_url = f"http://{host}:{port}/MiAZTimelineJS/css/timeline.css"

        # Resources: JSON Data for TimelineJS
        timelinejsdata_path = os.path.join(wdir, 'MiAZTimelineJS', 'timelinejs.json')
        util.json_save(timelinejsdata_path, timelinejs_data)
        timelinejsdata_url = f"http://{host}:{port}/MiAZTimelineJS/timelinejs.json"


        # Resources: TimelineJS webpage
        ## Source
        TPL_TIMELINE=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timeline</title>
    <link rel="stylesheet" href="{timelinecss_url}" />
</head>
<body>
<div id="timeline-embed" style="width: 100%; height: 600px;"></div>

<script src="{timelinejs_url}"></script>
<script>
    var options = {{
            start_at_end: true,
            zoom_sequence: [0.5, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
            initial_zoom: 10,
            scale_factor: 1
        }}
    var timeline = new TL.Timeline('timeline-embed', "{timelinejsdata_url}", options);
</script>
</body>
</html>"""

        timelinejs_page = os.path.join(ENV['LPATH']['HTML'], 'MiAZTimelineJS', 'timeline.html')
        with open(timelinejs_page, 'w') as fhtml:
            fhtml.write(TPL_TIMELINE)

        url = f"http://{host}:{port}/MiAZTimelineJS/timeline.html"
        stack = self.app.get_widget('stack')
        webbrowser = self.app.get_widget('webbrowser')
        self.log.debug(f"Loading {url}")
        webbrowser.load_url(url)
        stack.set_visible_child_name('page-webbrowser')

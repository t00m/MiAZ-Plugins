#!/usr/bin/python3

class PluginTest:
    def __init__(self, app):
        self.app = app
        workspace = self.app.get_widget('workspace')
        srvdlg = self.app.get_service('dialogs')
        body = ''
        window = workspace.get_root()
        srvdlg.create(enable_response=False, dtype='info', title="Hello World", body=body).present(window)

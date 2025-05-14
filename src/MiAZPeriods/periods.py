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
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Peas

from MiAZ.backend.log import MiAZLog
from MiAZ.backend.models import MiAZModel
from MiAZ.backend.config import MiAZConfig
from MiAZ.frontend.desktop.widgets.configview import MiAZConfigView
from MiAZ.frontend.desktop.widgets.columnview import MiAZColumnViewSelector
from MiAZ.frontend.desktop.services.pluginsystem import MiAZPlugin


class Periodicity(MiAZModel):
    __gtype_name__ = 'Periodicity'
    __title__ = _('Periodicity')
    __title_plural__ = _('Periods')
    __config_name__ = 'periodicity'
    __config_name_available__ = 'periodicity'
    __config_name_used__ = 'periodicity'


class MiAZConfigPeriodicity(MiAZConfig):
    def __init__(self, app, plugin):
        self.plugin = plugin
        config_dir = self.plugin.get_config_dir()
        config_file_setup = self.plugin.get_config_file_setup()
        ENV = app.get_env()
        super().__init__(
            app=app,
            log=MiAZLog('MiAZ.Config.Periods'),
            config_for='periodicity',
            used=os.path.join(config_dir, 'periodicity-used.json'),
            available=os.path.join(config_dir, 'periodicity-available.json'),
            default=config_file_setup,
            model=Periodicity,
            must_copy=False
        )


class MiAZColumnViewPeriodicity(MiAZColumnViewSelector):
    """ Custom ColumnView widget for MiAZ """
    __gtype_name__ = 'MiAZColumnViewPeriodicity'

    def __init__(self, app, available=True):
        item_type=Periodicity
        super().__init__(app, item_type)
        self.cv.append_column(self.column_id)
        self.column_id.set_visible(False)
        self.column_title.set_title(_('Period Id'))
        self.cv.append_column(self.column_title)
        if available:
            title = _(f"{item_type.__title_plural__} available")
        else:
            title = _(f"{item_type.__title_plural__} enabled")
        self.column_title.set_title(title)

periodicity = {
                '1D': 'Daily',
                '1W': 'Weekly',
                '1M': 'Monthly',
                '1Y': 'Yearly'
            }

class MiAZPeriodicityView(MiAZConfigView):
    """Manage purposes from Repo Settings"""
    __gtype_name__ = 'MiAZPeriodicityView'

    def __init__(self, app, plugin, config):
        self.plugin = plugin
        self.config = config
        self.log = self.plugin.log
        self.config_dir = self.plugin.get_config_dir()
        self.data_dir = self.plugin.get_data_dir()
        self.data_file = self.plugin.get_data_file()
        if self.config_dir is None:
            raise
        super(MiAZConfigView, self).__init__(app, edit=True)
        super().__init__(app, config_name='Periodicity', custom_config=config)

    def _setup_view_finish(self):
        # Setup Available and Used Columns Views
        self.viewAv = MiAZColumnViewPeriodicity(self.app)
        self._add_columnview_available(self.viewAv)
        self.viewSl = MiAZColumnViewPeriodicity(self.app, available=False)
        self._add_columnview_used(self.viewSl)
        self._add_config_menubutton(self.config.config_for)
        self.update_views()


class MiAZPeriodsPlugin(GObject.GObject, Peas.Activatable):
    __gtype_name__ = 'MiAZPeriods'
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

        ## Get services
        self.actions = self.app.get_service('actions')
        self.factory = self.app.get_service('factory')
        self.srvdlg = self.app.get_service('dialogs')
        self.util = self.app.get_service('util')

        # Connect signals to startup
        self.workspace = self.app.get_widget('workspace')
        self.workspace.connect('workspace-loaded', self.startup)

    def do_deactivate(self):
        self.log.warning("Deactivation not implemented")

    def startup(self, *args):
        if not self.plugin.menu_item_loaded():
            # Get submenu for this plugin (subcategory)
            submenu = self.plugin.install_menu_entry()

            # Install periodicity submenu
            periodicity_menu = Gio.Menu()
            menuitem = self.factory.create_menuitem('period-add', _('... set periodicity'), self._set_periodicity, None, [])
            periodicity_menu.append_item(menuitem)
            menuitem = self.factory.create_menuitem('period-del', _('... unset periodicity'), self._unset_periodicity, None, [])
            periodicity_menu.append_item(menuitem)
            submenu.append_submenu("Periodicity", periodicity_menu)

            # Get config
            self.config = MiAZConfigPeriodicity(self.app, self.plugin)

            ## Set factory data
            data_file = self.plugin.get_config_file_setup()
            self.util.json_save(data_file, periodicity)

            # Periodicity dropdown for custom filters
            # ~ config = MiAZConfigPeriodicity(self.app, self.plugin)
            dd_period = self.factory.create_dropdown_generic(item_type=Periodicity, ellipsize=False, enable_search=True)
            self.config.connect('used-updated', self.actions.dropdown_populate, dd_period, Periodicity, False, False)
            # ~ self.config.connect('used-updated', self._on_config_used_updated, dd_period, Periodicity, False, False)
            self.actions.dropdown_populate(self.config, dd_period, Periodicity, any_value=True)
            dd_period.set_hexpand(True)
            boxDropdown = self.factory.create_box_filter('Period', dd_period)
            row = self.app.get_widget('sidebar-box-custom-filters')
            row.append(boxDropdown)

    def _set_periodicity(self, *args):
        selected_items = self.workspace.get_selected_items()
        if len(selected_items) > 0:
            dd_periods = self.factory.create_dropdown_generic(item_type=Periodicity, ellipsize=False, enable_search=False)
            self.actions.dropdown_populate(self.config, dd_periods, Periodicity, any_value=True)
            dialog = self.srvdlg.show_action(title='Manage periodicity', widget=dd_periods)
            dialog.connect('response', self._on_set_periodicity_response, dd_periods)
            dialog.present(self.workspace.get_root())
        else:
            parent = self.app.get_widget('window')
            self.srvdlg.show_error(title=_('Action ignored'), body=_('<big>You must select at least one document</big>'), parent=parent)

    def _on_set_periodicity_response(self, dialog, response, dropdown):
        datafile = self.plugin.get_data_file()
        try:
            data = self.util.json_load(filepath=datafile)
        except FileNotFoundError:
            self.log.debug(f"Creating new data file in {datafile}")
            data = {}
            data['documents'] = {}
            data['periods'] = {}
            self.util.json_save(filepath=datafile, adict=data)

        # ~ # Check dictionaries
        # ~ try:
            # ~ documents = data['documents']
        # ~ except KeyError:
            # ~ documents = {}
            # ~ data['documents'] = documents

        # ~ try:
            # ~ periods = data['periods']
        # ~ except KeyError:
            # ~ periods = []
            # ~ data['periods'] = periods

        documents = data['documents']
        periods = data['periods']
        period = dropdown.get_selected_item()
        pid = period.id
        for document in self.workspace.get_selected_items():
            docid = document.id
            documents[docid] = pid
            if pid in periods:
                s = set(periods[pid])
                s.add(docid)
                periods[pid] = list(s)
            else:
                periods[pid] = [docid]
        data['documents'] = documents
        data['periods'] = periods
        self.util.json_save(datafile, data)

    def _unset_periodicity(self, *args):
        for document in self.workspace.get_selected_items():
            # do something
            pass

        self.log.debug("Plugin Periods activated")

    def show_settings(self, widget):
        self.log.error(self.config.config_for)
        config_dir = self.plugin.get_config_dir()
        configview = MiAZPeriodicityView(self.app, plugin=self.plugin, config=self.config)
        dialog = self.srvdlg.show_noop(title='Manage periodicity', widget=configview, width=800, height=600)
        dialog.present(widget.get_root())

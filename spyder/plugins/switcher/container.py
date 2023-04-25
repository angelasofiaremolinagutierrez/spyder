# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Switcher Main Container."""

# Standard library imports
import subprocess
import os

# Third-party imports
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

# Spyder imports
from spyder.api.translations import _
from spyder.api.widgets.main_container import PluginMainContainer
from spyder.plugins.switcher.widgets.switcher import Switcher


class SwitcherContainer(PluginMainContainer):

    # --- PluginMainContainer API
    # ------------------------------------------------------------------------
    def setup(self):
        self.switcher = Switcher(self._plugin.get_main())

        # Switcher shortcuts
        self.create_action(
            'file switcher',
            _('File switcher...'),
            icon=self._plugin.get_icon(),
            tip=_('Fast switch between files'),
            triggered=self.open_switcher,
            register_shortcut=True,
            context=Qt.ApplicationShortcut
        )

        self.create_action(
            'symbol finder',
            _('Symbol finder...'),
            icon=self.create_icon('symbol_find'),
            tip=_('Fast symbol search in file'),
            triggered=self.open_symbolfinder,
            register_shortcut=True,
            context=Qt.ApplicationShortcut
        )

    def update_actions(self):
        pass

    # --- Public API
    # ------------------------------------------------------------------------
    def open_switcher(self, symbol=False):
        """Open switcher dialog."""
        switcher = self.switcher
        if switcher is not None and switcher.isVisible():
            switcher.clear()
            switcher.hide()
            return

        if symbol:
            switcher.set_search_text('@')
        else:
            switcher.set_search_text('')
            switcher.setup()

        # Set position
        mainwindow = self._plugin.get_main()

        # Note: The +8 pixel on the top makes it look better
        default_top = (mainwindow.toolbar.toolbars_menu.geometry().height() +
                       mainwindow.menuBar().geometry().height() + 8)

        current_window = QApplication.activeWindow()
        if current_window == mainwindow:
            if self.get_conf('toolbars_visible', section='toolbar'):
                delta_top = default_top
            else:
                delta_top = mainwindow.menuBar().geometry().height() + 8
        else:
            delta_top = default_top

        switcher.set_position(delta_top, current_window)
        switcher.show()

    def open_symbolfinder(self):
        """Open symbol list management dialog box."""
        self.open_switcher(symbol=True)

    def get_all_files_in_project(self, project_path):
        return self._execute_fzf_subprocess(project_path)

    # def get_search_results_list(self, search_text):
    #     return self._execute_fzf_subprocess(search_text=search_text)

    def is_projects_enabled(self):
        return self.get_conf('enable', section='project_explorer')

    # --- Private API
    # ------------------------------------------------------------------------
    def _execute_fzf_subprocess(self, project_path, search_text=""):
        # command = fzf --filter <search_str>
        cmd_list = ["fzf", "--filter", search_text]
        shell = False
        env = os.environ.copy()
        startupinfo = subprocess.STARTUPINFO()
        try:
            out = subprocess.check_output(cmd_list, cwd=project_path,
                                          shell=shell, env=env,
                                          startupinfo=startupinfo,
                                          stderr=subprocess.STDOUT)
            relative_path_list = out.decode('UTF-8').strip().split("\n")
            # List of tuples with the absolute path
            result_list = [os.path.join(project_path, path)
                           for path in relative_path_list]
            # Limit the number of results to 500
            if (len(result_list) > 500):
                result_list = result_list[:500]
            return result_list
        except subprocess.CalledProcessError as e:
            print(e)
            return []

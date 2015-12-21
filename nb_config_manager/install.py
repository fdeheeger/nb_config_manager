#!/usr/bin/env python
# coding: utf-8

# Copyright (c) - Continuum Analytics

import argparse
import os
from os.path import exists, join
from pprint import pprint

from jupyter_core.paths import jupyter_config_dir

def install(enable=False, disable=False, prefix=None):
    """Install the nb_config_manager config piece.

    Parameters
    ----------
    enable: bool
        Enable the nb_config_manager on every notebook launch
    disable: bool
        Disable nb_config_manager on every notebook launch
    """
    from notebook.services.config import ConfigManager

    if enable:
        if prefix is not None:
            path = join(prefix, "etc", "jupyter")
            if not exists(path):
                print("Making directory", path)
                os.makedirs(path)
        else:
            path = jupyter_config_dir()

        cm = ConfigManager(config_dir=path)
        print("Enabling nb_config_manager in", cm.config_dir)
        cfg = cm.get("jupyter_notebook_config")
        print("Existing config...")
        pprint(cfg)

        notebook_app = (cfg.setdefault("NotebookApp", {}))
        if "config_manager_class" not in notebook_app:
            cfg["NotebookApp"]["config_manager_class"] = "nb_config_manager.EnvironmentConfigManager"

        cm.update("jupyter_notebook_config", cfg)
        print("New config...")
        pprint(cm.get("jupyter_notebook_config"))

    if disable:
        if prefix is not None:
            path = join(prefix, "etc", "jupyter")
        else:
            path = jupyter_config_dir()

        cm = ConfigManager(config_dir=path)
        print("Disabling nb_config_manager in", cm.config_dir)
        cfg = cm.get("jupyter_notebook_config")
        print("Existing config...")
        pprint(cfg)

        config_manager = cfg["NotebookApp"]["config_manager_class"]

        if "nb_config_manager.EnvironmentConfigManager" == config_manager:
            cfg["NotebookApp"].pop("config_manager_class")

        cm.set("jupyter_notebook_config", cfg)
        print("New config...")
        pprint(cm.get("jupyter_notebook_config"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Installs nbextension")
    parser.add_argument(
        "-e", "--enable",
        help="Automatically load nb_config_manager on notebook launch",
        action="store_true")
    parser.add_argument(
        "-d", "--disable",
        help="Remove nb_config_manager from config on notebook launch",
        action="store_true")
    parser.add_argument(
        "-p", "--prefix",
        help="prefix where to load nb_config_manager config",
        action="store")

    install(**parser.parse_args().__dict__)

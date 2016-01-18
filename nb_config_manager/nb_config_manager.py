# -*- coding: utf-8 -*-

from errno import EACCES
from os.path import exists, join

from notebook.services.config.manager import ConfigManager
from jupyter_core.paths import jupyter_config_dir, ENV_CONFIG_PATH

from traitlets import Bool


class EnvironmentConfigManager(ConfigManager):
    """Config Manager used for storing notebook frontend config

    But taking into account also the config from environments.
    """

    disable_user_config = Bool(False,
                               config=True,
                               help="Do not capture info from the user config")

    user_config_dir = join(jupyter_config_dir(), 'nbconfig')
    environment_config_dir = join(ENV_CONFIG_PATH[0], 'nbconfig')
    default_config_dir = environment_config_dir

    def __init__(self, **kwargs):
        super(EnvironmentConfigManager, self).__init__(**kwargs)
        self._update_env_config()

    def _update_sections(self, section_name):
        """Get info from each section in the user space and port it to the
        environment config file.
        """
        # point the ConfigManager to the user config_dir and save the info
        self.config_dir = self.user_config_dir
        cfg_user = self.get(section_name)
        if "load_extensions" in cfg_user:
            user_extensions = cfg_user["load_extensions"]
        else:
            user_extensions = None

        # point the ConfigManager to the environment config_dir
        self.config_dir = self.environment_config_dir
        cfg_environment = self.get(section_name)

        # load user info into the environment space
        if user_extensions is not None:
            if "load_extensions" in cfg_environment:
                cfg_environment["load_extensions"].update(user_extensions)
            else:
                cfg_environment["load_extensions"] = user_extensions

        try:
            # try to write updated environment config
            self.update(section_name, cfg_environment)
        except IOError as ex:
            if ex.errno == EACCES:
                # for example, if environment config dir is read-only.
                # write to user config location instead.
                cfg_user["load_extensions"] = cfg_environment.get("load_extensions")
                self.config_dir = self.user_config_dir
                self.update(section_name, cfg_user)

                # leave config dir pointing here after loading config
                self.default_config_dir = self.user_config_dir
            else:
                raise

    def _update_env_config(self):
        """Update the three section in the environment space with the user info"""
        if exists(self.environment_config_dir):  # otherwise defaults to user config
            if exists(self.user_config_dir) and not self.disable_user_config:
                # update the three sections
                self._update_sections("notebook")
                self._update_sections("tree")
                self._update_sections("editor")
        else:
            self.default_config_dir = self.user_config_dir

        self.config_dir = self.default_config_dir

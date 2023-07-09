"""
ConfigFunctions as taken from GitHub 07082023

"""

import configparser
from os import getcwd, mkdir
from os.path import isfile, join, isdir
from typing import List

default_config_filename = 'main_config.ini'
default_config_dir = '../cfg'
default_config_full_path = join(default_config_dir, default_config_filename).replace('\\', '/')


def get_config(config_location=None, config_list_dict=None):
    """
    get_config() either builds a .ini config file from a given list_dict
    (config_list_dict param) OR reads it from a given path (config_location).
    """
    # if a config location is given and the file exists, then read from it
    if config_location and isfile(config_location):
        c_config = _read_config(config_location)
    # if a config list dict AND a config location are given,
    # then write it to the given location, and read it back into a variable
    elif config_list_dict is not None and config_location is not None:
        config_loc = _write_config(config_list_dict, config_location=config_location)
        c_config = _read_config(config_loc)
    # if a config location is not given, but a config list dict IS,
    # then write it to the default location, and read it back into a variable
    elif config_location is None and config_list_dict is not None:
        config_loc = _write_config(config_list_dict)
        c_config = _read_config(config_loc)
    else:
        raise AttributeError("_get_current_config requires either "
                             "a valid config location, "
                             "or a list_dict of configuration params")
    return c_config


def _write_config(config_list_dict: List[dict], config_location=default_config_full_path):
    def _file_io(location):
        with open(location, 'w') as f:
            config.write(f)
        print(f'Config written to {location}.')
        return location

    config_location.replace('\\', '/')
    config_parent_dir = '/'.join(config_location.split('/')[:-1])

    if isdir(config_parent_dir):
        pass
    else:
        mkdir(config_parent_dir)

    if not isfile(config_location):
        config = configparser.ConfigParser()
        try:
            config['DEFAULT'] = config_list_dict[0]['DEFAULT']
        except KeyError:
            raise KeyError("DEFAULT key must always be first in the config_list_dict")
        for i in config_list_dict:
            for key, value in i.items():
                if key != 'DEFAULT':
                    config[key] = value
        # then write the config to a file
        try:
            # since config location doesn't exist, use the default
            config_location = _file_io(config_location)
            return config_location
        except FileNotFoundError as e:
            print(f'{config_location} could not be found, '
                  f'writing to fallback at {getcwd()} with filename {config_location.split("/")[-1]}')
            config_location = _file_io(join(getcwd().replace('\\', '/'), config_location.split("/")[-1]))
            return config_location
    else:
        try:
            raise FileExistsError(f"config file \'{config_location}\' detected")
        except FileExistsError as e:
            print(e)
            return config_location


def _read_config(config_location):
    if isfile(config_location):
        config = configparser.ConfigParser()
        config.read(config_location)
    else:
        raise FileNotFoundError(f"Could not find config file in {config_location}")
    # print(f"returning config with sections {config.sections()}")
    return config
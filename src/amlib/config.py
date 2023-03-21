# read configuration from yaml file in (home) directory

import os
import yaml

import amlib

def read_from_file(path:str|None = None) -> dict:
    if not path:
        path = os.path.expanduser("~")
        config_file = os.path.join(path, ".pylerttool.yaml")
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        # print(f"No configuration file found, please create {config_file}")
        raise FileNotFoundError(f"No configuration file found, please create {config_file}")
        return {}

def set_config(config:dict) -> None:
    try:
        amlib.BASE_URL = config["URL"]["BASE_URL"]
        amlib.BASE_API_URL = amlib.BASE_URL + config["URL"]["API_PATH"]
        amlib.BASE_SILENCE_URL = amlib.BASE_URL + config["URL"]["HTTP_SILENCE_PATH"]
    except KeyError as ke:
        print(f"Invalid configuration File - KeyError: {ke}")
        exit(1)

    Auth = config.get("Authentication", None)
    if Auth:
        if Auth.get("Header", None):
            amlib.HEADERS.update(Auth["Header"])
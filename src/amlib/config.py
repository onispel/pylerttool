# read configuration from yaml file in (home) directory

import os,sys
import yaml
import amlib

STD_TIMEOUT = (10,20)

# BASE_URL = None
# BASE_API_URL = None
# BASE_SILENCE_URL = None
URLS = {}
HEADERS = {
    "Content-Type": "application/json",
}

def read_from_file(path:str|None = None) -> dict:
    if not path:
        path = os.path.expanduser("~")
        config_file = os.path.join(path, ".pylerttool.yaml")
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"No configuration file found, please create {config_file}")
        return {}

def set_config(config:dict) -> None:
    try:
        URLS["BASE_URL"] = config["URL"]["BASE_URL"]
        URLS["BASE_API_URL"] = URLS["BASE_URL"] + config["URL"]["API_PATH"]
        URLS["BASE_SILENCE_URL"] = URLS["BASE_URL"] + config["URL"]["HTTP_SILENCE_PATH"]
    except KeyError as ke:
        print(f"Invalid configuration File - KeyError: {ke}")
        exit(1)

    Auth = config.get("Authentication", None)
    if Auth:
        if Auth.get("Header", None):
            HEADERS.update(Auth["Header"])

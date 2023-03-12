# read configuration from yaml file in (home) directory

import os
import yaml

def read_config(path:str|None = None) -> dict:
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


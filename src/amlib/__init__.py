from . import config
from enum import Enum

# Connect and read timeout
STD_TIMEOUT=(10,20)

HEADERS = {
    "Content-Type": "application/json",
}

# Read configuration
try:
    conf = config.read_config()
except FileNotFoundError as fnf_ex:
    print(fnf_ex)
    exit(1)

try:
    BASE_URL = conf["URL"]["BASE_URL"]
    BASE_API_URL = BASE_URL + conf["URL"]["API_PATH"]
    BASE_SILENCE_URL = BASE_URL + conf["URL"]["HTTP_SILENCE_PATH"]
except KeyError as ke:
    print(f"Invalid configuration File - KeyError: {ke}")
    exit(1)

Auth = conf.get("Authentication", None)
if Auth:
    if Auth.get("Header", None):
        HEADERS.update(Auth["Header"])

class Paths(Enum):
    STATUS = 'status'
    ALERTS = 'alerts'
    SILENCES = 'silences'
    SILENCE = 'silence'


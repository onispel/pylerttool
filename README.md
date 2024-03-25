# pylerttool
Helpful Library and CLI for daily alertmanager tasks.

## Installation
Python 3.10+ is required.
### Pip from GitHub
```
pip install git+https://github.com/onispel/pylerttool.git
```
### pipenv from Github
```
pipenv install git+https://github.com/onispel/pylerttool.git#egg=pylerttool
```
### pip from local cloned repository
```
pip install --editable .
```
## Configuration
Configuration is done with the .amlib.yaml file in the users home directory.

Example (don't forget trailing slashes in URLs):
```
URL:
  BASE_URL: "https://YOUR.ALERTMANAGER.URL/"
  API_PATH: "api/v2/"
  HTTP_SILENCE_PATH: "#/silences/"
Authentication:
  Header:
    HEADER_KEY1: HEADER-VALUE1
    HEADER_KEY2: HEADER-VALUE2
    ...
```

### Authentication
At the moment only header-based authentication is supported. The headers specified in the configuration will be added to the API requests.
## amcli - Alertmanager CLI
### basic usage
```
> amcli --help
Usage: amcli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  alert    show and filter alerts
  silence  Commands for handling silences
  status   Cluster status commands
```
## Use PipEnv
1. [optional] create *.venv* - virtual environment directory
```
mkdir .venv
```
2. create virtual environment with PipEnv
```
pipenv update
```
For installation of dev-packages:
```
pipenv update --dev
```

## Useful URLs
- https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml
- https://app.swaggerhub.com/apis/megrez/alertmanager-api/0.0.1#/
- https://app.swaggerhub.com/apis/muryoutaisuu/alertmanager-api/2#/

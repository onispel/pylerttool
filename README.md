# pylerttool
Helpful Library and CLI for daily alertmanager tasks.

## Configuration
Configuration ist done with the .amlib.yaml file in the users home directory.

Example (not't forget trailing slashes):
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
""" Command line interface for alertmanager"""
import click
from amlib.config import read_from_file, set_config, URLS, HEADERS

from amlib.cligrp.status import status_grp
from amlib.cligrp.alert import alert_grp
from amlib.cligrp.silence import silence_grp


@click.group
def main_cli() -> None:
    pass

main_cli.add_command(status_grp)
main_cli.add_command(silence_grp)
main_cli.add_command(alert_grp)

conf = read_from_file()
set_config(conf)

if __name__ == '__main__':

    main_cli()

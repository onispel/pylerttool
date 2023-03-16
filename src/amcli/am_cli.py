""" Command line interface for alertmanager"""
import click

from .cligrp.status import status_grp
from .cligrp.alert import alert_grp
from .cligrp.silence import silence_grp


@click.group
def main_cli() -> None:
    pass

main_cli.add_command(status_grp)

main_cli.add_command(silence_grp)

main_cli.add_command(alert_grp)


if __name__ == '__main__':
    main_cli()

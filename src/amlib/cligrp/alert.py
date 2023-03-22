import click
import amlib.tools as tools
from . import echo_alert,echo_silence


@click.group(name='alert')
def alert_grp() -> None:
    """show and filter alerts"""
    pass


@click.command(name='filter')
@click.option('--fingerprint', type=str, default=None, help='fingerprint of alert')
@click.option('--active/--noactive', 'active', default=True,show_default="--active" ,help='allow/deny active alerts')
@click.option('--silenced/--nosilenced', 'silenced', default=True,show_default="--silenced" ,help='allow/deny silenced alerts')
@click.option('--inhibited/--noinhibited', 'inhibited', default=False,show_default="--noinhibited" ,help='allow/deny inhibited alerts')
@click.option('--unprocessed/--nounprocessed', 'unprocessed', default=False,show_default="--nounprocessed", help='allow/deny unprocessed alerts')
@click.option('--receiver', type=str, help='alerts sent to a specific receiver')
@click.option('--find-silences', 'find_silences', is_flag=True, default=False)
@click.argument('label_filter', nargs=-1)
def alert_filter(fingerprint: str, active: bool = True, silenced: bool = True, inhibited: bool = True, unprocessed: bool = True, label_filter: list[str] | None = None, receiver: str | None = None, find_silences: bool = False) -> None:
    """ Find alerts by status, labelsm or receivers, --find-silences allows to filter for matching silences (evaluates regexes also) """
    if not label_filter:
        label_filter = []
    alerts = tools.get_alerts(
        active, silenced, inhibited, unprocessed, tuple(label_filter), receiver)
    if fingerprint:
        alerts = [alert for alert in alerts if alert.fingerprint == fingerprint]
    for alert in alerts:
        echo_alert(alert)
        if find_silences:
            silences = tools.get_silences()
            for silence in silences:
                if tools.is_matching_all(alert.labels, silence.matchers):
                    echo_silence(silence)
    if not alerts:
        click.echo('No alerts found.')
    else :
        click.echo(f'{len(alerts)} alerts found.')

alert_grp.add_command(alert_filter)

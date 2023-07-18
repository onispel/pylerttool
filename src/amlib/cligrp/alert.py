import click
import amlib.tools as tools
from datetime import timezone
from . import LOCAL_TZ
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
@click.option('--local/--utc', 'localtime', default=True, show_default='--local', help='UTC / local timezone')
@click.option('--find-silences', 'find_silences', is_flag=True, default=False)
@click.argument('label_filter', nargs=-1)
def alert_filter(fingerprint: str, active: bool, silenced: bool, inhibited: bool, unprocessed: bool, localtime: bool, label_filter: list[str] | None = None, receiver: str | None = None,find_silences: bool = False) -> None:
    """ Find alerts by status, labelsm or receivers, --find-silences allows to filter for matching silences (evaluates regexes also) """
    tz_info = LOCAL_TZ if localtime else timezone.utc
    if not label_filter:
        label_filter = []
    # get filtered alerts
    alerts = tools.get_alerts(
        active, silenced, inhibited, unprocessed, tuple(label_filter), receiver)
    # find alerts with matching fingerprint (if selected)
    if fingerprint:
        alerts = [alert for alert in alerts if alert.fingerprint == fingerprint]
    # print all alerts
    for alert in alerts:
        echo_alert(alert,tz_info)
        if find_silences:
            silences = tools.get_silences()
            silence_counter = 0
            for silence in silences:
                if tools.is_matching_all(alert.labels, silence.matchers):
                    echo_silence(silence,tz_info)
                    silence_counter += 1
            if not silence_counter:
                click.echo('No silences found')
            else:
                click.echo(f'{silence_counter} silence(s) found')
    if not alerts:
        click.echo('No alerts found.')
    else :
        click.echo(f'{len(alerts)} alerts found.')

alert_grp.add_command(alert_filter)

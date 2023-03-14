""" Command line interface for alertmanager"""

import getpass
import re
from datetime import date, datetime, time, timedelta, timezone, tzinfo

import click
import tabulate
from pytimeparse.timeparse import timeparse

from amlib import model, tools  #type: ignore

LOCAL_TZ = datetime.now().astimezone().tzinfo
DT_FORMATS = [
    '%Y-%m-%d',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%H:%M:%S',
    '%H:%M'
]

state_colors = {
    model.State.active: 'green',
    model.State.pending: 'yellow',
    model.State.expired: 'red'
}

def echo_status(status: model.AlertmanagerStatus, tzi: tzinfo | None = timezone.utc) -> None:
    """ Print representation of status """
    stat_tbl = []
    cluster_info = [['Name', status.cluster.name]]
    cluster_info.append(['Status',status.cluster.status.value])
    cluster_peers = [[peer.address, peer.name] for peer in status.cluster.peers]
    cluster_info.append(['Peers', tabulate.tabulate(cluster_peers, tablefmt='plain')])
    stat_tbl.append(['Cluster', tabulate.tabulate(cluster_info, tablefmt='plain')])
    stat_tbl.append(['Uptime', str(status.uptime.astimezone(tzi))])
    version_info = [['Version', status.versionInfo.version]]
    version_info.append(['Revision', status.versionInfo.revision])
    version_info.append(['Branch', status.versionInfo.branch])
    version_info.append(['BuildUser', status.versionInfo.buildUser])
    version_info.append(['BuildDate', status.versionInfo.buildDate])
    version_info.append(['GoVersion', status.versionInfo.goVersion])
    stat_tbl.append(['VersionInfo', tabulate.tabulate(version_info, tablefmt='plain')])
    click.echo(tabulate.tabulate(stat_tbl))

def echo_silence(silence: model.GettableSilence, tzi: tzinfo | None = timezone.utc) -> None:
    """ Print representation of silence """
    silence_tbl: list[list[str]] = []
    silence_tbl.append(['ID', click.style(silence.id, fg='yellow')])
    silence_tbl.append(['Starts at', str(silence.startsAt.astimezone(tzi))])
    silence_tbl.append(['Ends at', str(silence.endsAt.astimezone(tzi))])
    silence_tbl.append(['Updated at', str(silence.updatedAt.astimezone(tzi))])
    silence_tbl.append(['Created by', str(silence.createdBy)])
    silence_tbl.append(['Comment', silence.comment])
    silence_tbl.append(['State', click.style(silence.status.state.value,
               fg=state_colors[silence.status.state])])
    matchers = [(m.name, matcher_op_to_str(m), m.value)
                for m in silence.matchers.__root__]
    silence_tbl.append(['Matchers', tabulate.tabulate(matchers, tablefmt='plain')])
    silence_tbl.append(['SilenceURL', tools.silence_url(silence)])
    click.echo(tabulate.tabulate(silence_tbl))


def echo_alert(alert: model.GettableAlert, tzi: tzinfo = timezone.utc) -> None:
    """ Print representation of alert """
    alert_tbl = []
    alert_tbl.append(['fingerprint', click.style(alert.fingerprint, fg='yellow')])
    alert_tbl.append(['startsAt', str(alert.startsAt.astimezone(tzi))])
    alert_tbl.append(['endsAt', str(alert.endsAt.astimezone(tzi))])
    alert_tbl.append(['state', alert.status.state.value])
    # atb.append(['silencedBy',alert.status.state])
    receivers = [['', rec.name] for rec in alert.receivers]
    if len(receivers) > 0:
        receivers[0][0] = 'receivers'
        alert_tbl.extend(receivers)
    silencers = [['', sil] for sil in alert.status.silencedBy]
    if len(silencers) > 0:
        silencers[0][0] = "silencedBy"
        alert_tbl.extend(silencers)
    inhibitors = [['', inh] for inh in alert.status.inhibitedBy]
    if len(inhibitors) > 0:
        inhibitors[0][0] = "silencedBy"
        alert_tbl.extend(inhibitors)
    annotations = [[ann[0], '=', ann[1]] for ann in alert.annotations]
    if len(annotations) > 0:
        alert_tbl.append(['annotations', tabulate.tabulate(
            annotations, tablefmt='plain')])
    labels = [[label[0], '=', label[1]] for label in alert.labels]
    if len(labels) > 0:
        alert_tbl.append(['labels', tabulate.tabulate(labels, tablefmt='plain')])
    alert_tbl.append(['generatorURL', str(alert.generatorURL)])
    click.echo(tabulate.tabulate(alert_tbl))


def parse_matcher(expr: str) -> model.Matcher | None:
    """translates matcher-string into matcher-object"""
    matcher = None
    regex = r"(?P<key>\S+)(?P<op>!?=~?)(?P<val>.*)"
    match = re.match(regex, expr)
    if match:
        key, oper, val = match.groups()
        is_eq = False if oper[0] == "!" else True
        is_re = True if oper[-1] == "~" else False
        matcher = tools.match(key, val, is_re, is_eq)
    return matcher


def matcher_op_to_str(matcher: model.Matcher) -> str:
    """Helper function for creating Matcher objects from strings."""
    moper = "=" if matcher.isEqual else "!="
    moper += "~" if matcher.isRegex else ""
    return moper

@click.group(name="status")
def status_grp() -> None:
    """Cluster status commands"""
    pass

@click.command(name='show')
@click.option('--local/--utc', 'localtime', default=True, show_default='local', help='UTC / local timezone')
def status_show(localtime:bool) -> None:
    """ Show status of alertmanager """
    tz_info = LOCAL_TZ if localtime else timezone.utc
    status = tools.get_status()
    echo_status(status,tz_info)

@click.command(name='config')
def status_config() -> None:
    """ Show config of alertmanager """
    config = tools.get_status().config.original
    click.echo(config)

@click.group(name="silence")
def silence_grp() -> None:
    """Commands for handling silences"""

@click.command(name='filter')
@click.option('--active/--noactive', default=True, show_default='active')
@click.option('--pending/--nopending', default=True, show_default='pending')
@click.option('--expired/--noexpired', default=False, show_default='noexpired')
@click.option('--local/--utc', 'localtime', default=True, show_default='local', help='UTC / local timezone')
@click.argument('match_filter', nargs=-1)
def silence_filter(active: bool, pending: bool, expired: bool, localtime: bool, match_filter: list[str]) -> None:
    """ Filter silences by state or matchers """
    tz_info = LOCAL_TZ if localtime else timezone.utc
    statelist = []
    if active:
        statelist.append(model.State.active)
    if pending:
        statelist.append(model.State.pending)
    if expired:
        statelist.append(model.State.expired)
    silences = tools.get_silences(statelist, match_filter)
    for silence in silences:
        echo_silence(silence, tz_info)


@click.command(name='delete')
@click.argument('silence_id', nargs=-1)
def silence_delete(silence_id: str) -> None:
    """delete silences by id"""
    for sid in silence_id:
        okay = tools.expire_silence(sid)
        if okay:
            click.echo(f'SilenceID: {sid} ' +
                       click.style('*DELETED*', fg='green'))
        else:
            click.echo(f'SilenceID: {sid} ' + click.style('*ERROR*', fg='red'))


@click.command(name="expires")
@click.option('--local/--utc', 'localtime', default=True, show_default='local', help='UTC / local timezone')
@click.option('--before', '-b', type=click.DateTime(formats=DT_FORMATS), default=None, help='silence expires before given date/time (overrides "--within")')
@click.option('--within', '-w', type=str, default=None, help='silence expires within given timerange (i.e.: "2h30m")')
@click.option('--after', '-a', type=click.DateTime(formats=DT_FORMATS), default=None, help='silence expires after given date/time (overrides "--within")')
@click.option('--notwithin', '-n', type=str, default=None, help='silence expires AFTER given timerange (i.e.: "2h30m")')
def silence_expires(localtime: bool, before: datetime | None, after: datetime | None, within: str | None, notwithin: str | None) -> None:
    """Search for silences that will expire"""
    tz_info = LOCAL_TZ if localtime else timezone.utc

    if len([opt for opt in (before, after, within, notwithin) if opt is not None]) != 1:
        raise click.UsageError(
            "Exactly ONE option of --before, --after, --within, --notwithin has to be used.")

    silence_list = tools.get_silences([model.State.active, model.State.pending])

    expiry_date = None
    if within:
        within_secs = timeparse(within)
        if not within_secs:
            raise click.BadOptionUsage('--within','invalid time range format')
        expiry_date = datetime.now().astimezone(tz_info) + timedelta(seconds=within_secs)
    if before:
        if before.date() == date(1900, 1, 1):
            before = datetime.combine(datetime.now(tz_info).date(), time(
                before.hour, before.minute, before.second))
        expiry_date = before.astimezone(tz_info)
    if expiry_date:
        silence_list = [silence for silence in silence_list if silence.endsAt < expiry_date]

    if notwithin:
        notwithin_secs = timeparse(notwithin)
        if not notwithin_secs:
            raise click.BadOptionUsage('--notwithin','invalid time range format')
        expiry_date = datetime.now().astimezone(tz_info) + timedelta(seconds=notwithin_secs)
    if after:
        if after.date() == date(1900, 1, 1):
            after = datetime.combine(datetime.now(tz_info).date(), time(
                after.hour, after.minute, after.second))
        expiry_date = after.astimezone(tz_info)
    if any((notwithin,after)) and expiry_date:
        silence_list = [silence for silence in silence_list if silence.endsAt > expiry_date]

    if silence_list:
        for silence in silence_list:
            echo_silence(silence, tz_info)
        click.echo(f'Found {len(silence_list)} expiring silences')
    else:
        click.echo('No expiring silences found')
        exit(1)


@click.command(name="expired")
@click.option('--local/--utc', 'localtime', default=True, show_default='local', help='UTC / local timezone')
@click.option('--after', '-a', type=click.DateTime(formats=DT_FORMATS), default=None, help='silence expired after given date/time (overrides "--within")')
@click.option('--within', '-w', type=str, default=None, help='silence expires within given timerange (i.e.: "2h30m")')
def silence_expired(localtime: bool, after: datetime | None, within: str | None) -> None:
    """Search for expired silences"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    # expiry_date = None
    if after is None and within is None:
        raise click.UsageError('"--after or --within as to be specified')
    if within:
        within_secs = timeparse(within)
        expiry_date = datetime.now().astimezone(
            tz_info) - timedelta(seconds=within_secs)
    if after:
        if after.date() == date(1900, 1, 1):
            after = datetime.combine(datetime.now(tz_info).date(), time(
                after.hour, after.minute, after.second))
        expiry_date = after.astimezone(tz_info)
    silence_list = tools.get_silences([model.State.expired])
    if silence_list:
        silence_list = [
            silence for silence in silence_list if silence.endsAt > expiry_date]
        for silence in silence_list:
            echo_silence(silence, tz_info)
    else:
        exit(1)


@click.command(name='modify')
@click.option('--sid', type=str, required=True, help='Silence ID')
@click.option('--start', '-s', type=click.DateTime(formats=DT_FORMATS), default=None, help="startsAt")
@click.option('--duration', '-d', type=str, default=None, help='Duration -> endsAt (overrides --end)')
@click.option('--end', '-e', type=click.DateTime(formats=DT_FORMATS), default=None, help="endsAt")
@click.option('--creator', '-u', type=str, default=None, show_default='(current user)', help='Creator of silence')
@click.option('--comment', '-t', type=str, default=None, help='Comment on silence')
@click.option('--local/--utc', 'localtime', default=True, show_default='local', help='UTC / local timezone')
@click.option('--noop', is_flag=True, help="Do nothing - testing only.")
@click.argument('matcher', nargs=-1)
def silence_modify(sid: str, start: datetime, duration: str, end: datetime, creator: str, comment: str, matcher: list[str], noop, localtime) -> None:
    """modify existing silence"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    silence = tools.get_silence(sid)
    if silence:
        if start:
            if start.date() == date(1900, 1, 1):
                start = datetime.combine(datetime.now(tz_info).date(), time(
                    start.hour, start.minute, start.second))
            start = start.astimezone(tz_info)
            silence.startsAt = start
        if duration:
            duration_secs = timeparse(duration)
            end = silence.startsAt + timedelta(seconds=duration_secs)
        if end:
            if end.date() == date(1900, 1, 1):
                end = datetime.combine(start.date(), time(
                    end.hour, end.minute, end.second))
                if end <= start:
                    end = end + timedelta(days=1)
            end = end.astimezone(tz_info)
            silence.endsAt = end
        if creator:
            silence.createdBy = creator
        if comment:
            silence.comment = comment
        if matcher:
            matchers = []
            for single_match in matcher:
                matcher_obj = parse_matcher(single_match)
                if matcher_obj:
                    matchers.append(matcher_obj)
            silence.matchers = model.Matchers.parse_obj(matchers)
        if noop:
            echo_silence(silence)
        else:
            okay, res = tools.set_silence(silence)
            if okay:
                click.echo(f'Silence created: {res}')
            else:
                raise click.UsageError(str(res))
    else:
        click.echo('Silence not found', err=True)


@click.command(name='create')
@click.option('--start', '-s', type=click.DateTime(formats=DT_FORMATS), default=datetime.now(), help="startsAt")
@click.option('--duration', '-d', type=str, default=None, help='Duration -> endsAt (overrides --end)')
@click.option('--end', '-e', type=click.DateTime(formats=DT_FORMATS), default=None, help="endsAt")
@click.option('--creator', '-u', type=str, default=getpass.getuser(), show_default='(current user)', help='Creator of silence')
@click.option('--comment', '-t', type=str, required=True, help='Comment on silence')
@click.option('--local/--utc', 'localtime', default=True, show_default='local', help='UTC / local timezone')
@click.option('--noop', is_flag=True, help="Do nothing - just test.")
@click.argument('matcher', nargs=-1)
def silence_create(start: datetime, duration: str | None, end: datetime, creator: str, comment: str, matcher: list[str], noop, localtime) -> None:
    """create a new silence"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    if start.date() == date(1900, 1, 1):  # no date is set (just time)
        start = datetime.combine(date.today(), time(
            start.hour, start.minute, start.second))
    start = start.astimezone(tz_info)
    if duration is None and end is None:
        raise click.UsageError("Either --duration or --end ist required.")
    if duration is not None:
        duration_secs = timeparse(duration)
        end = start + timedelta(seconds=duration_secs)
    else:
        if end.date() == date(1900, 1, 1):  # no date is set (just time)
            end = datetime.combine(start.date(), time(
                end.hour, end.minute, end.second))
            end = end.astimezone(tz_info)
            if end <= start:
                end = end + timedelta(days=1)
    end = end.astimezone(tz_info)
    matchers = []
    for single_match in matcher:
        matcher_obj = parse_matcher(single_match)
        if matcher_obj:
            matchers.append(matcher_obj)
    silence = model.Silence(
        matchers=model.Matchers.parse_obj(matchers),
        startsAt=start, endsAt=end, createdBy=creator, comment=comment
    )
    if noop:
        click.echo(silence.json(indent=3))
    else:
        okay, res = tools.set_silence(silence)
        if okay:
            click.echo(f'Silence created: {res}')
        else:
            raise click.UsageError(str(res))


@click.command(name="show")
@click.option('--local/--utc', 'localtime', default=True, show_default='local', help='UTC / local timezone')
@click.argument('silence_id', type=str, nargs=-1)
def silence_show(localtime: bool, silence_id: str) -> None:
    """show all information of a given silence id"""
    tz_info = LOCAL_TZ if localtime else timezone.utc
    for s_id in silence_id:
        silence = tools.get_silence(s_id)
        if silence:
            silence.startsAt = silence.startsAt.astimezone(tz_info)
            silence.endsAt = silence.endsAt.astimezone(tz_info)
            silence.updatedAt = silence.updatedAt.astimezone(tz_info)
            echo_silence(silence, tz_info)


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
    alerts = tools.get_alerts(
        active, silenced, inhibited, unprocessed, label_filter, receiver)
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

@click.group
def main_cli() -> None:
    pass

status_grp.add_command(status_show)
status_grp.add_command(status_config)
main_cli.add_command(status_grp)

silence_grp.add_command(silence_filter)
silence_grp.add_command(silence_show)
silence_grp.add_command(silence_create)
silence_grp.add_command(silence_modify)
silence_grp.add_command(silence_delete)
silence_grp.add_command(silence_expires)
silence_grp.add_command(silence_expired)
main_cli.add_command(silence_grp)

alert_grp.add_command(alert_filter)
main_cli.add_command(alert_grp)


if __name__ == '__main__':
    main_cli()
